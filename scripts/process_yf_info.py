from decimal import Decimal
import sys
import os
import json
import csv
import logging
import datetime as dt
import re
from typing import Any, Type, TypeVar
from pathlib import Path
from dataclasses import dataclass, asdict
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zb_quotes.models.models import Base, Fit, Gfi, GfiFundamentals, Sector, Industry, Country, Qfi, Market, Vendor, Vfi, Timeframe, VfiTimeSeries
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


# ── Directiories setup ───────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" 
FOREIGN_INFO_PATH = PROCESSED_DATA_PATH / "yf_info_mb_foreign.json"
FOREIGN_CSV_PATH  = PROCESSED_DATA_PATH / "mb_foreign_all.csv"
POLISH_INFO_PATH  = PROCESSED_DATA_PATH / "yf_info_mb_polish.json"
POLISH_JSON_PATH  = PROCESSED_DATA_PATH / "mb_pol_yf_ticker_to_isin.json"


# -- Data class for gathering additional - to yf info - data -------------------
@dataclass
class AdditionalInfo:
    isin:      str
    ticker_yf: str
    ticker_bl: str | None = None
    ticker_go: str | None = None




# ────── Mapping info to db configuration ─────────────────────────────────────────────────────
@dataclass
class Info2DbVal:
    src:       str
    transform: callable = None
    cast:      callable = None # e.g., int, float, str / Concern future use
    
def ts_to_date(ts):
    return dt.date.fromtimestamp(ts) if ts else None

def get_clean_name(name):   
    if name:
        # Collapse multiple spaces
        name = ' '.join(name.split())
        # Remove trailing single letter if it looks like an artifact
        if re.search(r'\s+[A-Z]$', name):
            name = re.sub(r'\s+[A-Z]$', '', name)
    
    return name

def get_gfi_names_from_db():
    with Session(engine) as session:
        stmt = select(Gfi.name)
        gfi_names = session.execute(stmt).scalars().all()
    return list(gfi_names)

GFI_NAMES_SET = set(get_gfi_names_from_db())

def assure_unique_gfi_name(name: str, info: dict, gfi_with_changed_name: list) -> str:
    c = 0
    is_unique = False
    orig_name = name
    while not is_unique:
        if name in GFI_NAMES_SET: # modify name to make it unique
            if c == 0:
                suffix = info.get('isin', '') + ' ' + info.get('ticker_yf', '')
                name = name[:45-len(suffix)] + ' ' + suffix
            else:
                additiona_suffix = f"-({c})"
                name = name[:45-len(additiona_suffix)] + additiona_suffix
            c += 1
        else:
            is_unique = True
    GFI_NAMES_SET.add(name)
    if c > 0:
        gfi_with_changed_name.append(f"{orig_name} -> {name}")
    return name
   
