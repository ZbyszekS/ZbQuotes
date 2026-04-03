"""
validate_yfinance_json.py — Validate yFinance JSON files before import.

Run with:  python validate_yfinance_json.py <path_to_json_file_or_directory>

This script:
- Validates JSON structure
- Checks for required fields
- Reports missing or invalid data
- Suggests data quality improvements
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List


# Required fields for basic import
REQUIRED_FIELDS = [
    'symbol',
    'currency',
]

# Recommended fields for good data quality
RECOMMENDED_FIELDS = [
    'shortName',
    'longName',
    'sector',
    'industryDisp',
    'country',
    'sharesOutstanding',
    'currentPrice',
    'marketCap',
]

# Fundamentals fields we import
FUNDAMENTALS_FIELDS = [
    'trailingPE', 'forwardPE', 'trailingEps', 'forwardEps',
    'bookValue', 'priceToBook', 'totalRevenue', 'beta',
    'dividendYield', 'trailingAnnualDividendRate',
    'fiftyTwoWeekHigh', 'fiftyTwoWeekLow',
]


def validate_entry(symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a single yFinance entry.
    
    Returns:
        Dict with validation results
    """
    issues = []
    warnings = []
    info = []
    
    # Check symbol format
    if '.' in symbol:
        ticker, suffix = symbol.rsplit('.', 1)
        info.append(f"Ticker: {ticker}, Market suffix: {suffix}")
    else:
        info.append(f"Ticker: {symbol} (no market suffix - will default to US)")
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            issues.append(f"Missing required field: {field}")
    
    # Check recommended fields
    missing_recommended = []
    for field in RECOMMENDED_FIELDS:
        if field not in data or data[field] is None:
            missing_recommended.append(field)
    
    if missing_recommended:
        warnings.append(f"Missing recommended fields: {', '.join(missing_recommended)}")
    
    # Check fundamentals coverage
    missing_fundamentals = []
    for field in FUNDAMENTALS_FIELDS:
        if field not in data or data[field] is None:
            missing_fundamentals.append(field)
    
    fundamentals_coverage = (len(FUNDAMENTALS_FIELDS) - len(missing_fundamentals)) / len(FUNDAMENTALS_FIELDS) * 100
    info.append(f"Fundamentals coverage: {fundamentals_coverage:.1f}%")
    
    if fundamentals_coverage < 50:
        warnings.append(f"Low fundamentals coverage ({fundamentals_coverage:.1f}%)")
    
    # Data type validations
    if 'sharesOutstanding' in data and data['sharesOutstanding'] is not None:
        try:
            int(data['sharesOutstanding'])
        except (ValueError, TypeError):
            issues.append("Invalid sharesOutstanding: not a valid integer")
    
    if 'currentPrice' in data and data['currentPrice'] is not None:
        try:
            float(data['currentPrice'])
        except (ValueError, TypeError):
            issues.append("Invalid currentPrice: not a valid number")
    
    # Check currency
    if 'currency' in data:
        currency = data['currency']
        if currency not in ['PLN', 'USD', 'EUR', 'GBP', 'JPY', 'CHF']:
            warnings.append(f"Currency '{currency}' may not exist in database. Run seed.py to create it.")
    
    return {
        'issues': issues,
        'warnings': warnings,
        'info': info,
    }


def validate_json_file(file_path: Path) -> Dict[str, Any]:
    """Validate a single JSON file."""
    results = {
        'file': file_path.name,
        'valid': True,
        'symbols_count': 0,
        'entries': [],
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)
        
        if not isinstance(data_dict, dict):
            results['valid'] = False
            results['error'] = "JSON root must be a dictionary"
            return results
        
        results['symbols_count'] = len(data_dict)
        
        for symbol, data in data_dict.items():
            validation = validate_entry(symbol, data)
            
            entry_result = {
                'symbol': symbol,
                'has_issues': len(validation['issues']) > 0,
                'has_warnings': len(validation['warnings']) > 0,
                'issues': validation['issues'],
                'warnings': validation['warnings'],
                'info': validation['info'],
            }
            
            results['entries'].append(entry_result)
            
            if entry_result['has_issues']:
                results['valid'] = False
        
    except json.JSONDecodeError as e:
        results['valid'] = False
        results['error'] = f"Invalid JSON: {e}"
    except Exception as e:
        results['valid'] = False
        results['error'] = f"Error reading file: {e}"
    
    return results


def print_validation_results(results: List[Dict[str, Any]]):
    """Print validation results in a readable format."""
    total_files = len(results)
    valid_files = sum(1 for r in results if r['valid'])
    total_symbols = sum(r.get('symbols_count', 0) for r in results)
    
    print(f"\n{'='*70}")
    print(f"  VALIDATION RESULTS")
    print(f"{'='*70}\n")
    
    for result in results:
        file_name = result['file']
        status = "✓ VALID" if result['valid'] else "❌ INVALID"
        
        print(f"\n📄 File: {file_name} — {status}")
        
        if 'error' in result:
            print(f"   Error: {result['error']}")
            continue
        
        print(f"   Symbols: {result['symbols_count']}")
        
        # Print entry details
        for entry in result['entries']:
            symbol = entry['symbol']
            
            if entry['has_issues']:
                print(f"\n   ❌ {symbol}")
                for issue in entry['issues']:
                    print(f"      • {issue}")
            elif entry['has_warnings']:
                print(f"\n   ⚠️  {symbol}")
            else:
                print(f"\n   ✓ {symbol}")
            
            # Print warnings
            for warning in entry['warnings']:
                print(f"      ⚠️  {warning}")
            
            # Print info (only for first entry or if there are issues)
            if entry['has_issues'] or entry['has_warnings']:
                for info_item in entry['info']:
                    print(f"      ℹ️  {info_item}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total files:        {total_files}")
    print(f"  Valid files:        {valid_files}")
    print(f"  Invalid files:      {total_files - valid_files}")
    print(f"  Total symbols:      {total_symbols}")
    
    if valid_files == total_files:
        print(f"\n  ✅ All files are valid and ready for import!")
    else:
        print(f"\n  ⚠️  Some files have issues. Please review and fix before importing.")
    
    print(f"{'='*70}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_yfinance_json.py <path_to_json_file_or_directory>")
        print("Example: python validate_yfinance_json.py ./data/yfinance")
        print("Example: python validate_yfinance_json.py ./data/yfinance/stocks.json")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if not path.exists():
        print(f"❌ Error: Path '{path}' does not exist.")
        sys.exit(1)
    
    # Collect JSON files
    json_files = []
    if path.is_file():
        if path.suffix == '.json':
            json_files = [path]
        else:
            print(f"❌ Error: File '{path}' is not a JSON file.")
            sys.exit(1)
    elif path.is_dir():
        json_files = list(path.glob('*.json'))
        if not json_files:
            print(f"❌ Error: No JSON files found in '{path}'.")
            sys.exit(1)
    
    # Validate files
    results = []
    for json_file in json_files:
        result = validate_json_file(json_file)
        results.append(result)
    
    # Print results
    print_validation_results(results)
    
    # Exit code
    if all(r['valid'] for r in results):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
