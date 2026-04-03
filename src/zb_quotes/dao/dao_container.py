from zb_quotes.dao.vfi_timeseries_dao import VfiTimeSeriesDao
# from zb_quotes.models.models import Quotes1m, Quotes1h, Quotes1d, Quotes1w, Quotes1M

class Dao:
    def __init__(self) -> None:
        self.vfi_timeseries = VfiTimeSeriesDao()

    # def get_responding_quote_model_class_4_vfits_id(self, session, vfits_id: int):
    #     # This is a placeholder - you'll need to implement the actual logic
    #     # to find the model for a given vfits_id
    #     vfits = self.vfi_timeseries.get_by_id(session, vfits_id)
    #     match vfits.timeframe_id:
    #         case 1: return Quotes1m
    #         case 2: return Quotes1h
    #         case 3: return Quotes1d
    #         case 4: return Quotes1w
    #         case 5: return Quotes1M
    #         case _:
    #             # TODO: Handle unexpected timeframe_id
    #             return None


dao = Dao()