MAP_DB_TO_INFO = {
    Gfi: {
        Gfi.name.key:        Info2DbVal('shortName', transform=get_clean_name),
        Gfi.description.key: Info2DbVal('longName'),
        Gfi.isin.key:        Info2DbVal('isin'),
        Gfi.ticker_yf.key:   Info2DbVal('ticker_yf'),
        Gfi.ticker_bl.key:   Info2DbVal('ticker_bl'),
        Gfi.ticker_go.key:   Info2DbVal('ticker_go'),
    },
    GfiFundamentals: {
        GfiFundamentals.shares_outstanding.key:   Info2DbVal('sharesOutstanding'),
        GfiFundamentals.last_price.key:           Info2DbVal('currentPrice', cast=Decimal),
        GfiFundamentals.market_cap.key:           Info2DbVal('marketCap',    cast=Decimal),

        GfiFundamentals.pe.key:                   Info2DbVal('trailingPE', cast=Decimal),
        GfiFundamentals.pe_forward.key:           Info2DbVal('forwardPE', cast=Decimal),
        GfiFundamentals.eps.key:                  Info2DbVal('trailingEps', cast=Decimal),
        GfiFundamentals.eps_forward.key:          Info2DbVal('forwardEps', cast=Decimal),
        GfiFundamentals.book_value_per_share.key: Info2DbVal('bookValue', cast=Decimal),
        GfiFundamentals.p_bv.key:                 Info2DbVal('priceToBook', cast=Decimal),
        GfiFundamentals.total_revenue.key:        Info2DbVal('totalRevenue', cast=Decimal),
        GfiFundamentals.beta.key:                 Info2DbVal('beta', cast=Decimal),

        GfiFundamentals.dividend_yield.key:       Info2DbVal('dividendYield', cast=Decimal),
        GfiFundamentals.last_dividend_amount.key: Info2DbVal('lastDividendValue', cast=Decimal),
        GfiFundamentals.last_dividend_date.key:   Info2DbVal('lastDividendDate', transform=ts_to_date),
        GfiFundamentals.week_52_high.key:         Info2DbVal('fiftyTwoWeekHigh', cast=Decimal),
        GfiFundamentals.week_52_low.key:          Info2DbVal('fiftyTwoWeekLow', cast=Decimal),
    },
    Qfi: {
        Qfi.name.key:          Info2DbVal('symbol'),           # or longName
        Qfi.description.key:   Info2DbVal('longName'), # rich description
    },
}


def get_additional_data_for_foreign() -> dict | None:
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


def get_additional_data_for_polish() -> dict:
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



def report_end(counter_processed: int, counter_skipped: int, gfi_seeded: list, qfi_seeded: list, vfi_seeded: list, vfi_ts_seeded: list):
    print("--------------------------------")
    print(f"Processed: {counter_processed}")
    print(f"Skipped:   {counter_skipped}")
    print(f"GFI seeded: {len(gfi_seeded)}")
    print(f"QFI seeded: {len(qfi_seeded)}")
    print(f"VFI seeded: {len(vfi_seeded)}")
    print(f"VFI TS seeded: {len(vfi_ts_seeded)}")
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

def report_seeding_item(key, info, counter: list):
    if counter[0] % 100 == 0:
        print(f"Seeding {counter[0]+counter[1]}/{counter[2]}:  {key}, {info['isin']}")



def set_counters(success: bool, counter_processed: int, counter_skipped: int):
    if success:
        counter_processed += 1
    else:
        counter_skipped += 1
    return counter_processed, counter_skipped



def get_id_by(session:   Session, 
                  model_cls: Type[ModelType], 
                  unique_fields: dict[str, Any]) -> int:
    stmt = select(model_cls).filter_by(**unique_fields)
    obj  = session.execute(stmt).scalar_one_or_none()
    return obj.id if obj else None

def get_by_fields(session:   Session, 
                  model_cls: Type[ModelType], 
                  unique_fields: dict[str, Any]) -> ModelType:
    stmt = select(model_cls).filter_by(**unique_fields)
    obj  = session.execute(stmt).scalar_one_or_none()
    return obj



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
    else:
        # if obj.ticker_yf != existing_obj.ticker_yf: # another qfi with the same isin
        #     print(f"Warning: Another qfi with the same isin {obj.isin} already exists with ticker {existing_obj.ticker_yf}")
        #     # add to additional_qfis
        #     additional_qfis.append((obj.ticker_yf, obj.isin))
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
    if sector_name:
        sector_id = get_or_insert(session, Sector, {'name': sector_name}).id
    industry_name = yf_data.get('industryKey')
    if industry_name:
        industry_id = get_or_insert(session, Industry, {'sector_id': sector_id, 'name': industry_name}).id
    country_name = yf_data.get('country')
    if country_name:
        country_id = get_id_by(session, Country, {'name': country_name}) # no insert, only get
   
    return {
        Gfi.fit_id.key      : fit_id,
        Gfi.sector_id.key   : sector_id,
        Gfi.industry_id.key : industry_id,
        Gfi.country_id.key  : country_id,
    }


