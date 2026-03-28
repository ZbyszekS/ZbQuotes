"""
seed.py — Populate the database with initial reference data.

Run with:  python seed.py

This script is IDEMPOTENT — safe to run multiple times.
It will only insert rows that don't already exist.
"""

import sys
import os
import csv

from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from zb_quotes.models.models import Country, Fit, Gfi, CurrencyDetails, Market, QuotedUnit, QuotedUnitConversion, Timeframe, Vendor, Qfi, Vfi



# ── Directiories        ───────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_PROCESSED = PROJECT_ROOT / "resources" / "data" / "processed_data"

print(f"SCRIPT_DIR: {SCRIPT_DIR}")
print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"DATA_PROCESSED: {DATA_PROCESSED}")
# ── Database connection ───────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL") # e.g., "sqlite:////path/to/your/database.db" defined in .env file
print(f"DEBUG: DATABASE_URL = {DATABASE_URL}")
engine = create_engine(DATABASE_URL, echo=False)


# ── Seed data definitions ─────────────────────────────────────────────────────

Fit_DATA_obj = [
    Fit(id=1, name="Cash",      description="Physical or digital cash"),
    Fit(id=2, name="Shares",    description="Equity shares / stocks"),
    Fit(id=3, name="Bonds",     description="Fixed income instruments"),
    Fit(id=4, name="Deposit",   description="Bank deposits"),
    Fit(id=5, name="Forex",     description="Foreign exchange instruments"),
    Fit(id=6, name="Commodity", description="Raw materials and commodities"),
    Fit(id=7, name="ETF",       description="Exchange Traded Funds"),
]

Gfi_DATA_obj = [
    Gfi(id=1, fit_id=1, name="PLN", description="Polish Zloty"),
    Gfi(id=2, fit_id=1, name="USD", description="US Dollar"),
    Gfi(id=3, fit_id=1, name="EUR", description="Euro"),
    Gfi(id=4, fit_id=1, name="GBP", description="British Pound"),
    Gfi(id=5, fit_id=1, name="JPY", description="Japanese Yen"),
    Gfi(id=6, fit_id=1, name="CHF", description="Swiss Franc"),
]
CurrencyDetails_DATA_obj = [
    CurrencyDetails(id=1, gfi_id=1, code="PLN", symbol="zł",  name="Polish Zloty",  decimal_places=2),
    CurrencyDetails(id=2, gfi_id=2, code="USD", symbol="$",   name="US Dollar",     decimal_places=2),
    CurrencyDetails(id=3, gfi_id=3, code="EUR", symbol="€",   name="Euro",          decimal_places=2),
    CurrencyDetails(id=4, gfi_id=4, code="GBP", symbol="£",   name="British Pound", decimal_places=2),
    CurrencyDetails(id=5, gfi_id=5, code="JPY", symbol="¥",   name="Japanese Yen",  decimal_places=0),
    CurrencyDetails(id=6, gfi_id=6, code="CHF", symbol="Fr.", name="Swiss Franc",   decimal_places=2),
]
QuotedUnit_DATA_obj = [
    QuotedUnit(id=1, name="Shares",      description="Stock shares",          symbol="sh"),
    QuotedUnit(id=2, name="Bushel",      description="US Bushel = ~60lbs",    symbol="bu"),
    QuotedUnit(id=3, name="Metric Tonne",description="Metric tonne = 1000kg", symbol="t"),
    QuotedUnit(id=4, name="Gram",        description="SI gram",               symbol="g"),
    QuotedUnit(id=5, name="Ounce",       description="US Troy ounce",         symbol="oz"),
    QuotedUnit(id=6, name="Barrel",      description="US Barrel",             symbol="bbl"),
    QuotedUnit(id=7, name="Cubic foot",  description="US Cubic foot",         symbol="ft³"),
    QuotedUnit(id=8, name="Cubic meter", description="SI Cubic meter",        symbol="m³"),
    QuotedUnit(id=9, name="Bushel_Wheat",description="US Bushel of Wheat",    symbol="bu"),
]
QuotedUnitConversion_DATA_obj = [
    QuotedUnitConversion(id=1, quoted_unit_from_id=5, quoted_unit_to_id=4, conversion_factor=28.3495),
    QuotedUnitConversion(id=2, quoted_unit_from_id=7, quoted_unit_to_id=8, conversion_factor=0.0283168),
    QuotedUnitConversion(id=3, quoted_unit_from_id=9, quoted_unit_to_id=3, conversion_factor=0.0272155),
]
Market_DATA_obj = [
    Market(id=1, currency_id=1, mic="XWAR", name="Warsaw Stock Exchange",    description="Warsaw Stock Exchange", abbreviation="WSE"),
    Market(id=2, currency_id=2, mic="XNYS", name="New York Stock Exchange",  description="New York Stock Exchange", abbreviation="NYSE"),
    Market(id=3, currency_id=2, mic="XNAS", name="NASDAQ Stock Market",      description="NASDAQ Stock Market", abbreviation="NASDAQ"),
    Market(id=4, currency_id=3, mic="XETR", name="Frankfurt Stock Exchange", description="Frankfurt Stock Exchange (Xetra)", abbreviation="FSE"),
    Market(id=5, currency_id=4, mic="XLON", name="London Stock Exchange",    description="London Stock Exchange", abbreviation="LSE"),
    Market(id=6, currency_id=4, mic="XAMS", name="Amsterdam Stock Exchange", description="Amsterdam Stock Exchange", abbreviation="ASE"),
    Market(id=7, currency_id=4, mic="XBRU", name="Brussels Stock Exchange",  description="Brussels Stock Exchange", abbreviation="BSE"),
    Market(id=8, currency_id=4, mic="XMAD", name="Madrid Stock Exchange",    description="Madrid Stock Exchange", abbreviation="MSE"),
    Market(id=9, currency_id=4, mic="XPAR", name="Paris Stock Exchange",     description="Paris Stock Exchange", abbreviation="PAR"),
    Market(id=10,currency_id=2, mic="FX",   name="Foreign Exchange (OTC)",   description="FOREX - Foreign Exchange (OTC)", abbreviation="FX"),

    
    
]
TimeFrame_DATA_obj = [
    Timeframe(id=1, code="1m",   seconds=60,     is_intraday=True,  is_aggregatable=True,  name="1 Minute"),
    Timeframe(id=2, code="1h",   seconds=3600,   is_intraday=True,  is_aggregatable=True,  name="1 Hour"),
    Timeframe(id=3, code="1d",   seconds=86400,  is_intraday=False, is_aggregatable=False, name="Daily"),
    Timeframe(id=4, code="1w",   seconds=7*86400,is_intraday=False, is_aggregatable=False, name="Weekly"),
    Timeframe(id=5, code="1M",   seconds=None,   is_intraday=False, is_aggregatable=False, name="Monthly"),
]

