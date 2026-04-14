import datetime as dt
from itertools import batched
from collections import defaultdict

import pandas as pd
from sqlalchemy import inspect
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session
import yfinance as yf

from zb_quotes.config import LOGGER, IMPORT_LOGGER
from zb_quotes.import_data.yf_data import YfDownloadCondition
from zb_quotes.database.db_session_provider import DBSessionProvider
from zb_quotes.mappers.base_mapper import BaseMapper
from zb_quotes.reference_data.sql_alchemy import SQL_ALCHEMY
from zb_quotes.reference_data.time_frame import TIME_FRAME
from zb_quotes.reference_data.yf import YF
from zb_quotes.services.services_provider import SERVICES_PROVIDER
from zb_quotes.dtos import VfiTimeSeriesDTO
from zb_quotes.models.models import Quote_1day, Split, Dividend, ModelType
from zb_quotes.import_data.report_import_2 import ImportReport



class QuoteImporter2:
    def __init__(self):
        self._tck_2_vfits_id          = {}
        self._vfits_id_2_gfi_cur__ids = {}
        self._report                  = ImportReport()

    # main function
    def import_quotes(self):
        self._report.start_time = dt.datetime.now()

        self._vfits_id_2_gfi_cur__ids = SERVICES_PROVIDER.get_gfiids_curids_4_vfitsids_enabled_only()
        import_params, tck_2_vfits_id = self._get_yfinance_import_params()
        for tf_id, cond2tickers in import_params.items():
            # for one timeframe -> one quote table
            tf_quotes, tf_divids, tf_splits = [], [], []
            for cond, ticker_list in cond2tickers.items():
                # for one condition -> get data for the list of tickers
                for batch_of_tickers in batched(ticker_list, YF.TICKERS_PER_DOWNLOAD.SAFE):
                    fs = dt.datetime.now()
                    yf_quotes = self._fetch_quotes(cond, batch_of_tickers)
                    fe = dt.datetime.now()
                    # parse yf data to quotes, splits, dividends filling proper vfits_id in place of ticker
                    qs, ds, ss = self._parse_multi_ticker_vectorized_universal_short(yf_quotes, tck_2_vfits_id, tf_id)
                    # accumulate for this timeframe
                    tf_quotes.extend(qs)
                    tf_divids.extend(ds)
                    tf_splits.extend(ss)
                    # update report
                    self._data_2_report_inside_loop(qs, ds, ss, tck_2_vfits_id, tf_id, cond, batch_of_tickers, fs, fe)
            # write to db for given time frame
            self._write_to_db(tf_quotes, tf_divids, tf_splits, tf_id, tck_2_vfits_id)

        self._report.end_time = dt.datetime.now()
        self._report.print_report(IMPORT_LOGGER)

    def _data_2_report_inside_loop(self, quotes, dividends, splits, tck_2_vfits_id, tf_id, cond, batch_of_tickers, fetch_start, fetch_end):
        self._report.add_quotes_count(len(quotes))
        self._report.add_dividends_count(len(dividends))
        self._report.add_splits_count(len(splits))
        self._report.tck_2_vfits_id_2_update = tck_2_vfits_id
        self._report.tf_processed.append(tf_id)
        self._report.process_dict[tf_id][cond].append(batch_of_tickers)
        self._report.fetch_times.append((fetch_start, fetch_end))

    def _write_to_db(self, quotes, dividends, splits, tf_id, tck_2_vfits_id):
        # vfits_dtos      = BaseMapper.models_2_dto_list(tck_2_vfits_id.values(), VfiTimeSeriesDTO)          # -> for writing metadata
        vfits_ids       = list(tck_2_vfits_id.values())
        quote_model_cls = TIME_FRAME.TO_QUOTE_MODEL[tf_id]       # -> for writing quotes
        with DBSessionProvider() as session:
            vfits_dtos = SERVICES_PROVIDER.get_vfits_dtos_4_list_of_ids(vfits_ids, session)                         # -> for writing metadata
            self._insert_quotes_idempotent(session, quote_model_cls, quotes)
            self._write_dividends_to_db(session, dividends)
            self._write_splits_to_db(session, splits)
            self._write_metadata_to_db(session, vfits_dtos)


    def _write_metadata_to_db(self, session, vfits_dtos: list[VfiTimeSeriesDTO]):
        for vfi_ts_dto in vfits_dtos:
            if vfi_ts_dto.last_imported_to is None:
                # it was the first import:
                model_cls = TIME_FRAME.TO_QUOTE_MODEL[vfi_ts_dto.timeframe_id]
                # it has to be done using current session to catch last updates done by flush
                last_imported_from = SERVICES_PROVIDER.get_first_quote_date_4_vfi_ts(vfi_ts_dto, model_cls, session)
            else:
                last_imported_from = vfi_ts_dto.last_imported_from
            
            last_imported_to = dt.date.today()
            last_imported_at = dt.datetime.now()

            vfi_ts_dto.last_imported_from = last_imported_from
            vfi_ts_dto.last_imported_to   = last_imported_to
            vfi_ts_dto.last_imported_at   = last_imported_at
            SERVICES_PROVIDER.upsert_vfi_ts_dto(session, vfi_ts_dto)



    def _insert_quotes_idempotent(self, session: Session, model_class: type[ModelType], records: list[dict]):
        if not records:
            return

        mapper = inspect(model_class)
        variables_per_record  = len(mapper.columns)
        max_records_per_batch = SQL_ALCHEMY.MAX_PARAMETERS_PER_INSERT // variables_per_record
        
        for batch_num, batch in enumerate(batched(records, max_records_per_batch), start=1):
            try:
                # Create insert statement
                stmt = sqlite_insert(model_class).values(batch)
                # If a row with the same vfi_time_series_id and timestamp exists, do nothing
                timestamp_col   = 'timestamp' if hasattr(model_class, 'timestamp') else 'q_date'
                do_nothing_stmt = stmt.on_conflict_do_nothing(
                    index_elements=['vfi_time_series_id', timestamp_col]
                )
                session.execute(do_nothing_stmt)
            except Exception as e:
                LOGGER.error(f"Error inserting quotes: {e}")
                raise


    def _write_dividends_to_db(self, session: Session, dividends: list[dict]):
        if not dividends:
            return

        # Transform all records first
        insert_dicts = [self._parse_yfdivdict_2_dbdivdict(d) for d in dividends]

        # Create the bulk insert statement
        stmt = sqlite_insert(Dividend).values(insert_dicts)

        # Tell SQLite: if gfi_id, date, and amount match, do nothing
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['gfi_id', 'dividend_date', 'amount']
        )

        session.execute(stmt)


    def _parse_yfdivdict_2_dbdivdict(self, dividend_dict):
        """ Changes vfits_id in given dict to gfi_id and currency_id
            IN:  (dividend_dict) - dict {vfi_time_series_id,  dividend_date, amount}
            OUT: (dividend_dict) - dict {gfi_id, currency_id, dividend_date, amount}
        """
        vfits_id = dividend_dict.get('vfi_time_series_id')
        gfi_id, currency_id = self._vfits_id_2_gfi_cur__ids.get(vfits_id)
        return {
            'gfi_id': gfi_id,
            'currency_id': currency_id,
            'dividend_date': dividend_dict.get('dividend_date'),
            'amount': dividend_dict.get('amount'),
        }



    def _write_splits_to_db(self, session: Session, splits: list[dict]):
        if not splits:
            return
        
        # Transform all records first
        insert_dicts = [self._parse_yfsplit_2_dbsplit(split) for split in splits]
        
        # Create the bulk insert statement
        stmt = sqlite_insert(Split).values(insert_dicts)

        # Tell SQLite: if gfi_id, date, and ratio match, do nothing
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['gfi_id', 'split_date', 'ratio']
        )

        session.execute(stmt)


    def _parse_yfsplit_2_dbsplit(self, split: dict):
        v_ts_id = split.get('vfi_time_series_id')
        gfi_id, _ = self._vfits_id_2_gfi_cur__ids.get(v_ts_id)
        return {
            'gfi_id': gfi_id,
            'split_date': split.get('split_date'),
            'ratio': split.get('ratio'),
        }




    def _fetch_quotes(self, cond: YfDownloadCondition, ticker_list: list[str])-> pd.DataFrame:
        """ Returns downloaded quotes from yfinance as pd.DataFrame
            pre: is_correct_condition(cond)
        
        """
        if not ticker_list:
            return pd.DataFrame()
        
        download_kwargs = {
            'tickers': ticker_list,
            'interval': cond.interval,
            'auto_adjust': cond.auto_adjust,
            'actions': cond.actions,
            'repair': cond.repair
        }

        if cond.period is not None:
            download_kwargs['period'] = cond.period
        elif cond.start is not None and cond.end is not None:
            download_kwargs['start'] = cond.start
            download_kwargs['end'] = cond.end
        
        return yf.download(**download_kwargs)
        

    def _get_yfinance_import_params(self) -> tuple[
                                               dict[int, dict[YfDownloadCondition, list[str]]], 
                                               dict[str, int]
                                            ]:
        """
            IN: 
                DB.vfi_time_series
            OUT:
                Returns:
                    tuple[
                        - dict[int, dict[YfDownloadCondition, list[str]]]: {timeframe_id: {condition: [ticker_list]}}
                        - dict[str, int]:                                  {ticker: vfi_time_series_id}
                    ]
        """
        conditions = defaultdict(lambda: defaultdict(list))
        t = {}
        vfi_tss_2_update: list[VfiTimeSeriesDTO] = SERVICES_PROVIDER.all_vfits_need_update()
        for vfi_ts in vfi_tss_2_update:
            t[vfi_ts.yf_ticker] = vfi_ts.id

            tfid = vfi_ts.timeframe_id
            cond_list = self._create_cond_from_vfits(vfi_ts)
            for cond in cond_list:
                conditions[tfid][cond].append(vfi_ts.yf_ticker)
        return conditions, t


    def _create_cond_from_vfits(self, vfi_ts: VfiTimeSeriesDTO):
        interval = YF.INTERVAL_NAME[vfi_ts.timeframe_id]
        if self._never_imported(vfi_ts) and  self._can_be_downloaded_once(vfi_ts):
            r = [YfDownloadCondition(
                    interval=interval, 
                    period=  YF.MAX_PERIOD_CODE
                )]
        else:
            end = dt.date.today()
            if self._never_imported(vfi_ts):
                beg = dt.date.today() - dt.timedelta(days=YF.MAX_DAYS_BACK[vfi_ts.timeframe_id])
            else:
                beg = vfi_ts.last_imported_to
            beg_end_list = self._chop_date_range(beg, end, YF.MAX_DAYS_IN[vfi_ts.timeframe_id])
            r = []
            for beg_end in beg_end_list:
                r.append(
                    YfDownloadCondition(
                        interval= interval,
                        start=    beg_end[0].strftime("%Y-%m-%d"),
                        end=      beg_end[1].strftime("%Y-%m-%d"),
                    ))
        return r


    def _can_be_downloaded_once(self, vfi_ts: VfiTimeSeriesDTO):
        return YF.MAX_DAYS_BACK[vfi_ts.timeframe_id] == YF.MAX_DAYS_IN[vfi_ts.timeframe_id]
        

    def _chop_date_range(self, beg, end, max_days_in) -> list[ tuple[dt.date, dt.date] ]:
        if max_days_in is None:
            return [(beg, end)]
        
        r = []
        finished = False
        while not finished:
            r_start_date = beg
            r_end_date = min(beg + dt.timedelta(days=max_days_in), end)
            r.append((r_start_date, r_end_date))
            beg = r_end_date
            if beg >= end:
                finished = True
        return r


    def _never_imported(self, vfi_ts: VfiTimeSeriesDTO):
        return vfi_ts.last_imported_to is None
    





    #############################################################
    #
    #   PARSING
    #
    #############################################################

    def _parse_multi_ticker_vectorized_universal_short( self,
        df:              pd.DataFrame, 
        ticker_2_vfi_ts: dict[str, int],
        tf_id:           int
    ) -> tuple[
            list[dict], 
            list[dict], 
            list[dict]
        ]:
        """ Transform downloaded yf data into quotes, splits, dividends dicts with proper vfits_id """
        all_quotes, all_divids, all_splits = [], [], []
        df = self._df_2_multiindex(df, ticker_2_vfi_ts)
        
        for ticker, vfits_id in ticker_2_vfi_ts.items():
            # for every ticker -> vfits_id
            sub_df = self._sub_df_4_ticker(df, ticker)
            if sub_df is not None and not sub_df.empty:
                # transform data for current ticker
                db_date_col, df_date_col = self._normalize_date_column(sub_df, ticker)
                qs = self._get_quotes_from_df(sub_df, vfits_id, db_date_col, df_date_col)
                all_quotes.extend(qs)
                # if it is a 1 day time frame fetch splits and dividends
                if tf_id == TIME_FRAME.ID._1d:
                    ss = self._df_events(sub_df, vfits_id, YF.DF_COLS.SPLIT,    db_date_col, Split.split_date.key,       Split.ratio.key)
                    ds = self._df_events(sub_df, vfits_id, YF.DF_COLS.DIVIDEND, db_date_col, Dividend.dividend_date.key, Dividend.amount.key)
                    all_splits.extend(ss)
                    all_divids.extend(ds)
        
        return all_quotes, all_divids, all_splits




    def _df_events(
        self, 
        sub_df: pd.DataFrame, 
        vfi_ts_id: int, 
        df_action_col: str,
        db_date_col: str, 
        date_col: str,
        value_col: str
    ):
        # --- EXTRACT ACTIONS ---
        r = []
        if df_action_col in sub_df.columns:
            event_df = sub_df[[db_date_col, df_action_col]].copy()
            event_df = event_df[event_df[df_action_col] > 0]  # Filter out zeros
            
            if not event_df.empty:
                event_df = event_df.rename(columns={
                    db_date_col: date_col,
                    df_action_col: value_col
                })
                event_df["vfi_time_series_id"] = vfi_ts_id
                r = event_df.to_dict(orient="records")
                
        return r


    def _get_quotes_from_df(self, sub_df: pd.DataFrame, vfits_id: int, db_date_col: str, df_date_col: str):
        # --- EXTRACT QUOTES ---
        # create a clean subset for quotes only
        quote_cols_mapping = {
            # different Quote models differs only on date attribute, so one can use any of them
            # for vfi_ts_id attrib the column will be inserted below
            df_date_col: db_date_col,
            "Open":      Quote_1day.open.key,
            "High":      Quote_1day.high.key,
            "Low":       Quote_1day.low.key,
            "Close":     Quote_1day.close.key,
            "Adj Close": Quote_1day.adj_close.key,
            "Volume":    Quote_1day.volume.key,
        }
        # create new df with columns from quote_cols_mapping
        # quote_df = sub_df[[db_date_col] + list(quote_cols_mapping.keys())].copy()
        quote_df = sub_df[list(quote_cols_mapping.keys())].copy()
        quote_df = quote_df.rename(columns=quote_cols_mapping)
        # add a column of vfi_time_series_id at the beginning
        quote_df.insert(0, "vfi_time_series_id", vfits_id)
        
        # Convert to records
        quote_records = quote_df.to_dict(orient="records")
        return quote_records


    def _normalize_date_column(self, sub_df: pd.DataFrame, ticker: str)-> tuple[str, str]:
        # --- DATE/TIMESTAMP HANDLING ---
        if "Date" in sub_df.columns:
            df_date_col = "Date"
            db_date_col = 'q_date'
        elif "Datetime" in sub_df.columns:
            df_date_col = "Datetime"
            db_date_col = 'timestamp'
        else:
            raise ValueError(
                f"Neither 'Date' nor 'Datetime' column found for ticker '{ticker}'. "
                f"Columns available: {sub_df.columns.tolist()}"
            )
        
        # pandas column(series) temp_date =...
        temp_date = pd.to_datetime(sub_df[df_date_col])
        # Convert and clean timezone
        if temp_date.dt.tz is not None:
            temp_date = temp_date.dt.tz_localize(None)
        
        # adding new column to sub_df with proper db_name and value without timezone
        if df_date_col == "Date":
            sub_df[db_date_col] = temp_date.dt.date
        else:
            sub_df[db_date_col] = temp_date

        return db_date_col, df_date_col

    def _df_2_multiindex(self, df: pd.DataFrame, ticker_to_vfi_ts: dict[str, int]):
        # --- UNIVERSAL ADAPTER ---
        if isinstance(df.columns, pd.MultiIndex):
            df = df.swaplevel(axis=1).sort_index(axis=1)
        else:
            if len(ticker_to_vfi_ts) != 1:
                raise ValueError(
                    f"Single-index DataFrame but {len(ticker_to_vfi_ts)} tickers provided. "
                    "This mismatch suggests data/mapping inconsistency."
                )
            # If it's a single ticker, create a MultiIndex artificially so the rest of the code can treat all cases uniformly.
            ticker_name = list(ticker_to_vfi_ts.keys())[0]
            df.columns = pd.MultiIndex.from_product([[ticker_name], df.columns])
        return df


    def _sub_df_4_ticker(self, df, ticker):
        if ticker not in df.columns:
            print(f"Warning: Ticker '{ticker}' not found in DataFrame columns")
            return None
        
        sub_df = df[ticker].dropna(how='all').reset_index()
        
        if sub_df.empty:
            print(f"Warning: No data for ticker '{ticker}'")
            return None
        
        return sub_df
