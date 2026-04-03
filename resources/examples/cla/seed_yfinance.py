"""
seed_yfinance.py — Import yFinance JSON data into the database.

Run with:  python seed_yfinance.py <path_to_json_directory>

This script processes yFinance JSON files and populates:
- Country, Sector, Industry (reference data)
- Gfi (global financial instrument)
- GfiFundamentals (financial metrics)
- Market (if new markets discovered)
- Qfi (quoted instrument linking Gfi to Market)

The script is IDEMPOTENT — safe to run multiple times.
It will skip existing entries and only insert new ones.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from zb_quotes.models.models import (
    Fit, Gfi, Country, Sector, Industry, Market, 
    CurrencyDetails, QuotedUnit, Qfi, GfiFundamentals
)

# ── Database connection ───────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)


# ── Market suffix mapping ─────────────────────────────────────────────────────
# Maps yFinance suffixes to your Market MIC codes
MARKET_SUFFIX_TO_MIC = {
    'WA': 'XWAR',  # Warsaw
    'US': 'XNYS',  # New York (or could be NASDAQ)
    'DE': 'XETR',  # Frankfurt (Xetra)
    'L': 'XLON',   # London
    # Add more as needed
}

# Default market if suffix not recognized
DEFAULT_MARKET_MIC = 'XWAR'


# ── Helper functions ──────────────────────────────────────────────────────────

def parse_ticker_symbol(symbol: str) -> tuple[str, str, str]:
    """
    Parse yFinance symbol into ticker, suffix, and MIC.
    
    Examples:
        '11B.WA' → ('11B', 'WA', 'XWAR')
        'AAPL' → ('AAPL', '', 'XNYS')  # default to NYSE for US stocks
    
    Returns:
        (ticker, suffix, mic_code)
    """
    if '.' in symbol:
        ticker, suffix = symbol.rsplit('.', 1)
        mic = MARKET_SUFFIX_TO_MIC.get(suffix, DEFAULT_MARKET_MIC)
        return ticker, suffix, mic
    else:
        # No suffix - assume US market
        return symbol, '', 'XNYS'


def safe_decimal(value: Any, default: Optional[Decimal] = None) -> Optional[Decimal]:
    """Safely convert value to Decimal, handling None and invalid values."""
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """Safely convert value to int, handling None and invalid values."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_date(timestamp: Any) -> Optional[datetime]:
    """Convert epoch timestamp to datetime."""
    if timestamp is None:
        return None
    try:
        return datetime.fromtimestamp(int(timestamp))
    except (ValueError, TypeError, OSError):
        return None


# ── Lookup/Create helper functions ────────────────────────────────────────────

def get_or_create_country(session: Session, country_name: str) -> Country:
    """Get existing country or create new one."""
    if not country_name:
        country_name = "Unknown"
    
    # Try to find existing
    stmt = select(Country).where(Country.name == country_name)
    country = session.scalars(stmt).first()
    
    if country:
        return country
    
    # Create new - generate a simple ISO code if not in standard list
    # In production, you'd want a proper ISO code mapping
    iso_code = country_name[:2].upper()
    
    country = Country(
        iso_code_2=iso_code,
        name=country_name,
        description=f"Auto-created from yFinance data"
    )
    session.add(country)
    session.flush()  # Get the ID
    return country


def get_or_create_sector(session: Session, sector_name: str) -> Sector:
    """Get existing sector or create new one."""
    if not sector_name:
        sector_name = "Unknown"
    
    stmt = select(Sector).where(Sector.name == sector_name)
    sector = session.scalars(stmt).first()
    
    if sector:
        return sector
    
    sector = Sector(
        name=sector_name,
        description=f"Auto-created from yFinance data"
    )
    session.add(sector)
    session.flush()
    return sector


def get_or_create_industry(session: Session, industry_name: str) -> Industry:
    """Get existing industry or create new one."""
    if not industry_name:
        industry_name = "Unknown"
    
    stmt = select(Industry).where(Industry.name == industry_name)
    industry = session.scalars(stmt).first()
    
    if industry:
        return industry
    
    industry = Industry(
        name=industry_name,
        description=f"Auto-created from yFinance data"
    )
    session.add(industry)
    session.flush()
    return industry


def get_market_by_mic(session: Session, mic: str) -> Optional[Market]:
    """Get market by MIC code."""
    stmt = select(Market).where(Market.mic == mic)
    return session.scalars(stmt).first()


def get_currency_gfi_by_code(session: Session, currency_code: str) -> Optional[Gfi]:
    """Get currency Gfi by currency code (e.g., 'PLN', 'USD')."""
    stmt = (
        select(Gfi)
        .join(CurrencyDetails)
        .where(CurrencyDetails.code == currency_code)
    )
    return session.scalars(stmt).first()


