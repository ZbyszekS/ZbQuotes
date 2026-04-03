# yFinance Data Import Guide

This guide explains how to import yFinance data into your ZbQuotes database.

## Overview

The import process consists of three main steps:

1. **Prepare** - Ensure your yFinance JSON files are properly formatted
2. **Validate** - Check for data quality issues before importing
3. **Import** - Load data into the database

## Prerequisites

Before importing yFinance data, you **must** run the base seed script first:

```bash
python seed.py
```

This creates the foundational reference data:
- Financial Instrument Types (Fit) - including "Shares"
- Currencies (Gfi + CurrencyDetails) - PLN, USD, EUR, GBP, JPY, CHF
- Markets - Warsaw (XWAR), NYSE (XNYS), Frankfurt (XETR), London (XLON)
- Quoted Units - Shares, etc.

## Data Flow

```
yFinance JSON → Validation → Database Import
     ↓              ↓              ↓
 stocks.json → validate → seed_yfinance.py
                  ↓              ↓
              Check for    Creates/Updates:
              issues       - Gfi (instruments)
                          - GfiFundamentals
                          - Qfi (quoted instruments)
                          - Country/Sector/Industry
```

## Expected JSON Format

Your JSON file should be a dictionary where:
- **Keys** = yFinance symbols (e.g., "11B.WA", "AAPL")
- **Values** = yFinance data objects

### Symbol Format

The symbol format determines the market:

| Format | Example | Market | MIC Code |
|--------|---------|--------|----------|
| `XXX.WA` | `11B.WA` | Warsaw | XWAR |
| `XXX.DE` | `SAP.DE` | Frankfurt | XETR |
| `XXX.L` | `BP.L` | London | XLON |
| `XXX` | `AAPL` | NYSE (default) | XNYS |

To add more markets, edit `MARKET_SUFFIX_TO_MIC` in `seed_yfinance.py`.

### Required Fields

Minimum fields needed for import:
- `symbol` - The ticker symbol
- `currency` - Trading currency (PLN, USD, EUR, etc.)

### Recommended Fields

For best data quality:
- `shortName` - Short company name
- `longName` - Full company name
- `sector` - Business sector
- `industryDisp` - Industry classification
- `country` - Country of incorporation
- `sharesOutstanding` - Number of shares
- `currentPrice` - Current stock price
- `marketCap` - Market capitalization

### Fundamentals Fields

These are imported into `GfiFundamentals` table:
- Price ratios: `trailingPE`, `forwardPE`, `priceToBook`
- Earnings: `trailingEps`, `forwardEps`
- Company metrics: `bookValue`, `totalRevenue`, `beta`
- Dividends: `dividendYield`, `trailingAnnualDividendRate`
- Price range: `fiftyTwoWeekHigh`, `fiftyTwoWeekLow`

## Step-by-Step Workflow

### Step 1: Prepare Your JSON Files

Organize your yFinance data in JSON files:

```
data/
└── yfinance/
    ├── warsaw_stocks.json      # Polish stocks
    ├── us_stocks.json          # US stocks
    └── european_stocks.json    # European stocks
```

Example file structure (`warsaw_stocks.json`):

```json
{
  "11B.WA": {
    "symbol": "11B.WA",
    "shortName": "11BIT",
    "longName": "11 bit studios S.A.",
    "currency": "PLN",
    "sector": "Communication Services",
    "industryDisp": "Electronic Gaming & Multimedia",
    "country": "Poland",
    "sharesOutstanding": 2417199,
    "currentPrice": 135.2,
    "marketCap": 326805312,
    "trailingPE": -17.49,
    "forwardPE": 2.45,
    ...
  },
  "PKO.WA": {
    ...
  }
}
```

### Step 2: Validate Your Data

Before importing, validate your JSON files:

```bash
# Validate a single file
python validate_yfinance_json.py data/yfinance/warsaw_stocks.json

# Validate all files in a directory
python validate_yfinance_json.py data/yfinance/
```

The validator will check:
- ✅ JSON syntax is valid
- ✅ Required fields are present
- ⚠️  Recommended fields are present
- ⚠️  Data types are correct
- ⚠️  Currency exists in database
- ℹ️  Fundamentals coverage percentage

**Example output:**

```
======================================================================
  VALIDATION RESULTS
======================================================================

📄 File: warsaw_stocks.json — ✓ VALID
   Symbols: 2

   ✓ 11B.WA
      ℹ️  Ticker: 11B, Market suffix: WA
      ℹ️  Fundamentals coverage: 85.7%

   ⚠️  PKO.WA
      ⚠️  Missing recommended fields: sharesOutstanding
      ℹ️  Ticker: PKO, Market suffix: WA
      ℹ️  Fundamentals coverage: 71.4%

======================================================================
  SUMMARY
======================================================================
  Total files:        1
  Valid files:        1
  Invalid files:      0
  Total symbols:      2

  ✅ All files are valid and ready for import!
======================================================================
```

### Step 3: Import Data

Once validation passes, import the data:

```bash
# Import all JSON files from a directory
python seed_yfinance.py data/yfinance/
```

