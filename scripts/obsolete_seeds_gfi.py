import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

import logging
import csv
import re
from dataclasses import dataclass, fields
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
import yfinance as yf
from zb_quotes.models.models import Gfi, GfiFundamentals, Qfi, Market, Sector, Industry, Country

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GFI_CSV_FILE = "../resources/data/mbank_instruments.csv"

# ── Database connection ───────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL") # e.g., "sqlite:////path/to/your/database.db" defined in .env file
print(f"DEBUG: DATABASE_URL = {DATABASE_URL}")
engine = create_engine(DATABASE_URL, echo=False)


@dataclass
class MBankInstrument:
    isin: str
    name_composite: str
    first_part_of_name: str
    short_name: str
    long_name: str
    mic: str
    currency: str
    instrument_type: str
    ticker_bloomberg: str
    ticker_google: str
    ticker_yf: str  


@dataclass
class YfInfo:
    short_name: str
    long_name: str
    sector_name: str
    sector_key: str
    industry_name: str
    industry_key: str
    # gfi fundamentals
    # Size / valuation
    shares_outstanding: int
    last_price: float
    market_cap: float

    # Fundamentals
    beta: float
    country: str
    currency: str
    dividend_yield: float
    dividend_amount: float
    dividend_date: str
    total_revenue: float
    

def csv_row_2_mbank_instrument(row: list[str]) -> MBankInstrument:
    isin = row[0]
    name_composite = row[1]
    first_part_of_name = name_composite.split()[0]
    idx_of_second_part_of_name = name_composite.find(first_part_of_name, 1)
    short_name = name_composite[idx_of_second_part_of_name:]
    long_name = name_composite[0:idx_of_second_part_of_name].strip()
    mic = row[2]
    currency = row[3]
    instrument_type = row[4]
    ticker_bloomberg = row[5]
    ticker_google = row[6]
    ticker_yf = row[7]
    return MBankInstrument(
        isin=isin,
        name_composite=name_composite,
        first_part_of_name=first_part_of_name,
        short_name=short_name,
        long_name=long_name,
        mic=mic,
        currency=currency,
        instrument_type=instrument_type,
        ticker_bloomberg=ticker_bloomberg,
        ticker_google=ticker_google,
        ticker_yf=ticker_yf
    )

def csv_file_to_list_of_mbank_instruments(file_path: str, type_in: list[str]) -> list[MBankInstrument]:
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        mbank_instruments = []
        for row in reader:
            mbank_instrument = csv_row_2_mbank_instrument(row)
            if mbank_instrument.instrument_type in type_in:
                mbank_instruments.append(mbank_instrument)
        return mbank_instruments


def get_fit_id(instrument_type: str) -> int:
    """
    Based on values inserted by seeds_fit.py script
    Returns the FIT ID for the given instrument type.
    If the instrument type is not found, returns None.
    """
    if instrument_type == "STOCK":
        return 2
    elif instrument_type == "BOND":
        return 3
    elif instrument_type == "ETF":
        return 7
    elif instrument_type == "CURRENCY":
        return 1
    elif instrument_type == "COMMODITY":
        return 6
    else:
        return None



def update_gfi(session: Session, existing_gfi: Gfi, new_gfi: Gfi):
    """
    Updates the existing GFI with the new GFI data.
    """
    existing_gfi.fit_id = new_gfi.fit_id
    existing_gfi.isin = new_gfi.isin
    existing_gfi.name = new_gfi.name
    existing_gfi.description = new_gfi.description
    existing_gfi.ticker_bl = new_gfi.ticker_bl
    existing_gfi.ticker_go = new_gfi.ticker_go
    existing_gfi.ticker_yf = new_gfi.ticker_yf


def find_gfi_by_isin(session: Session, isin: str) -> Gfi:
    """
    Finds a GFI by ISIN.
    Returns the GFI if found, None otherwise.
    """
    stmt = select(Gfi).where(Gfi.isin == isin)
    return session.execute(stmt).scalars().first()

