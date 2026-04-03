"""
fetch_yfinance_data.py — Fetch yFinance data for a list of ticker symbols.

Run with:  python fetch_yfinance_data.py <tickers_file> <output_json>

Example:
    python fetch_yfinance_data.py tickers_warsaw.txt data/warsaw_stocks.json

The tickers file should contain one ticker per line:
    11B.WA
    PKO.WA
    CDR.WA
    ...

Requires: yfinance package (pip install yfinance)
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

try:
    import yfinance as yf
except ImportError:
    print("❌ Error: yfinance package not found.")
    print("   Install it with: pip install yfinance")
    sys.exit(1)


def read_tickers(file_path: str) -> List[str]:
    """Read ticker symbols from a text file (one per line)."""
    tickers = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            ticker = line.strip()
            if ticker and not ticker.startswith('#'):  # Skip empty lines and comments
                tickers.append(ticker)
    
    return tickers


def fetch_ticker_info(ticker: str) -> Dict[str, Any]:
    """Fetch info for a single ticker using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or 'symbol' not in info:
            return None
        
        return info
        
    except Exception as e:
        print(f"  ❌ Error fetching {ticker}: {e}")
        return None


def fetch_all_tickers(tickers: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch info for all tickers."""
    results = {}
    
    print(f"\nFetching data for {len(tickers)} ticker(s)...\n")
    
    for i, ticker in enumerate(tickers, 1):
        print(f"  [{i:>3}/{len(tickers)}] Fetching {ticker:<15} ... ", end='', flush=True)
        
        info = fetch_ticker_info(ticker)
        
        if info:
            results[ticker] = info
            print("✓")
        else:
            print("❌ Failed")
    
    return results


def save_to_json(data: Dict[str, Any], output_path: str):
    """Save data to JSON file."""
    output_file = Path(output_path)
    
    # Create directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(data)} ticker(s) to: {output_path}")


def print_summary(data: Dict[str, Any]):
    """Print summary statistics."""
    if not data:
        print("\n⚠️  No data was fetched successfully.")
        return
    
    total = len(data)
    
    # Count how many have key fields
    has_market_cap = sum(1 for v in data.values() if v.get('marketCap'))
    has_sector = sum(1 for v in data.values() if v.get('sector'))
    has_industry = sum(1 for v in data.values() if v.get('industryDisp'))
    has_country = sum(1 for v in data.values() if v.get('country'))
    
    print(f"\n{'='*60}")
    print(f"  FETCH SUMMARY")
    print(f"{'='*60}")
    print(f"  Total tickers:        {total}")
    print(f"  With market cap:      {has_market_cap} ({has_market_cap/total*100:.1f}%)")
    print(f"  With sector:          {has_sector} ({has_sector/total*100:.1f}%)")
    print(f"  With industry:        {has_industry} ({has_industry/total*100:.1f}%)")
    print(f"  With country:         {has_country} ({has_country/total*100:.1f}%)")
    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 3:
        print("Usage: python fetch_yfinance_data.py <tickers_file> <output_json>")
        print()
        print("Example:")
        print("  python fetch_yfinance_data.py tickers_warsaw.txt data/warsaw_stocks.json")
        print()
        print("The tickers file should contain one ticker per line:")
        print("  11B.WA")
        print("  PKO.WA")
        print("  CDR.WA")
        print("  ...")
        sys.exit(1)
    
    tickers_file = sys.argv[1]
    output_json = sys.argv[2]
    
    # Read tickers
    if not Path(tickers_file).exists():
        print(f"❌ Error: Tickers file '{tickers_file}' not found.")
        sys.exit(1)
    
    tickers = read_tickers(tickers_file)
    
    if not tickers:
        print(f"❌ Error: No tickers found in '{tickers_file}'.")
        sys.exit(1)
    
    print(f"📋 Loaded {len(tickers)} ticker(s) from: {tickers_file}")
    
    # Fetch data
    data = fetch_all_tickers(tickers)
    
    if not data:
        print("\n❌ Error: No data was fetched successfully.")
        sys.exit(1)
    
    # Save to JSON
    save_to_json(data, output_json)
    
    # Print summary
    print_summary(data)
    
    print("✅ Done! You can now validate and import the data:")
    print(f"   python validate_yfinance_json.py {output_json}")
    print(f"   python seed_yfinance.py {Path(output_json).parent}")


if __name__ == "__main__":
    main()
