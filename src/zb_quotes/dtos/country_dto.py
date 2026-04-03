# src/zb_quotes/country_dto.py
from dataclasses import dataclass
from .base_dto import BaseDTO

@dataclass
class CountryDTO(BaseDTO):
    id:          int
    iso_code_2:  str
    name:        str
    description: str | None = None
    region:      str | None = None
    subregion:   str | None = None
    