Vendor_DATA_obj = [
    Vendor(id=1, name="Yahoo Finance", description="Yahoo Finance", allowed_time_series="1m,1h,1d,1w,1M"),
]

Qfi_DATA_obj = [
    Qfi(id = 1, gfi_id=3, market_id=10, currency_id=2, quoted_unit_id=1,
        name="EUR/USD", description="EUR/USD - Euro to US Dollar", quoted_amount=1),
    Qfi(id = 2, gfi_id=2, market_id=10, currency_id=1, quoted_unit_id=1,
        name="USD/PLN", description="USD/PLN - US Dollar to Polish Zloty", quoted_amount=1),
    Qfi(id = 3, gfi_id=3, market_id=10, currency_id=1, quoted_unit_id=1,
        name="EUR/PLN", description="EUR/PLN - Euro to Polish Zloty", quoted_amount=1),
]

Vfi_DATA_obj = [
    Vfi(id=1, qfi_id=1, vendor_id=1, vendor_ticker="EURUSD=X", name="EURUSD - Yahoo Finance", description="FOREX EURUSD from Yahoo Finance"),
    Vfi(id=2, qfi_id=2, vendor_id=1, vendor_ticker="USDPLN=X", name="USDPLN - Yahoo Finance", description="FOREX USDPLN from Yahoo Finance"),
    Vfi(id=3, qfi_id=3, vendor_id=1, vendor_ticker="EURPLN=X", name="EURPLN - Yahoo Finance", description="FOREX EURPLN from Yahoo Finance"),
]

def read_country_data()-> list[Country]:
    # Read country data from CSV file
    country_data = []
    try:
        with open(DATA_PROCESSED / "country.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                obj = Country()
                
                obj.id = row['id']
                obj.iso_code_2 = row['iso_code_2']
                obj.name = row['name']
                obj.description = row['description']
                obj.region = row['region']
                obj.subregion = row['subregion']

                country_data.append(obj)
    except:
        print("---> !!! Error reading country data from CSV file")
        sys.exit(1)
    return country_data

Country_DATA_obj = read_country_data()
# ── Helper: upsert-style insert ───────────────────────────────────────────────

# for data in dictionary format
def seed_table(session: Session, model, data: list[dict], label: str):
    """
    Insert rows that don't already exist (matched by primary key 'id').
    Prints a summary of what was inserted vs. skipped.
    """
    inserted = 0
    skipped  = 0

    for row in data:
        existing = session.get(model, row["id"])
        if existing is None:
            session.add(model(**row))
            inserted += 1
        else:
            skipped += 1

    print(f"  {label:<20} inserted: {inserted:>3}   skipped (already exist): {skipped:>3}")

# for data in object format
def seed_table_obj(session: Session, objects: list, label: str):
    """
    Insert rows that don't already exist (matched by primary key 'id').
    Prints a summary of what was inserted vs. skipped.
    """
    inserted = 0
    skipped  = 0

    for obj in objects:
        existing = session.get(type(obj), obj.id)
        if existing is None:
            session.add(obj)
            inserted += 1
        else:
            skipped += 1

    print(f"  {label:<22} inserted: {inserted:>3}   skipped (already exist): {skipped:>3}")


# ── Main seed function ────────────────────────────────────────────────────────

def run_seed():
    print("\n=== Seeding database ===\n")

    with Session(engine) as session:
        # seed_table(session, Fit, FIT_DATA, "Financial Inst. Types")
        seed_table_obj(session, Fit_DATA_obj, "Financial Inst. Types")
        seed_table_obj(session, Gfi_DATA_obj, "Gfi")
        seed_table_obj(session, CurrencyDetails_DATA_obj, "Currency Details")
        seed_table_obj(session, QuotedUnit_DATA_obj, "Quoted Unit")
        seed_table_obj(session, QuotedUnitConversion_DATA_obj, "Quoted Unit Conversion")
        seed_table_obj(session, Market_DATA_obj, "Market")
        seed_table_obj(session, TimeFrame_DATA_obj, "Time Frame")
        seed_table_obj(session, Country_DATA_obj, "Country")
        seed_table_obj(session, Vendor_DATA_obj, "Vendor")
        seed_table_obj(session, Qfi_DATA_obj, "Qfi")
        seed_table_obj(session, Vfi_DATA_obj, "Vfi")

        session.commit()

    print("\n=== Done ===\n")


if __name__ == "__main__":
    run_seed()