def process_yf_data_sector(yf_data: YfInfo, session: Session) -> int:
    """
    Processes the YF data and returns the sector ID.
    """
    name = yf_data.sector_key
    description = yf_data.sector_name
    stmt = select(Sector).where(Sector.name == name)
    sector = session.execute(stmt).scalars().first()
    if sector is None:
        sector = Sector(name=name, description=description)
        session.add(sector)
        session.flush()
    return sector.id

def process_yf_data_industry(yf_data: YfInfo, session: Session) -> int:
    """
    Processes the YF data and returns the industry ID.
    """
    name = yf_data.industry_key
    description = yf_data.industry_name
    stmt = select(Industry).where(Industry.name == name)
    industry = session.execute(stmt).scalars().first()
    if industry is None:
        industry = Industry(name=name, description=description)
        session.add(industry)
        session.flush()
    return industry.id

def process_yf_data_country(yf_data: YfInfo, session: Session) -> int:
    """
    Processes the YF data and returns the country ID.
    """
    name = yf_data.country
    stmt = select(Country).where(Country.name == name)
    country = session.execute(stmt).scalars().first()
    if country is None:
        return None
    return country.id

def seed_gfi(session: Session, mbank_instrument: MBankInstrument, yf_data: YfInfo):
    """
    Single insert or update or skip to Gfi table
    
    Args:
        session: SQLAlchemy session
        bank_instrument: MBankInstrument object
        
    Returns:
        None
    
    Outcome:
        possible one row in Gfi table
    """
    r = None
    fit_id = get_fit_id(mbank_instrument.instrument_type)
    sector_id = process_yf_data_sector(yf_data, session)
    industry_id = process_yf_data_industry(yf_data, session)
    country_id = process_yf_data_country(yf_data, session)
    if country_id is None:
        logger.warning(f"Country not found for instrument isin: {mbank_instrument.isin}, name: {yf_data.short_name}, skipping...")
        return None
    if fit_id is None:
        new_gfi = Gfi(
            fit_id          =fit_id,
            isin            =mbank_instrument.isin, 
            name            =yf_data.short_name, 
            description     =yf_data.long_name,
            ticker_bloomberg=mbank_instrument.ticker_bloomberg,
            ticker_google   =mbank_instrument.ticker_google,
            ticker_yf       =mbank_instrument.ticker_yf,
            sector_id       =sector_id,
            industry_id     =industry_id,
            country_id      =country_id,
        )
        existing_gfi = find_gfi_by_isin(session, mbank_instrument.isin)
        if existing_gfi:
            update_gfi(session, existing_gfi, new_gfi)
            logger.debug(f"GFI {new_gfi.name} with ISIN {new_gfi.isin} already exists")
            r = existing_gfi
        else:
            session.add(new_gfi)
            logger.debug(f"GFI {new_gfi.name} with ISIN {new_gfi.isin} added")
            r = new_gfi
    else:
        logger.debug(f"No FIT ID found for {mbank_instrument.short_name} instrument type: {mbank_instrument.instrument_type}")
    return r


