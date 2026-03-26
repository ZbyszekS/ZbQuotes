import sys
import os
import json
import csv
import logging
from typing import Any, Type, TypeVar
from pathlib import Path
from dataclasses import dataclass, asdict
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zb_quotes.models.models import Base, Fit, Gfi, GfiFundamentals, Sector, Industry, Country, Qfi, Market
ModelType = TypeVar("ModelType", bound=Base) # Type variable for SQLAlchemy models

# ── Logger creation ───────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ── Database connection ───────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
DATABASE_URL = os.getenv("DATABASE_URL") # e.g., "sqlite:////path/to/your/database.db" defined in .env file
print(f"DEBUG: DATABASE_URL = {DATABASE_URL}")
engine = create_engine(DATABASE_URL, echo=False)


# directory where import_data.py lives
# ZbQuotes root directory
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" 
FOREIGN_INFO_PATH = PROCESSED_DATA_PATH / "yf_info_mb_foreign.json"
FOREIGN_CSV_PATH  = PROCESSED_DATA_PATH / "mb_foreign_all.csv"
POLISH_INFO_PATH  = PROCESSED_DATA_PATH / "yf_info_mb_polish.json"
POLISH_JSON_PATH  = PROCESSED_DATA_PATH / "mb_pol_yf_ticker_to_isin.json"



@dataclass
class AdditionalInfo:
    isin:      str
    ticker_yf: str
    ticker_bl: str | None = None
    ticker_go: str | None = None