def get_shares_quoted_unit(session: Session) -> Optional[QuotedUnit]:
    """Get the 'Shares' quoted unit."""
    stmt = select(QuotedUnit).where(QuotedUnit.name == "Shares")
    return session.scalars(stmt).first()


def get_fit_by_name(session: Session, fit_name: str) -> Optional[Fit]:
    """Get Financial Instrument Type by name."""
    stmt = select(Fit).where(Fit.name == fit_name)
    return session.scalars(stmt).first()


# ── Main import function ──────────────────────────────────────────────────────

def import_yfinance_data(session: Session, symbol: str, data: Dict[str, Any]) -> dict:
    """
    Import a single yFinance JSON entry into the database.
    
    Returns:
        Dict with import statistics
    """
    stats = {
        'gfi_created': False,
        'gfi_updated': False,
        'fundamentals_created': False,
        'fundamentals_updated': False,
        'qfi_created': False,
        'country_created': False,
        'sector_created': False,
        'industry_created': False,
    }
    
    # Parse symbol
    ticker, suffix, mic = parse_ticker_symbol(symbol)
    
    # Get or create reference data
    country = get_or_create_country(session, data.get('country', 'Unknown'))
    if country and not session.query(Country).filter_by(id=country.id).first():
        stats['country_created'] = True
    
    sector = get_or_create_sector(session, data.get('sector', 'Unknown'))
    if sector and not session.query(Sector).filter_by(id=sector.id).first():
        stats['sector_created'] = True
    
    industry = get_or_create_industry(session, data.get('industryDisp', 'Unknown'))
    if industry and not session.query(Industry).filter_by(id=industry.id).first():
        stats['industry_created'] = True
    
    # Get Fit (should be 'Shares' for stocks)
    fit = get_fit_by_name(session, 'Shares')
    if not fit:
        raise ValueError("Fit 'Shares' not found. Run seed.py first!")
    
    # Check if Gfi already exists (by ticker_yf or name)
    stmt = select(Gfi).where(Gfi.ticker_yf == symbol)
    gfi = session.scalars(stmt).first()
    
    if not gfi:
        # Create new Gfi
        gfi = Gfi(
            fit_id=fit.id,
            sector_id=sector.id if sector else None,
            industry_id=industry.id if industry else None,
            country_id=country.id if country else None,
            name=data.get('shortName', ticker),
            description=data.get('longBusinessSummary', '')[:255] if data.get('longBusinessSummary') else None,
            ticker_yf=symbol,
        )
        session.add(gfi)
        session.flush()
        stats['gfi_created'] = True
    else:
        # Update existing Gfi if data has changed
        gfi.sector_id = sector.id if sector else gfi.sector_id
        gfi.industry_id = industry.id if industry else gfi.industry_id
        gfi.country_id = country.id if country else gfi.country_id
        gfi.description = data.get('longBusinessSummary', '')[:255] if data.get('longBusinessSummary') else gfi.description
        stats['gfi_updated'] = True
    
    # Create or update GfiFundamentals
    stmt = select(GfiFundamentals).where(GfiFundamentals.gfi_id == gfi.id)
    fundamentals = session.scalars(stmt).first()
    
    if not fundamentals:
        fundamentals = GfiFundamentals(
            gfi_id=gfi.id,
            updated_at=datetime.now(),
            source_vendor='yfinance'
        )
        session.add(fundamentals)
        stats['fundamentals_created'] = True
    else:
        stats['fundamentals_updated'] = True
    
    # Populate fundamentals fields
    fundamentals.shares_outstanding = safe_int(data.get('sharesOutstanding'))
    fundamentals.last_price = safe_decimal(data.get('currentPrice'))
    fundamentals.market_cap = safe_decimal(data.get('marketCap'))
    fundamentals.pe = safe_decimal(data.get('trailingPE'))
    fundamentals.pe_forward = safe_decimal(data.get('forwardPE'))
    fundamentals.eps = safe_decimal(data.get('trailingEps'))
    fundamentals.eps_forward = safe_decimal(data.get('forwardEps'))
    fundamentals.book_value_per_share = safe_decimal(data.get('bookValue'))
    fundamentals.p_bv = safe_decimal(data.get('priceToBook'))
    fundamentals.total_revenue = safe_decimal(data.get('totalRevenue'))
    fundamentals.beta = safe_decimal(data.get('beta'))
    fundamentals.dividend_yield = safe_decimal(data.get('dividendYield'))
    fundamentals.last_dividend_amount = safe_decimal(data.get('trailingAnnualDividendRate'))
    fundamentals.week_52_high = safe_decimal(data.get('fiftyTwoWeekHigh'))
    fundamentals.week_52_low = safe_decimal(data.get('fiftyTwoWeekLow'))
    fundamentals.updated_at = datetime.now()
    
    # Get Market
    market = get_market_by_mic(session, mic)
    if not market:
        print(f"  ⚠️  Warning: Market with MIC '{mic}' not found for {symbol}. Skipping Qfi creation.")
        return stats
    
    # Get currency Gfi
    currency_code = data.get('currency', 'USD')
    currency_gfi = get_currency_gfi_by_code(session, currency_code)
    if not currency_gfi:
        print(f"  ⚠️  Warning: Currency '{currency_code}' not found for {symbol}. Skipping Qfi creation.")
        return stats
    
    # Get QuotedUnit (Shares)
    quoted_unit = get_shares_quoted_unit(session)
    if not quoted_unit:
        print(f"  ⚠️  Warning: QuotedUnit 'Shares' not found. Run seed.py first!")
        return stats
    
    # Check if Qfi already exists
    stmt = (
        select(Qfi)
        .where(Qfi.gfi_id == gfi.id)
        .where(Qfi.market_id == market.id)
    )
    qfi = session.scalars(stmt).first()
    
    if not qfi:
        # Create Qfi
        qfi = Qfi(
            gfi_id=gfi.id,
            market_id=market.id,
            currency_id=currency_gfi.id,
            quoted_unit_id=quoted_unit.id,
            name=f"{ticker} on {market.abbreviation}",
            description=f"{data.get('longName', ticker)} quoted on {market.name}",
            quoted_amount=1  # 1 share
        )
        session.add(qfi)
        stats['qfi_created'] = True
    
    return stats


