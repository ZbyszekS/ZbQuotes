import sys
import os
import json
import csv
import logging
from pathlib import Path
from dataclasses import dataclass
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from zb_quotes.models.models import Fit, Gfi, CurrencyDetails, Market, QuotedUnit, QuotedUnitConversion, Timeframe

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
    isin:             str
    yf_symbol:        str
    ticker_bloomberg: str | None = None
    ticker_google:    str | None = None


def additional_data_for_foreign() -> dict | None:
    try:
        data = {}
        with open(FOREIGN_CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row["yf_symbol"]
                data[key] = AdditionalInfo(
                    isin             = row["isin"],
                    yf_symbol        = row["yf_symbol"],
                    ticker_bloomberg = row["ticker_bloomberg"],
                    ticker_google    = row["ticker_google"],)
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
                isin             = v,
                yf_symbol        = k,
                ticker_bloomberg = None,
                ticker_google    = None
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




def get_or_create(session: Session, model, name: str | None):
    if not name:
        return None

    obj = session.execute(
        select(model).where(model.name == name)
    ).scalar_one_or_none()

    if obj:
        return obj.id

    obj = model(name=name)
    session.add(obj)
    session.flush()

    return obj.id


# main seeding function ---------------------------------------------------------
def process_yf_info(info_dict: dict, additional_info: AdditionalInfo) -> bool:
    # country_id = get_or_create_country(additional_info.isin)
    return True




def report_end(counter_processed: int, counter_skipped: int):
    print("--------------------------------")
    print(f"Processed: {counter_processed}")
    print(f"Skipped:   {counter_skipped}")
    print("--------------------------------")

def report_init(fPath: Path, dict_data: dict):
    print("-------------------------------------------------------")
    print(f"Start processing: \n{fPath}, \nwith {len(dict_data)} entries")
    print("-------------------------------------------------------\n")

def report_seeding_item(key, info: AdditionalInfo):
    print(f"Seeding: {key}, {info.isin}, {info.yf_symbol}, {info.ticker_bloomberg}, {info.ticker_google}")

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


def seed_single(session, yf_tckr, additional: AdditionalInfo, info_polish, info_foreign):
    if additional.ticker_bloomberg is None: # it is polish
        yf_data = info_polish.get(yf_tckr)
    else: # it is foreign
        yf_data = info_foreign.get(yf_tckr)
    if yf_data is None:
        logger.warning(f"YF info not found for {yf_tckr}")
        success = False
    else:
        print(yf_data.get("longName"))
        success = process_yf_info(yf_tckr, additional)
    return success

def register_processed_or_skipped(yf_tckr, success, processed, skipped):
    if success:
        processed.append(yf_tckr)
    else:
        skipped.append(yf_tckr)

def process_all():
    # info_dict = get_data_from_json_file(path_to_file)
    counter_processed, counter_skipped = 0, 0
    processed, skipped = [], []
    additional_polish  = additional_data_for_polish()
    additional_foreign = additional_data_for_foreign()
    info_polish = get_data_from_json_file(POLISH_INFO_PATH)
    info_foreign = get_data_from_json_file(FOREIGN_INFO_PATH)
    additional_data = additional_polish | additional_foreign
    duplicates = set(additional_polish.keys()) & set(additional_foreign.keys())
    report_duplicates(duplicates)
    with Session(engine) as session:
        for yf_tckr, additional in additional_data.items():
            success = seed_single(session, yf_tckr, additional, info_polish, info_foreign)
            counter_processed, counter_skipped = set_counters(success, counter_processed, counter_skipped)
            register_processed_or_skipped(yf_tckr, success, processed, skipped)
            report_seeding_item(yf_tckr, additional, len(additional_data), counter_processed, counter_skipped)

        report_end(counter_processed, counter_skipped)
            

def main():
    # process_yf_info_json_file(FOREIGN_INFO_PATH)
    process_all()


if __name__ == "__main__":
    main()