def seed_gfi_fundamentals(session, gfi: Gfi, yf_data: YfInfo):
    ngf = GfiFundamentals()
    ngf.gfi_id = gfi.id
    ngf.shares_outstanding = yf_data.shares_outstanding
    ngf.last_price = yf_data.last_price
    ngf.market_cap = yf_data.market_cap
    ngf.pe = yf_data.pe_ratio
    ngf.eps = yf_data.eps
    ngf.book_value_per_share = yf_data.book_value_per_share
    ngf.beta = yf_data.beta
    ngf.total_revenue = yf_data.total_revenue
    ngf.dividend_yield = yf_data.dividend_yield
    ngf.last_dividend_amount = yf_data.last_dividend_amount
    ngf.last_dividend_date = yf_data.last_dividend_date
    ngf.week_52_high = yf_data.week_52_high
    ngf.week_52_low = yf_data.week_52_low
    
    ngf = GfiFundamentals(
        gfi_id              =gfi.id,

        shares_outstanding  =yf_data.shares_outstanding,
        last_price          =yf_data.last_price,
        market_cap          =yf_data.market_cap,

        pe_ratio            =yf_data.pe_ratio,
        eps                 =yf_data.eps,
        book_value_per_share=yf_data.book_value_per_share,
        beta=yf_data.beta,
        total_revenue=yf_data.total_revenue,
        dividend_yield=yf_data.dividend_yield,
        last_dividend_amount=yf_data.last_dividend_amount,
        last_dividend_date=yf_data.last_dividend_date,
        week_52_high=yf_data.week_52_high,
        week_52_low=yf_data.week_52_low,
    )
    existing_gfi_fundamentals = find_gfi_fundamentals_by_gfi_id(session, gfi.id)
    if existing_gfi_fundamentals:
        update_gfi_fundamentals(session, existing_gfi_fundamentals, ngf)
        logger.debug(f"GFI Fundamentals {ngf.gfi_id} already exists")
    else:
        session.add(ngf)
        logger.debug(f"GFI Fundamentals {ngf.gfi_id} added")

def get_market_id(session, mic):
    stmt = select(Market).where(Market.mic == mic)
    result = session.execute(stmt)
    market = result.scalar_one_or_none()
    return market.id if market else None

def get_currency_id(session, currency):
    stmt = select(Gfi).where(Gfi.name == currency)
    result = session.execute(stmt)
    currency = result.scalar_one_or_none()
    return currency.id if currency else None

def update_qfi(session, existing_qfi: Qfi, new_qfi: Qfi):
    # existing_qfi.gfi_id = new_qfi.gfi_id # assuming the same gfi
    existing_qfi.market_id = new_qfi.market_id
    existing_qfi.currency_id = new_qfi.currency_id
    existing_qfi.quoted_unit_id = new_qfi.quoted_unit_id
    # existing_qfi.name = new_qfi.name # assuming the same name
    existing_qfi.description = new_qfi.description
    existing_qfi.quoted_amount = new_qfi.quoted_amount
    session.add(existing_qfi)
    logger.debug(f"QFI {existing_qfi.name} updated")

def get_existing_qfi_4_gfi_id__name(session, new_qfi: Qfi) -> Qfi | None:
    stmt = select(Qfi).where(Qfi.gfi_id == new_qfi.gfi_id, Qfi.name == new_qfi.name)
    result = session.execute(stmt)
    return result.scalar_one_or_none()


def seed_qfi(session, bank_instrument: MBankInstrument, gfi: Gfi) -> Qfi | None:
    """
    Seeds the Qfi table with the given bank instrument.
    
    Args:
        session: SQLAlchemy session
        bank_instrument: MBankInstrument object
        
    Returns:
        None
    
    Outcome:
        possible one row in Qfi table
    """
    r = None
    market_id = get_market_id(session, bank_instrument.mic)
    if market_id is None:
        logger.warning(f"Market with MIC {bank_instrument.mic} not found")
        return r

    currency_id = get_currency_id(session, bank_instrument.currency)
    if currency_id is None:
        logger.warning(f"Currency {bank_instrument.currency} not found")
        return r
    
    quoted_unit_id = 1  # from seeds.py
    quoted_amount = 1
    new_qfi = Qfi(
        gfi_id          =gfi.id,
        market_id       =market_id,
        currency_id     =currency_id,
        quoted_unit_id  =quoted_unit_id,
        name            =bank_instrument.short_name + " " + bank_instrument.mic,
        description     =bank_instrument.long_name + " " + bank_instrument.mic,
        quoted_amount   =quoted_amount,
    )
    existing_qfi = get_existing_qfi_4_gfi_id__name(session, new_qfi)
    if existing_qfi:
        logger.debug(f"QFI {existing_qfi.name} already exists")
        update_qfi(session, existing_qfi, new_qfi)
        return existing_qfi
    else:
        logger.debug(f"QFI {new_qfi.name} not found, creating new one")
        session.add(new_qfi)
        return new_qfi

