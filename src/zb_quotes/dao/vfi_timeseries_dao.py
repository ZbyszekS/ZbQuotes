import datetime as dt
from zb_quotes.dao.base_dao import BaseDao
from zb_quotes.models.models import VfiTimeSeries

class VfiTimeSeriesDao(BaseDao[VfiTimeSeries]):
    def __init__(self):
        super().__init__(VfiTimeSeries)

    def get_all_enabled(self, session):
        return self.get_many_by_unique_cols(session, enabled=True)
    
    def get_all_enabled_and_not_updated(self, session):
        return self.get_many(
            session,
            VfiTimeSeries.enabled == True,
            VfiTimeSeries.last_imported_to < dt.date.today()
        )
    
    def get_by_ids(self, session, vfi_ts_ids):
        return self.get_many(session, VfiTimeSeries.id.in_(vfi_ts_ids))