The import process will:
1. Parse each symbol
2. Create/update reference data (Country, Sector, Industry)
3. Create/update Gfi (Global Financial Instrument)
4. Create/update GfiFundamentals
5. Create Qfi (Quoted Financial Instrument) linking to Market

**Example output:**

```
============================================================
  Processing 1 JSON file(s) from: data/yfinance
============================================================

  Processing: 11B.WA           [GFI✓, FUND✓, QFI✓]
  Processing: PKO.WA           [updated]

============================================================
  IMPORT SUMMARY
============================================================
  Files processed:        1
  GFIs created:           1
  GFIs updated:           1
  Fundamentals created:   1
  Fundamentals updated:   1
  QFIs created:           1
  Errors:                 0
============================================================
```

### Step 4: Verify Import

Check your database to verify the import:

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Gfi, GfiFundamentals, Qfi

engine = create_engine("your_database_url")

with Session(engine) as session:
    # Check Gfi
    stmt = select(Gfi).where(Gfi.ticker_yf == "11B.WA")
    gfi = session.scalars(stmt).first()
    print(f"GFI: {gfi}")
    
    # Check Fundamentals
    stmt = select(GfiFundamentals).where(GfiFundamentals.gfi_id == gfi.id)
    fundamentals = session.scalars(stmt).first()
    print(f"Fundamentals: PE={fundamentals.pe}, Market Cap={fundamentals.market_cap}")
    
    # Check Qfi
    stmt = select(Qfi).where(Qfi.gfi_id == gfi.id)
    qfi = session.scalars(stmt).first()
    print(f"QFI: {qfi}")
```

## Database Relationships

The import creates the following structure:

```
Gfi (11 bit studios S.A.)
├── fit_id → Fit ("Shares")
├── sector_id → Sector ("Communication Services")
├── industry_id → Industry ("Electronic Gaming & Multimedia")
├── country_id → Country ("Poland")
├── fundamentals → GfiFundamentals
│   ├── market_cap: 326,805,312 PLN
│   ├── pe: -17.49
│   ├── last_price: 135.2 PLN
│   └── ...
└── qfis → Qfi
    ├── market_id → Market (XWAR - Warsaw)
    ├── currency_id → Gfi (PLN currency)
    ├── quoted_unit_id → QuotedUnit ("Shares")
    └── quoted_amount: 1
```

## Idempotency

The import is **idempotent** - you can run it multiple times safely:

- **First run**: Creates new records
- **Subsequent runs**: Updates existing records where needed
- **Skips**: Records that haven't changed

This means you can:
- Re-run imports to update fundamentals
- Add new symbols to existing JSON files
- Fix data errors and re-import

## Troubleshooting

### Common Issues

**Issue**: `Currency 'XXX' not found`
- **Solution**: Add the currency to `seed.py` and run it, or the script will skip Qfi creation

**Issue**: `Market with MIC 'XXXX' not found`
- **Solution**: Add the market to `seed.py`, or update `MARKET_SUFFIX_TO_MIC` in `seed_yfinance.py`

**Issue**: `Fit 'Shares' not found`
- **Solution**: Run `seed.py` first to create base reference data

**Issue**: Country ISO code conflicts
- **Solution**: The script auto-generates ISO codes. For production, maintain a proper country mapping table

### Data Quality Tips

1. **Validate before importing** - Always run validation first
2. **Check coverage** - Aim for >70% fundamentals coverage
3. **Update regularly** - Re-run imports to keep fundamentals fresh
4. **Monitor warnings** - Address missing recommended fields
5. **Use source consistently** - All imports are tagged with `source_vendor='yfinance'`

## Extending the Import

### Adding New Markets

Edit `MARKET_SUFFIX_TO_MIC` in `seed_yfinance.py`:

```python
MARKET_SUFFIX_TO_MIC = {
    'WA': 'XWAR',  # Warsaw
    'US': 'XNYS',  # New York
    'DE': 'XETR',  # Frankfurt
    'L': 'XLON',   # London
    'PA': 'XPAR',  # Paris - NEW
    'MI': 'XMIL',  # Milan - NEW
}
```

Then add the market to `seed.py` if not already present.

### Adding New Fundamentals Fields

1. Add the field to `GfiFundamentals` model
2. Add the mapping in `import_yfinance_data()` function:

```python
fundamentals.your_new_field = safe_decimal(data.get('yfinanceFieldName'))
```

3. Run Alembic migration to update database schema

## Best Practices

1. **Separate files by region** - Easier to manage and validate
2. **Run validation first** - Catch issues before import
3. **Commit in batches** - The script commits once per file
4. **Keep seed.py current** - Ensure all reference data exists
5. **Monitor import logs** - Check for warnings about missing data
6. **Version your JSON files** - Keep backups before re-importing

## Next Steps

After importing yFinance data:

1. **Import price history** - Use separate scripts for `Quote_1day`, etc.
2. **Set up Vfi records** - Link to data vendors
3. **Configure VfiTimeSeries** - Enable time series collection
4. **Schedule updates** - Automate regular fundamentals refreshes

## Questions or Issues?

- Check validation output for specific issues
- Review database logs for constraint violations
- Ensure seed.py was run successfully first
- Verify JSON structure matches yFinance API response format
