from itertools import batched
import datetime as dt
import time
from typing import TypeVar
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session
from zb_quotes.models.models import Base

# Define a type variable that MUST be a subclass of Base

from zb_quotes.database.db_session_provider import DBSessionProvider
from zb_quotes.services.services_provider import SERVICES_PROVIDER
from zb_quotes.dtos import VfiTimeSeriesDTO
from zb_quotes.models import Quote_1day, Quote_1hour, Quote_1week, Quote_1month, Dividend, Split
from zb_quotes.import_data.yf_dao import YfDao
from config import IMPORT_LOGGER

ModelType = TypeVar("ModelType", bound=Base)

class QuoteImporter:
    "This class import quote data from internet to local db"
    def __init__(self) -> None:
        # self.db_session_provider = DBSessionProvider()
        self.batch_size = 10
        self.pause_between_batches = 1.0
        self.yf_dao = YfDao()
        self.vfits_2_tfcode = SERVICES_PROVIDER.get_vfits_2_tfcode()
        self.tf_code_2_model_cls = {
            '1m': Quote_1day,
            '1h': Quote_1hour,
            '1d': Quote_1day,
            '1w': Quote_1week,
            '1M': Quote_1month,
        }
        self.vfits_2_gfi_cur_ids = SERVICES_PROVIDER.get_gfiids_curids_4_vfitsids()
        self.timeframe_id_2_timeframe_code = SERVICES_PROVIDER.get_vfi_timeframe_id_2_timeframe_code()

    
    
    def act_counters(self, success, c):
        if success: c[0] +=1
        else:       c[1] +=1


    def group_vts_by_timeframe(self, vfi_ts_to_import: list[VfiTimeSeriesDTO])-> dict[int, list[VfiTimeSeriesDTO]]:
        result = {}
        for vfi_ts in vfi_ts_to_import:
            tf = vfi_ts.timeframe_id
            if tf not in result:
                result[tf] = []
            result[tf].append(vfi_ts)
        return result

    




    # def get_vfi_ts_id_for_ticker_and_interval(self, ticker: str, interval: str) -> int:
    #     # This is a placeholder - you'll need to implement the actual logic
    #     # to find the VFI time series ID for a given ticker and interval
    #     pass

    #------------------------------------------------------------------------
    def import_all_quotes(self):
        IMPORT_LOGGER.info("Starting import of all quotes")
        vfi_tss_to_import: list[VfiTimeSeriesDTO]
        vfi_tss_to_import = SERVICES_PROVIDER.all_enabled_vfi_timeseries()
        vfi_tss_to_import = self._remove_already_imported_vfi_tss(vfi_tss_to_import)
        vfi_tss_to_import.sort(key=lambda x: x.timeframe_id)
        # divide list into chunks, because of memory and max nb of calls to outside api
        chunks = batched(vfi_tss_to_import, self.batch_size)
        self._report_import_input(vfi_tss_to_import, chunks)
        # IMPORT_LOGGER.info(f"Processing {len(vfi_tss_to_import)} time series in {len(chunks)} chunks")
        for chunk in chunks:
            quotes, dividends, splits = self.yf_dao.download_data_for_vfi_ts_list(chunk)
            self._report_download_results(chunk, quotes, dividends, splits)
            self.write_to_db(quotes, dividends, splits, chunk)
            time.sleep(self.pause_between_batches)

    def write_to_db(self, quotes, dividends, splits, chunk):
        with DBSessionProvider() as session:
            self._write_data_to_db(session, quotes, dividends, splits)
            self._write_metadata_to_db(session, chunk)
        IMPORT_LOGGER.info(f"- Written to database")

    def _report_download_results(self, chunk, quotes, dividends, splits):
        IMPORT_LOGGER.info(f"- Downloaded {len(quotes)} quotes, {len(dividends)} dividends, {len(splits)} splits for {len(chunk)} time series")
        # print(f"- Downloaded {len(quotes)} quotes, {len(dividends)} dividends, {len(splits)} splits for {len(chunk)} time series")

    def _report_import_input(self, vfi_tss_to_import, chunks):
        IMPORT_LOGGER.info(f"- Importing {len(vfi_tss_to_import)} time series")
        ifv_ts_names_to_be_imported = [obj.yf_ticker + "_" + self.timeframe_id_2_timeframe_code[obj.timeframe_id] for obj in vfi_tss_to_import]
        IMPORT_LOGGER.info(f"- Time series to be imported: {ifv_ts_names_to_be_imported}")

    def _remove_already_imported_vfi_tss(self, vfi_tss_to_import: list[VfiTimeSeriesDTO]):
        today = dt.date.today()
        return [obj for obj in vfi_tss_to_import 
                    if obj.last_imported_to != today]
                


    #         MAKE IT RIGHT!!! ##################################################################
    def _write_data_to_db(self, session, quotes, dividends, splits):
        IMPORT_LOGGER.info(f"- Writing {len(quotes)} quotes, {len(dividends)} dividends, {len(splits)} splits to db")
        if quotes:
            self._write_quotes_to_db(session, quotes)
        if dividends:
            self._write_dividends_to_db(session, dividends)
        if splits:
            self._write_splits_to_db(session, splits)
        

    def _write_metadata_to_db(self, session, vfi_ts_list: list[VfiTimeSeriesDTO]):
        for vfi_ts_dto in vfi_ts_list:
            if vfi_ts_dto.last_imported_to is None:
                # it was the first import:
                model_cls = self._model_cls_4_vfi_ts_id(vfi_ts_dto.id)
                # it has to be done using current session
                last_imported_from = SERVICES_PROVIDER.get_first_quote_date_for_vfi_ts(vfi_ts_dto, model_cls, session)
            else:
                last_imported_from = vfi_ts_dto.last_imported_from
            
            last_imported_to = dt.date.today()
            last_imported_at = dt.datetime.now()

            vfi_ts_dto.last_imported_from = last_imported_from
            vfi_ts_dto.last_imported_to   = last_imported_to
            vfi_ts_dto.last_imported_at   = last_imported_at
            SERVICES_PROVIDER.upsert_vfi_ts_dto(session, vfi_ts_dto)
            # write dto to db



    def _write_quotes_to_db(self, session, quotes):
        """ Writing list of dicts corresponding to appropriate QuoteModel to db
        Args:
            session: DB session
            quotes: list of dicts corresponding to appropriate QuoteModel
        """
        model_cls_2_records = self.assign_qdicts_to_modelcls(quotes)
        for model_cls, records in model_cls_2_records.items():
            self.insert_quotes_idempotent(session, model_cls, records)



    def insert_quotes_idempotent(self, session: Session, model_class: type[ModelType], records: list[dict]):
        if not records:
            return

        # Create the insert statement
        stmt = insert(model_class).values(records)
        
        # If a row with the same vfi_time_series_id and timestamp exists, do nothing
        timestamp_col = 'timestamp' if hasattr(model_class, 'timestamp') else 'q_date'
        do_nothing_stmt = stmt.on_conflict_do_nothing(
            index_elements=['vfi_time_series_id', timestamp_col]
        )
        
        session.execute(do_nothing_stmt)


    def assign_qdicts_to_modelcls(self, quotes)-> dict[type[ModelType], list[dict]]:
        r: dict[type[ModelType], list[dict]] = {}
        for quote in quotes:
            model_cls = self._model_cls_4_vfi_ts_id(quote.get('vfi_time_series_id'))
            if model_cls not in r:
                r[model_cls] = []
            r[model_cls].append(quote)
        return r
    
    def _model_cls_4_vfi_ts_id(self, vfi_ts_id: int) -> type[ModelType]:
        tf_code = self.vfits_2_tfcode.get(vfi_ts_id)
        return self.tf_code_2_model_cls.get(tf_code)
    
    # def _write_dividends_to_db(self, session, dividends):
    #     for dividend in dividends:
    #         insert_div = self._transform_dicrec_2_divdict(dividend)
    #         session.add(Dividend(**insert_div))
    
    def _write_dividends_to_db(self, session, dividends):
        if not dividends:
            return

        # Transform all records first
        insert_dicts = [self._transform_dicrec_2_divdict(d) for d in dividends]

        # Create the bulk insert statement
        stmt = insert(Dividend).values(insert_dicts)

        # Tell SQLite: if gfi_id, date, and amount match, do nothing
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['gfi_id', 'dividend_date', 'amount']
        )

        session.execute(stmt)


    def _transform_dicrec_2_divdict(self, dividend_yf_lodaer_rec):
        v_ts_id = dividend_yf_lodaer_rec.get('vfi_time_series_id')
        gfi_id, currency_id = self.vfits_2_gfi_cur_ids.get(v_ts_id)
        return {
            'gfi_id': gfi_id,
            'currency_id': currency_id,
            'dividend_date': dividend_yf_lodaer_rec.get('dividend_date'),
            'amount': dividend_yf_lodaer_rec.get('amount'),
        }



    def _write_splits_to_db(self, session, splits):
        # Transform all records first
        insert_dicts = [self._transform_dicrec_2_splitdict(split) for split in splits]
        
        # Create the bulk insert statement
        stmt = insert(Split).values(insert_dicts)

        # Tell SQLite: if gfi_id, date, and ratio match, do nothing
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['gfi_id', 'split_date', 'ratio']
        )

        session.execute(stmt)


    def _transform_dicrec_2_splitdict(self, split):
        v_ts_id = split.get('vfi_time_series_id')
        gfi_id, _ = self.vfits_2_gfi_cur_ids.get(v_ts_id)
        return {
            'gfi_id': gfi_id,
            'split_date': split.get('split_date'),
            'ratio': split.get('ratio'),
        }

    def _write_quotes_metadata_to_db(self, quotes):
        pass

    

    def import_quotes(self, vfi_ts_dto: VfiTimeSeriesDTO):
        print(f"- Importing quotes for {vfi_ts_dto}")
        return True

    def run(self):
        print('- Running quote importer')
        self.import_all_quotes()
