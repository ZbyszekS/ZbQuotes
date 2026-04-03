from typing import Optional
from dataclasses import dataclass
from datetime import date, datetime

from zb_quotes.models.models import VfiTimeSeries
from .base_dto import BaseDTO

@dataclass
class VfiTimeSeriesDTO(BaseDTO):
    id:           int
    vfi_id:       int
    timeframe_id: int
    
    # import control
    enabled:        bool       = False
    history_days:   int | None = None   # how far back to fetch

    # import state tracking
    last_imported_at:  datetime | None = None
    last_imported_from:date     | None = None
    last_imported_to:  date     | None = None

    # New field for the nested value
    yf_ticker: str | None = None  

    @classmethod
    def from_model(cls, model: VfiTimeSeries) -> Optional["VfiTimeSeriesDTO"]:
        dto = super().from_model(model)
        if dto and model:
            # Manually "reach into" the relationship chain
            # This works ONLY if these were eager-loaded or the session is still open
            try:
                dto.yf_ticker = model.vfi.qfi.gfi.ticker_yf
            except AttributeError:
                dto.yf_ticker = None
        return dto

    