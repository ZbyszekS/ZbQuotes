import sys
import logging
import csv
import time
import re
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Callable, Any

from datetime import datetime, date, timezone
import yfinance as yf
from zb_quotes.models.models import Gfi, GfiFundamentals

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# directory where import_data.py lives
SCRIPT_DIR = Path(__file__).resolve().parent
# ZbQuotes
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent

MBANK_CSV_FILE_NAME = "mbank_foreign.csv"
MBANK_CSV_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" / MBANK_CSV_FILE_NAME

YF_ALL_INFO_FILE_NAME = "yf_info.json"
YF_ALL_INFO_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" / YF_ALL_INFO_FILE_NAME
YF_ALL_INFO_SKIPPED_FILE_NAME = "yf_info_skipped.json"
YF_ALL_INFO_SKIPPED_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" / YF_ALL_INFO_SKIPPED_FILE_NAME

if not MBANK_CSV_DATA_PATH.exists():
    print("─────────────────────────────────────────────")
    print(f"Error: CSV file not found at {MBANK_CSV_DATA_PATH}")
    print("─────────────────────────────────────────────")
    sys.exit(1)

@dataclass
class mBankCsvInfo:
    isin:             str
    bloomberg_ticker: str
    goole_ticker:     str
    yf_ticker:        str



@dataclass
class FieldMapping:
    model_col:  str                        # column name on the SQLAlchemy model
    info_key:   str                        # key in the yFinance JSON
    transform:  Callable[[Any], Any] = None  # optional conversion function



def epoch_to_date(v):
    """Unix timestamp (int) → Python date"""
    return date.fromtimestamp(v) if v else None

def epoch_to_datetime(v):
    return datetime.fromtimestamp(v, tz=timezone.utc) if v else None

def pct_to_decimal(v):
    """yFinance sometimes gives 4.67 meaning 4.67%, we store as 0.0467"""
    return round(v / 100, 6) if v is not None else None

def get_clean_yf_name(name):  
    if name:
        # Collapse multiple spaces
        name = ' '.join(name.split())
        # Remove trailing single letter if it looks like an artifact
        if re.search(r'\s+[A-Z]$', name):
            name = re.sub(r'\s+[A-Z]$', '', name)
    
    return name

# Map: model_class → list of FieldMappings
YF_FIELD_MAPS: dict[type, list[FieldMapping]] = {

    Gfi: [
        FieldMapping("name",        "shortName", get_clean_yf_name),
        FieldMapping("description", "longName",  get_clean_yf_name),
        FieldMapping("ticker_yf",   "symbol"),
    ],

    GfiFundamentals: [
        # Size / valuation
        FieldMapping("shares_outstanding", "sharesOutstanding"),
        FieldMapping("last_price",         "currentPrice"),
        FieldMapping("market_cap",         "marketCap"),

        # Fundamentals
        FieldMapping("pe",                 "trailingPE"),
        FieldMapping("pe_forward",         "forwardPE"),
        FieldMapping("eps",                "epsTrailingTwelveMonths"),
        FieldMapping("eps_forward",        "forwardEps"),
        FieldMapping("book_value_per_share","bookValue"),
        FieldMapping("p_bv",               "priceToBook"),
        FieldMapping("total_revenue",      "totalRevenue"),
        FieldMapping("beta",               "beta"),

        # Dividends
        FieldMapping("dividend_yield",       "dividendYield",    pct_to_decimal),
        FieldMapping("last_dividend_amount", "lastDividendValue"),
        FieldMapping("last_dividend_date",   "lastDividendDate", epoch_to_date),

        # Price range
        FieldMapping("week_52_high", "fiftyTwoWeekHigh"),
        FieldMapping("week_52_low",  "fiftyTwoWeekLow"),
    ],
}









def csv_file_to_list_of_mbank_infos(file_path: Path) -> list[mBankCsvInfo]:
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        mbank_infos = []
        for row in reader:
            mbank_infos.append(mBankCsvInfo(
                isin            =row[0],
                bloomberg_ticker=row[6],
                goole_ticker    =row[7],
                yf_ticker       =row[8]
            ))
        return mbank_infos


def get_yf_info(ticker_yf: str) -> dict | None:
    try: # ----------------------------------
        ticker = yf.Ticker(ticker_yf)

        # # Try to get historical data as a test
        # hist = ticker.history(period="1d")        
        # if hist.empty:
        #     print(f"Warning: No historical data for '{ticker_yf}'")
        #     return None
        
        # Lightweight validity check
        fi = ticker.fast_info
        if not fi or fi.get("lastPrice") is None:
            logger.warning(f"---> No valid fast_info for '{ticker_yf}, skipping...'")
            return None
        else:
            return ticker.info

    except Exception as e: # ----------------------------------
        logger.error(f"---> Error creating ticker for {ticker_yf}: {e}")
        return None  


def mbank_infos_to_yf_infos(mbank_infos: list[mBankCsvInfo]) -> tuple[dict[str, dict], list[str]]:
    all_info = {}
    all_skipped = []
    counter, skipped = 0, 0
    for mbank_info in mbank_infos:
        yf_info = get_yf_info(mbank_info.yf_ticker)
        if yf_info:
            all_info[mbank_info.yf_ticker] = yf_info
            short_info = yf_info.get('shortName', 'N/A')
        else:
            logger.warning(f"---> No YF info for '{mbank_info.yf_ticker}', skipping...")
            short_info = 'N/A'
            skipped += 1
            all_skipped.append(mbank_info.yf_ticker)
        counter += 1
        logger.info(f"Processed/skipped/total/remaining: {counter:3d}/{skipped:3d}/{len(mbank_infos):4d}/{len(mbank_infos) - counter:4d} {mbank_info.yf_ticker}:{short_info}")
        time.sleep(1)  # Be nice to Yahoo API
    return all_info, all_skipped


if __name__ == "__main__":
    mbank_infos = csv_file_to_list_of_mbank_infos(MBANK_CSV_DATA_PATH)
    yf_infos, all_skipped = mbank_infos_to_yf_infos(mbank_infos)
    # Save to JSON
    with open(YF_ALL_INFO_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(yf_infos, f, indent=2)
    with open(YF_ALL_INFO_SKIPPED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(all_skipped, f, indent=2)
    logger.info(f'Saved  : {len(yf_infos)} YF infos to {YF_ALL_INFO_DATA_PATH}')
    logger.info(f'Skipped: {len(all_skipped)} YF skipped infos to {YF_ALL_INFO_SKIPPED_DATA_PATH}')
