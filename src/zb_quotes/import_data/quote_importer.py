"""
Interface:
    import_all_quotes() - Main method to import all quotes
    

Quote Importer Module

This module provides functionality to import financial quote data from Yahoo Finance
into a local database. It handles downloading data in batches, processing it, and
storing it in the appropriate database tables.

"""
from itertools import batched
import datetime as dt
import time
from typing import TypeVar

from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session
from sqlalchemy.dialects import sqlite

from zb_quotes.import_data.report_import import ReportOfImport
from zb_quotes.models.models import Base
from zb_quotes.database.db_session_provider import DBSessionProvider
from zb_quotes.services.services_provider import SERVICES_PROVIDER
from zb_quotes.dtos import VfiTimeSeriesDTO
from zb_quotes.models import Quote_1day, Quote_1hour, Quote_1week, Quote_1month, Dividend, Split
from zb_quotes.import_data.yf_dao import YfDao
from zb_quotes.import_data.report_import import Counter4Tf
from config import IMPORT_LOGGER, LOGGER

ModelType = TypeVar("ModelType", bound=Base)

class QuoteImporter:
    "This class import quote data from internet to local db"
    def __init__(self) -> None:
        # self.db_session_provider = DBSessionProvider()
        self.vfits_batch_size = 20 # max about 100, safe probably 50
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
        self.report = ReportOfImport()
        self.MAX_PARAMETERS_PER_INSERT = 32_766 



    ###############################################################
    # INTERFACE
    ###############################################################

    def import_all_quotes(self):
        self.report.timing.beg_time = dt.datetime.now()
        IMPORT_LOGGER.info("Starting import of all quotes")
        vfi_tss_to_import = self._get_vfi_tss_to_import()
        self._report_input(vfi_tss_to_import, self.vfits_batch_size)
        for chunk in batched(vfi_tss_to_import, self.vfits_batch_size):
            quotes, dividends, splits = self.yf_dao.download_data_for_vfi_ts_list(chunk, self.report)
            self._report_fetch(chunk, quotes, dividends, splits)
            self._write_to_db(quotes, dividends, splits, chunk)
            time.sleep(self.pause_between_batches)
        self._report_end()



    ###############################################################
    # IMPLEMENTATION
    ###############################################################
    
    def _report_end(self):
        self.report.timing.end_time = dt.datetime.now()
        IMPORT_LOGGER.info("------------------------------------")
        IMPORT_LOGGER.info("Summary report of import")
        IMPORT_LOGGER.info("------------------------------------")
  
        IMPORT_LOGGER.info(f"Import started at: {self.report.timing.beg_time.strftime('%Y-%m-%d %H:%M:%S')}")
        IMPORT_LOGGER.info(f"Import end at    : {self.report.timing.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        IMPORT_LOGGER.info("------------------------------------")
        IMPORT_LOGGER.info(f"VfiTs to be imported: {self.report.vfits.on_input}")
        IMPORT_LOGGER.info(f"VfiTs to be imported by timeframe:")
        IMPORT_LOGGER.info(f" - 1m: {self.report.vfits.on_input_by_tf._1m}")
        IMPORT_LOGGER.info(f" - 1h: {self.report.vfits.on_input_by_tf._1h}")
        IMPORT_LOGGER.info(f" - 1d: {self.report.vfits.on_input_by_tf._1d}")
        IMPORT_LOGGER.info(f" - 1w: {self.report.vfits.on_input_by_tf._1w}")
        IMPORT_LOGGER.info(f" - 1M: {self.report.vfits.on_input_by_tf._1mo}")

        IMPORT_LOGGER.info(f"VfiTs fetched    : {self.report.vfits.fetched:3}")
        IMPORT_LOGGER.info(f"VfiTs not fetched: {self.report.vfits.nonfetched}")
        IMPORT_LOGGER.info(f"Error during fetching : {self.report.vfits.non_fetched_by_cause.error}")
        IMPORT_LOGGER.info(f"No new data fetch.... : {self.report.vfits.non_fetched_by_cause.no_new_data}")
        
        IMPORT_LOGGER.info(f"Quotes fetched....... : {self.report.quotes_nb}")
        IMPORT_LOGGER.info(f"Dividends fetched.... : {self.report.dividends_nb}")
        IMPORT_LOGGER.info(f"Splits fetched....... : {self.report.splits_nb}")
        IMPORT_LOGGER.info(f"Fetch errors..........: {self.report.vfits.fetch_error}")
        IMPORT_LOGGER.info(f"Chunk size............: {self.report.chunk_size}")
        IMPORT_LOGGER.info(f"Chunks number.........: {self.report.chunks_nb}")
        IMPORT_LOGGER.info("------------------------------------")

    def _report_input(self, vfi_tss_to_import, batch_size):
        self._report_import_input(vfi_tss_to_import)
        self._register_reporting_input_data(vfi_tss_to_import, batch_size)

    def _report_fetch(self, chunk, quotes, dividends, splits):
        self._report_download_results(chunk, quotes, dividends, splits)
        self._actualize_report_numbers(quotes, dividends, splits)

    def _actualize_report_numbers(self, quotes, dividends, splits):
        self.report.quotes_nb += len(quotes)
        self.report.dividends_nb += len(dividends)
        self.report.splits_nb += len(splits)





    
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




    def _get_vfi_tss_to_import(self) -> list[VfiTimeSeriesDTO]:
        vfi_tss_to_import: list[VfiTimeSeriesDTO]
        vfi_tss_to_import = SERVICES_PROVIDER.all_enabled_vfi_timeseries()
        vfi_tss_to_import = self._remove_already_imported_vfi_tss(vfi_tss_to_import)
        vfi_tss_to_import.sort(key=lambda x: x.timeframe_id)
        return vfi_tss_to_import
    
    def _register_reporting_input_data(self, vfi_tss_to_import: list[VfiTimeSeriesDTO], batch_size: int):
        self.report.vfits.on_input = len(vfi_tss_to_import)
        self.report.chunks_nb   = self.count_chunks_nb(len(vfi_tss_to_import), batch_size)
        self.report.chunk_size = batch_size
        # group by timeframe and register counts
        vfi_tss_by_tf = self.group_vts_by_timeframe(vfi_tss_to_import)
        self.report.vfits.on_input_by_tf = Counter4Tf(
            _1m=len(vfi_tss_by_tf.get(1, [])),
            _1h=len(vfi_tss_by_tf.get(2, [])),
            _1d=len(vfi_tss_by_tf.get(3, [])),
            _1w=len(vfi_tss_by_tf.get(4, [])),
            _1mo=len(vfi_tss_by_tf.get(5, []))
        )
        
    def count_chunks_nb(self, input_len: int, batch_size: int) -> int:
        return (input_len + batch_size - 1) // batch_size

    def _write_to_db(self, quotes, dividends, splits, chunk):
        with DBSessionProvider() as session:
            self._write_data_to_db(session, quotes, dividends, splits)
            self._write_metadata_to_db(session, chunk)
        IMPORT_LOGGER.info(f"- Written to database")

    def _report_download_results(self, chunk, quotes, dividends, splits):
        IMPORT_LOGGER.info(f"- Downloaded {len(quotes)} quotes, {len(dividends)} dividends, {len(splits)} splits for {len(chunk)} time series")
        # print(f"- Downloaded {len(quotes)} quotes, {len(dividends)} dividends, {len(splits)} splits for {len(chunk)} time series")

    def _report_import_input(self, vfi_tss_to_import):
        IMPORT_LOGGER.info(f"- Importing {len(vfi_tss_to_import)} time series")
        ifv_ts_names_to_be_imported = [obj.yf_ticker + "_" + self.timeframe_id_2_timeframe_code[obj.timeframe_id] for obj in vfi_tss_to_import]
        IMPORT_LOGGER.info(f"- Time series to be imported: {ifv_ts_names_to_be_imported[:10]}")

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
        model_cls_2_records = self._assign_qdicts_to_modelcls(quotes)
        for model_cls, records in model_cls_2_records.items():

            self._insert_quotes_idempotent(session, model_cls, records)



    def _insert_quotes_idempotent(self, session: Session, model_class: type[ModelType], records: list[dict]):
        if not records:
            return

        variables_per_record = 8 + 2 # nb of vars to write in every row of Quote table + 2 
        max_records_per_batch = self.MAX_PARAMETERS_PER_INSERT // variables_per_record  # max 999 variables per batch
        
        for batch_num, batch in enumerate(batched(records, max_records_per_batch), start=1):
            IMPORT_LOGGER.info(f"Inserting batch {batch_num} ({len(batch)} records)...")

            try:
                # Create the insert statement
                stmt            = insert(model_class).values(batch)
                
                # If a row with the same vfi_time_series_id and timestamp exists, do nothing
                timestamp_col   = 'timestamp' if hasattr(model_class, 'timestamp') else 'q_date'
                do_nothing_stmt = stmt.on_conflict_do_nothing(
                    index_elements=['vfi_time_series_id', timestamp_col]
                )
                session.execute(do_nothing_stmt)
            except Exception as e:
                IMPORT_LOGGER.error(f"Error inserting quotes: {e}")
                raise


    def _assign_qdicts_to_modelcls(self, quotes)-> dict[type[ModelType], list[dict]]:
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

    

    # def import_quotes(self, vfi_ts_dto: VfiTimeSeriesDTO):
    #     print(f"- Importing quotes for {vfi_ts_dto}")
    #     return True

    # def run(self):
    #     print('- Running quote importer')
    #     self.import_all_quotes()