# ── Main execution ────────────────────────────────────────────────────────────

def process_json_files(json_directory: str):
    """Process all JSON files in the given directory."""
    json_path = Path(json_directory)
    
    if not json_path.exists():
        print(f"❌ Error: Directory '{json_directory}' not found.")
        sys.exit(1)
    
    json_files = list(json_path.glob('*.json'))
    
    if not json_files:
        print(f"❌ Error: No JSON files found in '{json_directory}'.")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"  Processing {len(json_files)} JSON file(s) from: {json_directory}")
    print(f"{'='*60}\n")
    
    total_stats = {
        'files_processed': 0,
        'gfi_created': 0,
        'gfi_updated': 0,
        'fundamentals_created': 0,
        'fundamentals_updated': 0,
        'qfi_created': 0,
        'errors': 0,
    }
    
    with Session(engine) as session:
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data_dict = json.load(f)
                
                # Process each symbol in the file
                for symbol, data in data_dict.items():
                    print(f"  Processing: {symbol:<15} ", end='')
                    
                    try:
                        stats = import_yfinance_data(session, symbol, data)
                        
                        # Update totals
                        total_stats['gfi_created'] += 1 if stats['gfi_created'] else 0
                        total_stats['gfi_updated'] += 1 if stats['gfi_updated'] else 0
                        total_stats['fundamentals_created'] += 1 if stats['fundamentals_created'] else 0
                        total_stats['fundamentals_updated'] += 1 if stats['fundamentals_updated'] else 0
                        total_stats['qfi_created'] += 1 if stats['qfi_created'] else 0
                        
                        # Show status
                        status = []
                        if stats['gfi_created']:
                            status.append('GFI✓')
                        if stats['fundamentals_created']:
                            status.append('FUND✓')
                        if stats['qfi_created']:
                            status.append('QFI✓')
                        if not status:
                            status.append('updated')
                        
                        print(f"  [{', '.join(status)}]")
                        
                    except Exception as e:
                        print(f"  ❌ Error: {e}")
                        total_stats['errors'] += 1
                
                total_stats['files_processed'] += 1
                
            except json.JSONDecodeError as e:
                print(f"  ❌ Error reading {json_file.name}: {e}")
                total_stats['errors'] += 1
            except Exception as e:
                print(f"  ❌ Error processing {json_file.name}: {e}")
                total_stats['errors'] += 1
        
        # Commit all changes
        session.commit()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"  IMPORT SUMMARY")
    print(f"{'='*60}")
    print(f"  Files processed:        {total_stats['files_processed']}")
    print(f"  GFIs created:           {total_stats['gfi_created']}")
    print(f"  GFIs updated:           {total_stats['gfi_updated']}")
    print(f"  Fundamentals created:   {total_stats['fundamentals_created']}")
    print(f"  Fundamentals updated:   {total_stats['fundamentals_updated']}")
    print(f"  QFIs created:           {total_stats['qfi_created']}")
    print(f"  Errors:                 {total_stats['errors']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed_yfinance.py <path_to_json_directory>")
        print("Example: python seed_yfinance.py ./data/yfinance")
        sys.exit(1)
    
    json_directory = sys.argv[1]
    process_json_files(json_directory)