def additional_data_for_foreign() -> dict | None:
    try:
        data = {}
        with open(FOREIGN_CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row["yf_symbol"]
                data[key] = AdditionalInfo(
                    isin      = row["isin"],
                    ticker_yf = row["yf_symbol"],
                    ticker_bl = row["ticker_bloomberg"],
                    ticker_go = row["ticker_google"],)
        return data

    except FileNotFoundError:
        print(f"---> File not found: {FOREIGN_CSV_PATH}")
        return None


def additional_data_for_polish() -> dict:
    data = get_data_from_json_file(POLISH_JSON_PATH)
    if data:
        r = {}
        for k, v in data.items():
            r[k] = AdditionalInfo(
                isin      = v,
                ticker_yf = k,
                ticker_bl = None,
                ticker_go = None
            )
        return r

    return None



def get_data_from_json_file(path_to_file: Path) -> dict:
    try:
        with open(path_to_file, "r") as f:
            data = json.load(f)
        return data

    except FileNotFoundError:
        print(f"---> File not found: {path_to_file}")
        return None
    except json.JSONDecodeError:
        print(f"---> Invalid JSON in: {path_to_file}")
        return None
    except Exception as e:
        print(f'---> {e}')
        return None




# def get_or_create(session: Session, model: ModelType, name: str | None):
#     if not name:
#         return None

#     obj = session.execute(
#         select(model).where(model.name == name)
#     ).scalar_one_or_none()

#     if obj:
#         return obj.id

#     obj = model(name=name)
#     session.add(obj)
#     session.flush()

#     return obj.id





def report_end(counter_processed: int, counter_skipped: int):
    print("--------------------------------")
    print(f"Processed: {counter_processed}")
    print(f"Skipped:   {counter_skipped}")
    print("--------------------------------")

def report_init(fPath: Path, dict_data: dict):
    print("-------------------------------------------------------")
    print(f"Start processing: \n{fPath}, \nwith {len(dict_data)} entries")
    print("-------------------------------------------------------\n")

# def report_seeding_item(key, info: AdditionalInfo):
#     print(f"Seeding: {key}, {info.isin}, {info.ticker_yf}, {info.ticker_bl}, {info.ticker_go}")

def report_duplicates(duplicates: set):
    if duplicates:
        print(f"Duplicate keys: {duplicates}")
    else:
        print("No duplicates found! :)")

def report_seeding_item(key, info, len_additional_data, counter_processed, counter_skipped):
    print(f"Seeding {counter_processed+counter_skipped}/{len_additional_data}:  {key}, {info}")



def set_counters(success: bool, counter_processed: int, counter_skipped: int):
    if success:
        counter_processed += 1
    else:
        counter_skipped += 1
    return counter_processed, counter_skipped



# # main seeding function ---------------------------------------------------------
# def process_info(info_dict: dict) -> bool:
#     # country_id = get_or_create_country(additional_info.isin)
#     return True


# -------------------------------- Mapping Configuration --------------------------------
@dataclass
class Info2DbVal:
    # db_column: str
    src: str
    transform: callable = None
    cast: callable = None # e.g., int, float, str / Concern future use
    
    
    
MAP_DB_TO_INFO = {
    Gfi: {
        Gfi.name.key:        Info2DbVal('shortName'),
        Gfi.description.key: Info2DbVal('longName'),
        Gfi.isin.key:        Info2DbVal('isin'),
        Gfi.ticker_yf.key:   Info2DbVal('ticker_yf'),
        Gfi.ticker_bl.key:   Info2DbVal('ticker_bl'),
        Gfi.ticker_go.key:   Info2DbVal('ticker_go'),
    },
    GfiFundamentals: {
        GfiFundamentals.shares_outstanding.key:   Info2DbVal('sharesOutstanding'),
        GfiFundamentals.last_price.key:           Info2DbVal('currentPrice'),
        GfiFundamentals.market_cap.key:           Info2DbVal('marketCap'),

        GfiFundamentals.pe.key:                   Info2DbVal('trailingPE'),
        GfiFundamentals.pe_forward.key:           Info2DbVal('forwardPE'),
        GfiFundamentals.eps.key:                  Info2DbVal('trailingEps'),
        GfiFundamentals.eps_forward.key:          Info2DbVal('forwardEps'),
        GfiFundamentals.book_value_per_share.key: Info2DbVal('bookValue'),
        GfiFundamentals.p_bv.key:                 Info2DbVal('priceToBook'),
        GfiFundamentals.total_revenue.key:        Info2DbVal('totalRevenue'),
        GfiFundamentals.beta.key:                 Info2DbVal('beta'),

        GfiFundamentals.dividend_yield.key:       Info2DbVal('dividendYield'),
        GfiFundamentals.last_dividend_amount.key: Info2DbVal('lastDividendValue'),
        GfiFundamentals.last_dividend_date.key:   Info2DbVal('lastDividendDate'),
        GfiFundamentals.week_52_high.key:         Info2DbVal('fiftyTwoWeekHigh'),
        GfiFundamentals.week_52_low.key:          Info2DbVal('fiftyTwoWeekLow'),
    },
    # ── New: Qfi mapping ─────────────────────────────────────────────────────
    Qfi: {
        Qfi.name.key:          Info2DbVal('shortName'),           # or longName
        Qfi.description.key:   Info2DbVal('longBusinessSummary'), # rich description

        # Core identification fields
        Qfi.gfi_id.key:        None,   # will be set manually (link to parent Gfi)
        Qfi.market_id.key:     None,   # will be resolved via Market model (see below)
        Qfi.currency_id.key:   None,   # will be resolved via Currency Gfi (PLN, USD...)
        Qfi.quoted_unit_id.key:None,   # usually "Shares" for equities → resolve via QuotedUnit

        # Important yf fields for Qfi
        Qfi.quoted_amount.key: Info2DbVal('quoteType', 
            transform=lambda x: 1 if x == "EQUITY" else None),  # example: 1 share unit

        # Optional but useful
        # You can add a custom column later if you want to store raw quoteType
    },
}

# MAP_FOREIGN_KEYS = {
#     Gfi: {
#         Gfi.fit_id.key:      Info2DbVal('fit_id'),
#         Gfi.sector_id.key:   Info2DbVal('sector_id'),
#         Gfi.industry_id.key: Info2DbVal('industry_id'),
#         Gfi.country_id.key:  Info2DbVal('country_id'),
#     }
# }

# @dataclass
# class GfiForeignKeys:
#     fit_id:      int
#     sector_id:   int
#     industry_id: int
#     country_id:  int



def get_id_by(session:   Session, 
              model_cls: Type[ModelType], 
              data:      dict[str, Any]) -> int:
    stmt = select(model_cls).filter_by(**data)
    obj  = session.execute(stmt).scalar_one_or_none()
    return obj.id if obj else None


def get_or_insert(session:   Session, 
                  model_cls: Type[ModelType], 
                  data:      dict[str, Any],
                  flush:     bool = True) -> ModelType:
    stmt = select(model_cls).filter_by(**data)
    obj  = session.execute(stmt).scalar_one_or_none()
    if obj is None:
        obj = model_cls(**data)
        session.add(obj)
        if flush:
            session.flush()
    return obj


def insert_or_update(session: Session, model_cls: Type[ModelType], obj: ModelType, unique_fields: dict[str, Any]):
    stmt = select(model_cls).filter_by(**unique_fields)
    existing_obj = session.execute(stmt).scalar_one_or_none()
    if existing_obj is None:
        session.add(obj)
        session.flush()
    else:
        mapper = inspect(model_cls)
        for column in mapper.columns:
            key = column.key
            setattr(existing_obj, key, getattr(obj, key))
        session.flush()


def get_gfi_foreign_keys(session, yf_data: dict): # -> MAP_FOREIGN_KEYS
    fit_id, sector_id, industry_id, country_id = None, None, None, None
    quote_type = yf_data.get('quoteType')
    match quote_type: # based on predefined data in seed.py
        case 'EQUITY':
            fit_id = 2
        case 'ETF':
            fit_id = 7

    if fit_id is None:
        return None

    sector_name = yf_data.get('sectorKey')
    if sector_name != "":
        sector_id = get_or_insert(session, Sector, {'name': sector_name}).id
    industry_name = yf_data.get('industryKey')
    if industry_name != "":
        industry_id = get_or_insert(session, Industry, {'name': industry_name}).id
    country_name = yf_data.get('country')
    if country_name != "":
        country_id = get_id_by(session, Country, {'name': country_name}) # no insert, only get

    # MAP_FOREIGN_KEYS[Gfi][Gfi.fit_id.key]      = fit_id
    # MAP_FOREIGN_KEYS[Gfi][Gfi.sector_id.key]   = sector_id
    # MAP_FOREIGN_KEYS[Gfi][Gfi.industry_id.key] = industry_id
    # MAP_FOREIGN_KEYS[Gfi][Gfi.country_id.key]  = country_id
    
    return {
        Gfi.fit_id.key      : fit_id,
        Gfi.sector_id.key   : sector_id,
        Gfi.industry_id.key : industry_id,
        Gfi.country_id.key  : country_id,
    }
    # return GfiForeignKeys(
    #     fit_id=fit_id,
    #     sector_id=sector_id,
    #     industry_id=industry_id,
    #     country_id=country_id
    # )


def map_dictdata_to_model(data: dict, model_cls, mapping: dict, obj = None):
    """
    Map JSON data to a model instance.
    
    Args:
        data:      data dictionary from yf info + adds: {info_key: info_value}
        model_cls: Model class to map to
        mapping:   Mapping configuration
        obj:       Existing object to update (optional) or create new one
        
    Returns:
        Model instance with mapped values from data parameter
    """
    if obj is None:
        obj = model_cls()

    for field, cfg in mapping.items():
        src = cfg.src
        value = data.get(src)

        if value is None:
            continue

        # transform
        if cfg.transform is not None:
            value = cfg.transform(value)

        # cast
        if cfg.cast is not None and value is not None:
            value = cfg.cast(value)

        setattr(obj, field, value)

    return obj    


# obsolete
# def set_foreign_keys(model_cls, obj):
#     for field, value in MAP_FOREIGN_KEYS[model_cls].items():
#         setattr(obj, field, value)

def set_attrs_of_obj(obj, attrs: dict):
    for field, value in attrs.items():
        setattr(obj, field, value)

def update_fundamentals(session: Session, info: dict, gfi: Gfi):
    fundamentals = gfi.fundamentals
    if fundamentals is None:
        fundamentals = GfiFundamentals(gfi_id= gfi.id)
    map_dictdata_to_model(info, GfiFundamentals, MAP_DB_TO_INFO[GfiFundamentals], fundamentals)
    session.add(fundamentals)

#───────────────────────────────────────────────────────────────────
# Main seed function
#───────────────────────────────────────────────────────────────────
def seed_single(session, info: dict):

    # gfi = get_or_insert(session, Gfi, {Gfi.ticker_yf.key: info.get(MAP_DB_TO_INFO[Gfi][Gfi.ticker_yf.key].src)})
    gfi = Gfi()
    map_dictdata_to_model(info, Gfi, MAP_DB_TO_INFO[Gfi], gfi) # keeps added records (Sector, Industry) in session
    gfi_fkeys = get_gfi_foreign_keys(session, info)
    set_attrs_of_obj(gfi, gfi_fkeys)
    # set_foreign_keys(Gfi, gfi)
    insert_or_update(session, Gfi, gfi, {Gfi.isin.key: gfi.isin})
    update_fundamentals(session, info, gfi)
    print(gfi)
    
    if info is None:
        logger.warning(f"YF info not found for {info.get('symbol')}")
        success = False
    else:
        print(info.get("longName"))
        success = process_info(info)
    return success





def register_processed_or_skipped(yf_tckr, success, processed, skipped):
    if success:
        processed.append(yf_tckr)
    else:
        skipped.append(yf_tckr)




def get_info_and_additional_data():
    """
    Returns a list of tuples containing info and additional data.
    
    Each tuple contains:
    - info_dict: Dictionary with YF info: yf_ticker -> yf_info # lacks isin
    - additional_dict: Dictionary with additional data: yf_ticker -> AdditionalInfo(isin, other_fields)
    """
    info_polish = get_data_from_json_file(POLISH_INFO_PATH)
    info_foreign = get_data_from_json_file(FOREIGN_INFO_PATH)
    additional_polish  = additional_data_for_polish()
    additional_foreign = additional_data_for_foreign()
    duplicates = set(additional_polish.keys()) & set(additional_foreign.keys())
    report_duplicates(duplicates)
    return [
        [info_polish,  additional_polish],
        [info_foreign, additional_foreign]
    ]


def process_all():
    # info_dict = get_data_from_json_file(path_to_file)
    counter_processed, counter_skipped = 0, 0
    processed, skipped = [], []
    info_and_additional_data_list = get_info_and_additional_data()
    with Session(engine) as session:
        for info_dict, additional_dict in info_and_additional_data_list:
            # looping only through additional_dict
            for additional in additional_dict.values():
                info = info_dict.get(additional.ticker_yf)
                info.update(asdict(additional)) # adding isin, yf_symbol, bloomberg and google tickers
                success = seed_single(session, info)
                counter_processed, counter_skipped = set_counters(success, counter_processed, counter_skipped)
                register_processed_or_skipped(additional.ticker_yf, success, processed, skipped)
                report_seeding_item(additional.ticker_yf, additional, len(additional_dict), counter_processed, counter_skipped)

        report_end(counter_processed, counter_skipped)
            

def main():
    # process_yf_info_json_file(FOREIGN_INFO_PATH)
    process_all()


if __name__ == "__main__":
    main()