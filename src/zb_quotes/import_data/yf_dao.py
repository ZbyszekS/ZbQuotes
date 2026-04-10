from dataclasses import dataclass
import datetime as dt
from logging import getLogger
import pandas as pd
import yfinance as yf
from zb_quotes.dtos import VfiTimeSeriesDTO
from zb_quotes.import_data.report_import import ReportOfImport

# from zb_quotes.models import YfDownloadCondition, YfDownloadTimeWindowCondition


logger = getLogger(__name__)


YF_TF_NAME = {
    1: "1m",
    2: "1h",
    3: "1d",
    4: "1w",
    5: "1M"
}

TIME_FRAME_MAX_PERIOD_ALLOWED = [
    "1h",
    "1d",
    "1w",
    "1M"
]

@dataclass
class DownloadCond:
    interval:      str
    max_days_back: int
    max_days_in:   int


yf_download_limits = {'1d': DownloadCond('1d', 365*300, 365*300),
                      '1h': DownloadCond('1h',     730,     730),
                      '1m': DownloadCond('1m',      30,       7)}


@dataclass(frozen=True)
class YfDownloadTimeWindowCondition:
    period:      str | None             = None
    fetch_range: tuple[str, str] | None = None

@dataclass(frozen=True)
class YfDownloadCondition:
    interval:    str
    time_window: YfDownloadTimeWindowCondition

@dataclass#(frozen=True)
class YfDownloadPrompt:
    ticker:    str
    condition: YfDownloadCondition


