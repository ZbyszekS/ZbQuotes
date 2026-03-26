import pdfplumber
import pandas as pd
import re

# 1. Configuration
pdf_path = "jupyter_notebooks/mbank_assets.pdf"
isin_pattern = re.compile(r'([A-Z]{2}[A-Z0-9]{10})') # Finds ISINs like DE000A1EWWW0

all_stocks = []

def get_yfinance_suffix(raw_text):
    """Maps mBank Market names to yfinance suffixes for your portfolio"""
    raw_text = raw_text.upper()
    if 'XETRA' in raw_text: return '.DE'
    if 'WARSAW' in raw_text or 'GPW' in raw_text: return '.WA'
    if 'LONDON' in raw_text: return '.L'
    if 'NASDAQ' in raw_text or 'NEW YORK' in raw_text: return '' # US usually no suffix
    return ''

# 2. Extraction
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if not table: continue
        
        for row in table:
            # Join row into one string to fix the 'merged cell' problem
            line = " ".join([str(c) for c in row if c])
            
            # Find the ISIN in the line
            match = isin_pattern.search(line)
            if match and "AKCJA" in line.upper():
                isin = match.group(1)
                
                # Split the line into words
                words = line.split()
                try:
                    isin_idx = words.index(isin)
                    
                    # In mBank's format: [..., TickerBloomberg, TickerGoogle, ISIN, TYP]
                    # So TickerGoogle is 1 step before ISIN
                    ticker = words[isin_idx - 1]
                    
                    # The Name is everything before the Tickers
                    name = " ".join(words[2:isin_idx - 2])
                    
                    all_stocks.append({
                        "Symbol": ticker,
                        "Suffix": get_yfinance_suffix(line),
                        "ISIN": isin,
                        "Name": name,
                        "Full_Ticker": f"{ticker}{get_yfinance_suffix(line)}"
                    })
                except (ValueError, IndexError):
                    continue

# 3. Save to JSON
df = pd.DataFrame(all_stocks).drop_duplicates(subset=['ISIN'])
df.to_json('mbank_stocks_final.json', orient='records', indent=4, force_ascii=False)

print(f"DONE! Found {len(df)} unique stocks.")
print("Sample:")
print(df[['Full_Ticker', 'Name', 'ISIN']].head())