def get_qfi_foreign_keys(session, info):
    market_id, currency_id = None, None
    market_name = info.get('exchange')
    # yfinance exchange codes -> market codes
    # dont know ASE
    match market_name:
        case 'NMS': market_name = 'XNAS'
        case 'NYQ': market_name = 'XNYS'
        case 'GER': market_name = 'XETR'
        case 'LSE': market_name = 'XLON'
        case 'WSE': market_name = 'XWAR'
        case _: market_name = None
    if market_name:
        market_id = get_id_by(session, Market, {'mic': market_name})
    currency_name = info.get('currency')
    currency_id = get_id_by(session, Gfi, {'name': currency_name})
    if market_id is None:
        print(f'--- Market - exchange: {info.get("exchange")} not found for {info["ticker_yf"]}')
    if currency_id is None:
        print(f'--- Currency: {info.get("currency")} not found for {info["ticker_yf"]}')

    if market_id is None or currency_id is None:
        return None
    return {
        'market_id': market_id,
        'currency_id': currency_id,
    }


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
        gfi.fundamentals = fundamentals
    map_dictdata_to_model(info, GfiFundamentals, MAP_DB_TO_INFO[GfiFundamentals], fundamentals)
    fundamentals.updated_at = dt.datetime.now()
    fundamentals.source_vendor = "YF"
    session.add(fundamentals)
    session.flush()


def seed_qfi(session: Session, info: dict, gfi_id: int):
    qfi: Qfi
    existing_qfi = get_by_fields(session, Qfi, {Qfi.gfi_id.key: gfi_id, Qfi.name.key: info.get('symbol')})
    if existing_qfi:
        qfi = existing_qfi
    else:
        qfi = Qfi(gfi_id= gfi_id)
    map_dictdata_to_model(info, Qfi, MAP_DB_TO_INFO[Qfi], qfi)
    if info.get('quoteType') in ['EQUITY', 'ETF']:
        qfi.quoted_amount = 1
        qfi.quoted_unit_id = 1 # shares - based on predefined data in seed.py ? change to seek for?
    else:
        print(f'---> Not found quoteType: {info.get("quoteType")} for {info.get("symbol")}')
        return
    
    # qfi.source_vendor = "YF"
    qfi_fkeys = get_qfi_foreign_keys(session, info)
    if qfi_fkeys:
        set_attrs_of_obj(qfi, qfi_fkeys)
        session.add(qfi)
        return qfi
    else:
        print(f'-------> QFI foreign keys not found for {info.get("symbol")}')
        return None


def seed_gfi(session: Session, info: dict, info_without_name: list, gfi_with_changed_name: list):
    gfi = Gfi()
    map_dictdata_to_model(info, Gfi, MAP_DB_TO_INFO[Gfi], gfi) # keeps added records (Sector, Industry) in session
    if gfi.name is None:
        gfi.name = info.get('longName') or info.get('shortName') or info.get('symbol')
        info_without_name.append(info) # for diagnostic info_without_name.append(info.get('symbol'))
    gfi.name = assure_unique_gfi_name(gfi.name, info, gfi_with_changed_name)
    gfi_fkeys = get_gfi_foreign_keys(session, info)
    if gfi_fkeys:
        set_attrs_of_obj(gfi, gfi_fkeys)
        insert_or_update(session, Gfi, gfi, {Gfi.isin.key: gfi.isin})
        update_fundamentals(session, info, gfi)
        return gfi
    else:
        return None

#───────────────────────────────────────────────────────────────────
# Main seed function
#───────────────────────────────────────────────────────────────────
def seed_single_gfi_qfi(session, info: dict, types_not_found: list, info_without_name: list, 
                gfi_seeded: list = [], 
                qfi_seeded: list = [],
                gfi_with_changed_name: list = []):
    result = False
    gfi = seed_gfi(session, info, info_without_name, gfi_with_changed_name)
    gfi_seeded.append(gfi)
    if gfi:
        qfi = seed_qfi(session, info, gfi.id)
        if qfi:
            qfi_seeded.append(qfi)
            result = True
    else: # for future diagnostics
        if info.get('quoteType') not in types_not_found:
            types_not_found.append((info.get('quoteType'), info.get('ticker_yf')))


    return result





