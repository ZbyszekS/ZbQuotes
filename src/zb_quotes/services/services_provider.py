from sqlalchemy import select, func
import datetime as dt
from zb_quotes.database.db_session_provider import DBSessionProvider
from zb_quotes.dao.dao_container import dao
from zb_quotes.dtos.vfi_time_serie_dto import VfiTimeSeriesDTO
from zb_quotes.mappers import BaseMapper
from zb_quotes.models.models import VfiTimeSeries, Timeframe, Vfi, Qfi

class ServicesProvider:
    def __init__(self):
        pass
    
    def all_vfits_enabled(self) -> list[VfiTimeSeriesDTO]:
        with DBSessionProvider() as session:
            r = dao.vfi_timeseries.get_all_enabled(session)
            return BaseMapper.models_2_dto_list(r, VfiTimeSeriesDTO)
    
    def all_vfits_need_update(self):
        with DBSessionProvider() as session:
            r = dao.vfi_timeseries.get_all_enabled_and_not_updated(session)
            return BaseMapper.models_2_dto_list(r, VfiTimeSeriesDTO)
    
    def get_vfits_2_tfcode(self):
        with DBSessionProvider() as session:
            stmt = select(VfiTimeSeries.id, Timeframe.code).join(Timeframe, VfiTimeSeries.timeframe_id == Timeframe.id)
            result = session.execute(stmt).all()
            return {row[0]: row[1] for row in result}
    

    def get_gfiids_curids_4_vfitsids(self):
        """Returns {vfi_ts_id: (gfi_id, currency_id)}"""
        with DBSessionProvider() as session:
            stmt = (
                select(VfiTimeSeries.id, Qfi.gfi_id, Qfi.currency_id)
                .join(Vfi, VfiTimeSeries.vfi_id == Vfi.id)
                .join(Qfi, Vfi.qfi_id == Qfi.id)
            )
            results = session.execute(stmt).all()
            return {row.id: (row.gfi_id, row.currency_id) for row in results}
    
    def get_gfiids_curids_4_vfitsids_enabled_only(self):
        """Returns {vfi_ts_id: (gfi_id, currency_id)} for enabled VfiTimeSeries only"""
        with DBSessionProvider() as session:
            stmt = (
                select(VfiTimeSeries.id, Qfi.gfi_id, Qfi.currency_id)
                .join(Vfi, VfiTimeSeries.vfi_id == Vfi.id)
                .join(Qfi, Vfi.qfi_id == Qfi.id)
                .where(VfiTimeSeries.enabled == True)
            )
            results = session.execute(stmt).all()
            return {row.id: (row.gfi_id, row.currency_id) for row in results}
    
    def get_vfits_dtos_enabled(self):
        with DBSessionProvider() as session:
            r = dao.vfi_timeseries.get_all_enabled(session)
            return BaseMapper.models_2_dto_list(r, VfiTimeSeriesDTO)
    
    def get_vfits_dtos_4_list_of_ids(self, vfi_ts_ids: list[int], session = None):
        if not session:
            with DBSessionProvider() as session:
                orms = dao.vfi_timeseries.get_by_ids(session, vfi_ts_ids)
                return BaseMapper.models_2_dto_list(orms, VfiTimeSeriesDTO)
        else:
            orms = dao.vfi_timeseries.get_by_ids(session, vfi_ts_ids)
            return BaseMapper.models_2_dto_list(orms, VfiTimeSeriesDTO)
    
    def get_first_quote_date_4_vfi_ts(self, vfi_ts_dto: VfiTimeSeriesDTO, model_cls, session = None):
        """
        Returns the earliest timestamp or q_date for a given VFI Time Series.
        """
        if session:
            return self._get_first_quote_date_for_vfi_ts(vfi_ts_dto, model_cls, session)
        else: 
            with DBSessionProvider() as session:
                return self._get_first_quote_date_for_vfi_ts(vfi_ts_dto, model_cls, session)
        return None

    def _get_first_quote_date_for_vfi_ts(self, vfi_ts_dto: VfiTimeSeriesDTO, model_cls, session):
        vfi_ts_id = vfi_ts_dto.id

        # 1. Dynamically identify the date/time column 
        # Intraday tables use 'timestamp', others use 'q_date'
        date_col = getattr(model_cls, 'timestamp', None)
        if date_col is None:
            date_col = getattr(model_cls, 'q_date')
        # 2. Query for the minimum date with proper join
        stmt = select(func.min(date_col)).join(
            VfiTimeSeries, model_cls.vfi_time_series_id == VfiTimeSeries.id
        ).where(VfiTimeSeries.id == vfi_ts_id)
        result = session.execute(stmt).scalar()
        if result is not None and isinstance(result, dt.datetime):
            result = result.date()
        return result


    def upsert_vfi_ts_dto(self, session, vfi_ts_dto: VfiTimeSeriesDTO, commit=False):
        model = dao.vfi_timeseries.get_by_id(session, vfi_ts_dto.id)
        if model is None:
            # Create new record
            model = VfiTimeSeries()
            BaseMapper.map_dto_2_model(vfi_ts_dto, model)
            session.add(model)
        else:
            # Update existing record
            BaseMapper.map_dto_2_model(vfi_ts_dto, model)
        
        # Ensure changes are sent to database
        session.flush()
        
        if commit:
            session.commit()
        
        return model


    def get_vfi_timeframe_id_2_timeframe_code(self):
        with DBSessionProvider() as session:
            stmt = select(
                Timeframe.id, Timeframe.code
            )
            result = session.execute(stmt).all()
            return {row[0]: row[1] for row in result}


SERVICES_PROVIDER = ServicesProvider()
