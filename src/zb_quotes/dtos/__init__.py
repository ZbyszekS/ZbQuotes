"""
DTO (Data Transfer Object) layer for ZbQuotes.

This module provides data transfer objects that can be safely passed
between different layers of the application without SQLAlchemy session dependencies.
"""

from .country_dto import CountryDTO
from .vfi_time_serie_dto import VfiTimeSeriesDTO

__all__ = [
    'CountryDTO',
    'VfiTimeSeriesDTO'
]