def register_seed_result(yf_tckr, success, processed, skipped, counter):
    if success:
        processed.append(yf_tckr)
        counter[0] += 1
    else:
        skipped.append(yf_tckr)
        counter[1] += 1




def get_info_and_additional_data() -> list[tuple[dict[str, dict], dict[str, AdditionalInfo]]]:
    """
    Returns a list of tuples containing info and additional data.
    
    Each tuple contains:
    - info_dict: Dictionary with YF info: yf_ticker -> yf_info # lacks isin
    - additional_dict: Dictionary with additional data: yf_ticker -> AdditionalInfo(isin, other_fields)
    """
    info_polish = get_data_from_json_file(POLISH_INFO_PATH)
    info_foreign = get_data_from_json_file(FOREIGN_INFO_PATH)
    additional_polish  = get_additional_data_for_polish()
    additional_foreign = get_additional_data_for_foreign()
    duplicates = set(additional_polish.keys()) & set(additional_foreign.keys())
    report_duplicates(duplicates)
    return [
        [info_polish,  additional_polish],
        [info_foreign, additional_foreign]
    ]

def report_input_preparing(list_of_info_and_additional_data, yf_tickers_not_found, infos_for_additional_qfi):
    """
    Reports the input preparing process.
    """
    print('-----------------------------')
    print("Input preparing report:")
    c = [0,0 ]
    c_not_found = len(yf_tickers_not_found)
    c_add_qfi = len(infos_for_additional_qfi)
    for a, i in list_of_info_and_additional_data:
        c[0] += len(a)
        c[1] += len(i)
        print(f'additional: {len(a)}, info: {len(i)}')
    print('-----------------------------')
    print(f'total isins: {c[0]}, total info: {c[1]}, diff: {c[0] - c[1]}')
    print(f"  - yf_tickers_not_found    : {c_not_found}")
    print(f"  - infos_for_additional_qfi: {c_add_qfi}")
    print('-----------------------------')
    

def prepare_gfi_infos():
    """
    Returns 
    - a dictionary [yf_ticker->yf_info_dict]
    - a list of YF tickers for which yf_info_dict was not found
    - a dictionary [yf_ticker->additional_info_dict] for additional QFI data (with the same ISIN)
    """
    r = {}
    yf_tickers_not_found = []
    infos_for_additional_qfi = {}
    isin_already_added = set()
    list_of_info_and_additional_data = get_info_and_additional_data()
    for info_dict, additional_dict in list_of_info_and_additional_data:
        # pairs additional_dict -> info_dict
        for additional in additional_dict.values():
            cur_yf_ticker = additional.ticker_yf
            info = info_dict.get(cur_yf_ticker)
            if not info:
                # put info in not_found
                # print(f"Info not found for ticker: {cur_yf_ticker}")
                yf_tickers_not_found.append(cur_yf_ticker)
            else:
                additional_info_dict = asdict(additional)
                proper_dict = {**info, **additional_info_dict}
                # only one isin for Gfi
                if additional.isin not in isin_already_added:
                    r[cur_yf_ticker] = proper_dict
                    isin_already_added.add(additional.isin)
                else:
                    infos_for_additional_qfi[cur_yf_ticker] = proper_dict
                    # print(f"Isin {additional.isin} already added, {cur_yf_ticker} moved to additional QFI")

    report_input_preparing(list_of_info_and_additional_data, yf_tickers_not_found, infos_for_additional_qfi)
    return r, yf_tickers_not_found, infos_for_additional_qfi


def report_types_not_found(types_not_found):
    print('-----------------')
    print("Types not found:")
    for type, ticker in types_not_found:
        print(f"{type} in: {ticker}")
    print('-----------------')

def report_info_not_found(infos_without_name):
    print('-----------------')
    print("Infos with no name - used yf_ticker as name:")
    for info in infos_without_name:
        print(info.get('symbol'))
    print('-----------------')

