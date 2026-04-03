from zb_quotes.dao.base_dao import BaseDao
from zb_quotes.models.models import VfiTimeSeries

class VfiTimeSeriesDao(BaseDao[VfiTimeSeries]):
    def __init__(self):
        super().__init__(VfiTimeSeries)

    def get_all_enabled(self, session):
        return self.get_many_by_unique_cols(session, enabled=True)