def get_clean_name(name):   
    if name:
        # Collapse multiple spaces
        name = ' '.join(name.split())
        # Remove trailing single letter if it looks like an artifact
        if re.search(r'\s+[A-Z]$', name):
            name = re.sub(r'\s+[A-Z]$', '', name)
    
    return name

def get_yf_info(ticker_yf: str) -> dict | None:
    try: # ----------------------------------
        ticker = yf.Ticker(ticker_yf)

        # Try to get historical data as a test
        hist = ticker.history(period="1d")
        
        if hist.empty:
            print(f"Warning: No historical data for '{ticker_yf}'")
            return None
        
        # Get info
        info = ticker.info
        
        # Check if we have minimum required data
        required_keys = ['symbol', 'longName']
        for key in required_keys:
            if key not in info or info[key] is None:
                logger.warning(f"Missing required field '{key}' for '{ticker_yf}'")
                return None
        
        return info
    except Exception as e: # ----------------------------------
        logger.error(f"Error creating ticker for {ticker_yf}: {e}")
        return None    
    



    return info



def get_null_fields(obj):
    """Return list of field names that are None using dataclass introspection"""
    return [field.name for field in fields(obj) if getattr(obj, field.name) is None]

# Usage
# null_fields = get_null_fields(yf_info)
# print(null_fields)


def get_yf_data(yf_info: dict) -> dict:
    r = YfInfo(
        short_name=    get_clean_name(yf_info.get("shortName")),
        long_name=     get_clean_name(yf_info.get("longName")),
        sector_name=   yf_info.get("sector"),
        sector_key=    yf_info.get("sectorKey"),
        industry_name= yf_info.get("industry"),
        industry_key=  yf_info.get("industryKey"),

        beta=          yf_info.get("beta"),
        country=       yf_info.get("country"),
        currency=      yf_info.get("currency"),

        dividend_yield= yf_info.get("dividendYield"),
        dividend_amount= yf_info.get("dividendRate"),
        dividend_date=  yf_info.get("lastDividendDate"),

        total_revenue= yf_info.get("totalRevenue"),
        shares_outstanding= yf_info.get("sharesOutstanding"),
        last_price= yf_info.get("currentPrice"),
        market_cap= yf_info.get("marketCap"),
        
        exchange=      yf_info.get("fullExchangeName"),
    )
    
    null_fields = get_null_fields(r)
    if null_fields:
        logger.warning(f"Null fields in YfInfo: {null_fields}")
    
    return r, null_fields

def main():
    count_skipped, count_processed = 0, 0
    mbank_instruments = csv_file_to_list_of_mbank_instruments(GFI_CSV_FILE, ["STOCK"])
    with Session(engine) as session:
        for mbank_instrument in mbank_instruments:
            # --- process yFinance data ---
            yf_info = get_yf_info(mbank_instrument.ticker_yf)
            if yf_info is None:
                logger.warning(f"YF info not found for {mbank_instrument.ticker_yf}")
                continue
            yf_data, null_fields = get_yf_data(yf_info)
            # logger.info(f"YF data for {mbank_instrument.ticker_yf}: {yf_data}")
            # --- process Gfi ----
            gfi = seed_gfi(session, mbank_instrument, yf_data)
            if gfi is None:
                logger.warning(f"--> Instrument nb: {count_processed + 1}. {mbank_instrument.short_name} - skipping...")
                count_skipped += 1
                continue
            qfi = seed_qfi(session, mbank_instrument)
            count_processed += 1

            
        session.commit()
        logger.info(f"Processed {count_processed} instruments, skipped {count_skipped}")

if __name__ == "__main__":
    main()