class YfDao:

    def __init__(self):
        pass

    def _divide_date_ranges(self, 
                                yf_timeframe: str, 
                                start_date: dt.date = None,
                                end_date: dt.date = dt.date.today()
                                ) -> list[tuple[dt.date, dt.date]]:
        r = []
        max_days_back = yf_download_limits[yf_timeframe].max_days_back
        max_days_in = yf_download_limits[yf_timeframe].max_days_in
        min_start_date = end_date - dt.timedelta(days=max_days_back)
        start_date = max(start_date, min_start_date) if start_date else min_start_date
        if end_date < start_date:
            logger.warning(f"End date {end_date} is before start date {start_date}, using today as end date")
            end_date = dt.date.today()
        days_to_download = (end_date - start_date).days
        finished = False
        while not finished:
            r_start_date = start_date
            r_end_date = min(start_date + dt.timedelta(days=max_days_in), end_date)
            r.append((r_start_date, r_end_date))
            start_date = r_end_date
            if start_date >= end_date:
                finished = True
        return r

    def _create_download_conditions(self, vfi_ts: VfiTimeSeriesDTO) -> list[YfDownloadCondition]:
        """
        Create download conditions for a given VFI time series.
        There can be one or many ich there's a need to chunk download due to Yahoo Finance limitations.
        
        Args:
            vfi_ts: VFI time series data transfer object
            
        Returns:
            List of download conditions
        """
        r = []
        yf_timeframe = YF_TF_NAME[vfi_ts.timeframe_id]
        # first import of this financial instrument
        if vfi_ts.last_imported_to is None: 
            if yf_timeframe in TIME_FRAME_MAX_PERIOD_ALLOWED:    
                # there can be just max period
                r.append(
                    YfDownloadCondition(
                        interval=yf_timeframe,
                        time_window=YfDownloadTimeWindowCondition(
                            period=      "max",
                            fetch_range= None
                        )
                    )
                )
            elif yf_timeframe == "1m":         
                # max period has to be divided because of granularity limit
                date_ranges = self._divide_date_ranges(yf_timeframe)
                for date_range in date_ranges:
                    r.append(
                        YfDownloadCondition(
                            interval=yf_timeframe,
                            time_window=YfDownloadTimeWindowCondition(
                                period=None,
                                fetch_range=(date_range[0].strftime("%Y-%m-%d"), date_range[1].strftime("%Y-%m-%d"))
                            )
                        )
                    )
        # next import - continue from last imported date
        else:
            last_to_date = vfi_ts.last_imported_to
            date_ranges = self._divide_date_ranges(yf_timeframe, start_date=last_to_date)
            for date_range in date_ranges:
                r.append(
                    YfDownloadCondition(
                        interval=yf_timeframe,
                        time_window=YfDownloadTimeWindowCondition(
                            period=None,
                            fetch_range=(date_range[0].strftime("%Y-%m-%d"), date_range[1].strftime("%Y-%m-%d"))
                        )
                    )
                )
        return r

    def _get_download_prompts(self, vfi_ts: VfiTimeSeriesDTO) -> list[YfDownloadPrompt]:
        r = []
        conditions = self._create_download_conditions(vfi_ts)
        for condition in conditions:
            r.append(YfDownloadPrompt(
                ticker=vfi_ts.yf_ticker,
                condition=condition
            ))
        return r
    

    def _download_quotes(self, ticker_list: list[str], condition: YfDownloadCondition) -> pd.DataFrame:
        # if len(ticker_list) < -10:
        #     print(f"Warning: Too few tickers to download: {len(ticker_list)}")
        #     return pd.DataFrame()

        if condition.time_window.period is not None:
            # download for specified period param
            return yf.download(
                ticker_list, 
                interval=condition.interval, 

                period=condition.time_window.period,

                auto_adjust=False,
                actions=True
            )
        else:
            # download form start to end
            return yf.download(
                ticker_list, 
                interval=condition.interval,

                start=condition.time_window.fetch_range[0], 
                end  =condition.time_window.fetch_range[1], 

                auto_adjust=False,
                actions=True
            )


    def _parse_multi_ticker_fast(self, df, ticker_to_vfi):
        all_records = []

        for ticker, vfi_ts_id in ticker_to_vfi.items():
            # Select the ticker and drop rows where all price data is missing
            sub_df = df[ticker].dropna(how='all').reset_index()
            
            # Prepare the constant column
            sub_df["vfi_time_series_id"] = vfi_ts_id
            
            # Rename columns to match your database keys
            # yfinance columns are usually 'Date', 'Open', etc.
            # We convert to a list of dictionaries in one go
            chunk = sub_df.rename(columns={
                "Date": "timestamp",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            }).to_dict(orient="records")
            
            all_records.extend(chunk)

        return all_records
    
    def _parse_multi_ticker(self, df_many: pd.DataFrame, ticker_to_vfi: dict[str, int]) -> list[dict]:
        if isinstance(df_many.columns, pd.MultiIndex):
            df_many_swapped = df_many.swaplevel(axis=1).sort_index(axis=1)
        else:
            df_many_swapped = df_many
        records = []
        for ticker, vfi_ts_id in ticker_to_vfi.items():
            # 2. Now df[ticker] works for both single-item lists and multi-item lists
            try:
                sub_df = df_many_swapped[ticker].dropna(how='all').reset_index()
            except KeyError:
                print(f"Warning: Ticker {ticker} not found in download results")
                continue
            for _, row in sub_df.iterrows():
                # Note: yfinance sometimes uses 'Date' or 'Datetime' depending on interval
                date_col = "Date" if "Date" in row else "Datetime"
                
                records.append({
                    "vfi_time_series_id": vfi_ts_id,
                    "timestamp": row[date_col].to_pydatetime(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "adj_close": float(row["Adj Close"]) if "Adj Close" in row else None,
                    "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else None,
                })
        
        return records


    def _parse_multi_ticker_vectorized_universal_z( self,
        df: pd.DataFrame, 
        ticker_to_vfi_ts: dict[str, int]
    ) -> tuple[list[dict], list[dict], list[dict]]:
        """
        Parse yfinance download results into database-ready dictionaries.
        
        Args:
            df: DataFrame from yf.download() - no matter if single or multi-ticker
            ticker_to_vfi_ts: dictionary of ticker symbols to vfi_time_series.id values, 
                              which (ts) is expected to be in multiindex of df
            
        Returns:
            Tuple of (quote_records, dividend_records, split_records)
        """
        all_quotes = []
        all_dividends = []
        all_splits = []
        
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
        
        # --- PROCESS EACH TICKER ---
        for ticker, vfi_ts_id in ticker_to_vfi_ts.items():
            if ticker not in df.columns:
                print(f"Warning: Ticker '{ticker}' not found in DataFrame columns")
                continue
            
            sub_df = df[ticker].dropna(how='all').reset_index()
            
            if sub_df.empty:
                print(f"Warning: No data for ticker '{ticker}'")
                continue
            
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
            
            # --- EXTRACT QUOTES ---
            # create a clean subset for quotes only
            quote_cols_mapping = {
                "Open":      "open",
                "High":      "high",
                "Low":       "low",
                "Close":     "close",
                "Adj Close": "adj_close",
                "Volume":    "volume",
            }
            # create new df with proper columns from sub_df
            quote_df = sub_df[[db_date_col] + list(quote_cols_mapping.keys())].copy()
            quote_df = quote_df.rename(columns=quote_cols_mapping)
            # add a column of vfi_time_series_id at the beginning
            quote_df.insert(0, "vfi_time_series_id", vfi_ts_id)
            
            # Convert to records
            quote_records = quote_df.to_dict(orient="records")
            all_quotes.extend(quote_records)
            
            # --- EXTRACT DIVIDENDS ---
            # Teaching: Only create dividend records where amount > 0
            if "Dividends" in sub_df.columns:
                dividend_df = sub_df[[db_date_col, "Dividends"]].copy()
                dividend_df = dividend_df[dividend_df["Dividends"] > 0]  # Filter out zeros
                
                if not dividend_df.empty:
                    dividend_df = dividend_df.rename(columns={
                        db_date_col: "dividend_date",
                        "Dividends": "amount"
                    })
                    dividend_df["vfi_time_series_id"] = vfi_ts_id  # Temporary helper
                    
                    dividend_records = dividend_df.to_dict(orient="records")
                    all_dividends.extend(dividend_records)
            
            # --- EXTRACT SPLITS ---
            # Teaching: Splits are represented as ratios (e.g., 2.0 for 2-for-1 split)
            if "Stock Splits" in sub_df.columns:
                split_df = sub_df[[db_date_col, "Stock Splits"]].copy()
                split_df = split_df[split_df["Stock Splits"] > 0]  # Filter out zeros
                
                if not split_df.empty:
                    split_df = split_df.rename(columns={
                        db_date_col: "split_date",
                        "Stock Splits": "ratio"
                    })
                    split_df["vfi_time_series_id"] = vfi_ts_id  # Temporary helper
                    
                    split_records = split_df.to_dict(orient="records")
                    all_splits.extend(split_records)
        
        return all_quotes, all_dividends, all_splits        


    def _get_yf_prompts_for_vfi_ts(self, vfi_ts_to_import_all: list[VfiTimeSeriesDTO]) -> list[YfDownloadPrompt]:
        r = []
        for vfi_ts in vfi_ts_to_import_all:
            prompts = self._get_download_prompts(vfi_ts)
            r.extend(prompts)
        return r

    def _group_by_condition(self, prompts: list[YfDownloadPrompt]) -> dict[YfDownloadCondition, list[str]]:
        r = {}
        for prompt in prompts:
            if prompt.condition not in r:
                r[prompt.condition] = []
            r[prompt.condition].append(prompt.ticker)
        return r

    def _tickers_to_vfi(self, condition: YfDownloadCondition, tickers: list[str], all_tickers_to_vfi_ts_id: dict[str, int]) -> dict[str, int]:
        r = {}
        for ticker in tickers:
            r[ticker] = all_tickers_to_vfi_ts_id[ticker + "_" + condition.interval]
        return r

    def download_data_for_vfi_ts_list(self, vfi_tss_to_import: list[VfiTimeSeriesDTO] | tuple[VfiTimeSeriesDTO], report: ReportOfImport):
        q, d, s = [], [], []
        tickers_to_vfi_ts_id = {}
        for vfi_ts in vfi_tss_to_import:
            tickers_to_vfi_ts_id[vfi_ts.yf_ticker + "_" + YF_TF_NAME[vfi_ts.timeframe_id]] = vfi_ts.id
        
        yf_prompts: list[YfDownloadPrompt] = self._get_yf_prompts_for_vfi_ts(vfi_tss_to_import)
        yf_prompts_cond_2_tickers = self._group_by_condition(yf_prompts)
        
        # condition: YfDownloadCondition
        for condition, tickers in yf_prompts_cond_2_tickers.items():
            
            # main fetching expression:
            df = self._download_quotes(tickers, condition)

            if df.empty:
                logger.warning(f"Downloaded empty dataframe for condition: {condition}")
            else:
                tickers_2_vfi_id = self._tickers_to_vfi(condition, tickers, tickers_to_vfi_ts_id)
                quotes, dividends, splits = self._parse_multi_ticker_vectorized_universal_z(df, tickers_2_vfi_id)
                q.extend(quotes)
                d.extend(dividends)
                s.extend(splits)
                self._analyze_and_report(df, tickers, report)
        return q, d, s

    
    def _analyze_download_results(self, df: pd.DataFrame, ticker_list: list[str]) -> dict:
        results = {
            'successful': [],
            'no_data': [],
            'errors': []
        }
        
        if df.empty:
            # All tickers failed
            results['errors'] = ticker_list.copy()
            return results
        
        # Check which tickers are present in the DataFrame
        if isinstance(df.columns, pd.MultiIndex):
            available_tickers = df.columns.get_level_values(1).unique().tolist()
        else:
            # Single ticker case
            available_tickers = [ticker_list[0]] if len(ticker_list) == 1 else []
        
        # Categorize results
        for ticker in ticker_list:
            if ticker in available_tickers:
                # Check if ticker has actual data (not all NaN)
                if isinstance(df.columns, pd.MultiIndex):
                    ticker_data = df.xs(ticker, axis=1, level=1)
                else:
                    ticker_data = df
                if ticker_data.dropna(how='all').empty:
                    results['no_data'].append(ticker)
                else:
                    results['successful'].append(ticker)
            else:
                results['errors'].append(ticker)
        
        return results
        
    def _analyze_and_report(self, pd, ticker_list, report: ReportOfImport):
        results = self._analyze_download_results(pd, ticker_list)
        report.vfits.fetched += len(results['successful'])
        report.vfits.nonfetched += len(results['no_data']) + len(results['errors'])
        report.vfits.non_fetched_by_cause.no_new_data += len(results['no_data'])
        report.vfits.non_fetched_by_cause.error += len(results['errors'])
        report.vfits.fetch_error.extend(results['errors'])        