def report_gfi_with_changed_name(gfi_with_changed_name):
    print('-----------------')
    print("GFI names with changed name:")
    for gfi  in gfi_with_changed_name:
        print(gfi)
    print('-----------------')


def seed_vfi_for_yFinance(session, qfi: Qfi):
    yf_vendor_id = 1 # predefined data, based on seed.py
    yf_vendor_suffix = "_YF"
    existing_vfi = get_by_fields(session, Vfi, {'qfi_id': qfi.id, 'vendor_id': yf_vendor_id})
    if existing_vfi:
        vfi = existing_vfi
    else:
        vfi = Vfi(qfi_id=    qfi.id, 
                  vendor_id= yf_vendor_id)
        session.add(vfi)
    
    qfi_description = qfi.description or ""
    set_attrs_of_obj(vfi, {
            Vfi.vendor_ticker.key: qfi.gfi.ticker_yf,
            Vfi.name.key:          qfi.name        + yf_vendor_suffix,
            Vfi.description.key:   qfi_description
        })
    session.flush()
    return vfi
    

def seed_additional_qfis(session, infos_to_additional_qfis, qfi_seeded):
    print("Seeding additional QFIs...")
    c = 0
    for info in infos_to_additional_qfis.values():
        gfi = get_by_fields(session, Gfi, {Gfi.isin.key: info.get('isin')})
        qfi = seed_qfi(session, info, gfi.id)
        if qfi:
            qfi_seeded.append(qfi)
            print(f'{c}. Additional qfi {qfi.name} added for isin: {info.get("isin")}')
            c += 1

def seed_vfis(session, qfi_seeded, vfi_seeded):
    for qfi in qfi_seeded:
        vfi = seed_vfi_for_yFinance(session, qfi)
        vfi_seeded.append(vfi)

def get_time_frames_from_db(session):
    stmt = select(Timeframe)
    return session.execute(stmt).scalars().all()

def seed_vfi_ts(session, vfi_seeded, vfi_ts_seeded):
    time_frames = get_time_frames_from_db(session)
    for vfi in vfi_seeded:
        for time_frame in time_frames:
            vfi_ts = VfiTimeSeries(vfi_id=vfi.id, timeframe_id=time_frame.id)
            session.add(vfi_ts)
            vfi_ts_seeded.append(vfi_ts)
    session.flush()

def process_all():
    processed, skipped, types_not_found, info_without_name = [], [], [], []
    infos_to_gfis, yf_tickers_not_found, infos_to_additional_qfis = prepare_gfi_infos()
    counter = [0, 0, len(infos_to_gfis)] # processed, skipped, total
    gfi_seeded, qfi_seeded, vfi_seeded, vfi_ts_seeded = [], [], [], []
    gfi_with_changed_name = []
    with Session(engine) as session:
        for info in infos_to_gfis.values():
            success = seed_single_gfi_qfi(session, info, types_not_found, info_without_name, gfi_seeded, qfi_seeded, gfi_with_changed_name) # -> db, types_not_found, info_without_name
            register_seed_result(info['ticker_yf'], success, processed, skipped, counter)
            report_seeding_item(info['ticker_yf'], info, counter)
        

        if infos_to_additional_qfis:
            seed_additional_qfis(session, infos_to_additional_qfis, qfi_seeded)
                
        seed_vfis(session, qfi_seeded, vfi_seeded)
                
        seed_vfi_ts(session, vfi_seeded, vfi_ts_seeded)

        
        # session.rollback() # testing phase
        session.commit() # save all changes to db
    
    report_types_not_found(types_not_found)
    report_info_not_found(info_without_name)
    report_gfi_with_changed_name(gfi_with_changed_name)
    report_end(counter[0], counter[1], gfi_seeded, qfi_seeded, vfi_seeded, vfi_ts_seeded)    

def main():
    # process_yf_info_json_file(FOREIGN_INFO_PATH)
    process_all()


if __name__ == "__main__":
    main()