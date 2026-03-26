"""
extract_mbank.py — parse mBank Wykaz instrumentow zagranicznych PDF
"""
import sys, json, re, csv
from pathlib import Path
from datetime import date
from collections import Counter
import pdfplumber

# directory where import_data.py lives
SCRIPT_DIR = Path(__file__).resolve().parent
# ZbQuotes
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent
MBANK_PDF_FILE_NAME = "Lista dostepnych instumentow zagranicznych 18 03 2026 kid all in one.pdf"
MBANK_PDF_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "raw_net_data" / MBANK_PDF_FILE_NAME
MBANK_OUT_JSON_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" / "mbank_foreign.json"
MBANK_OUT_CSV_PATH =  PROJECT_ROOT / "resources" / "data" / "processed_data" / "mbank_foreign.csv"

if not MBANK_PDF_DATA_PATH.exists():
    print("─────────────────────────────────────────────")
    print(f"Error: PDF file not found at {MBANK_PDF_DATA_PATH}")
    print("─────────────────────────────────────────────")
    sys.exit(1)


EXCHANGE_PREFIX = [
    ("DEUTSCHE BÖRSE",                 "XETR", "DEU-XETRA"),
    ("LONDON STOCK EXCHANGE",          "XLON", "GBR-LSE"),
    ("NEW YORK STOCK EXCHANGE",        "XNYS", "USA-NYSE"),
    ("NASDAQ",                         "XNAS", "USA-NASDAQ"),
    ("GIEŁDA PAPIERÓW WARTOŚCIOWYCH",  "XWAR", "GPW-WWA"),
    ("GIEŁDA PAPIERÓW",                 "XWAR", "GPW-WWA"),
]
TYPE_MAP = {"AKCJA":"STOCK","ETF":"ETF","ADR/GDR":"ADR_GDR","OBLIGACJA":"BOND"}
FIT_MAP  = {"STOCK":"Shares","ETF":"Shares","ADR_GDR":"Shares","BOND":"Bonds","UNKNOWN":"Shares"}

ISIN_TYPE_RE = re.compile(
    r'(.+?)\s+([A-Z]{2}[A-Z0-9]{10})\s+(AKCJA[\s\d\)]*|ETF|ADR/GDR|OBLIGACJA\**)\s*$'
)
MARKET_RE = re.compile(r'\b([A-Z]{3}-[A-Z]{3,6})\b')
CCY_RE    = re.compile(r'\(([A-Z]{3})\)')

BB_TICKER_RE = re.compile(r'\b([A-Z0-9\.]{1,8}:[A-Z]{2})\b')

def detect_exchange(line):
    up = line.upper()
    for name, mic, mkt in EXCHANGE_PREFIX:
        if up.startswith(name):
            m = CCY_RE.search(line[:len(name)+12])
            ccy = m.group(1) if m else ""
            return name, mic, mkt, ccy
    return None, None, None, None

def strip_prefix(line, exchange_name):
    p = re.compile(re.escape(exchange_name)+r'\s*\([A-Z]{3}\)\s+[A-Z]+-[A-Z]+\s+', re.I)
    return p.sub('', line, 1).strip()

def parse_tickers(chunk):
    """Extract bloomberg + google ticker from the chunk between name and ISIN."""
    tokens = chunk.strip().split()
    bb, gg = "", ""
    # find rightmost colon-ticker
    for i in range(len(tokens)-1, -1, -1):
        if re.match(r'^[A-Z0-9\./\-]{1,10}:[A-Z]{2}$', tokens[i]):
            bb = tokens[i]
            if i > 0 and re.match(r'^[A-Z0-9\./\-]{1,10}$', tokens[i-1]) and len(tokens[i-1])<=10:
                gg = tokens[i-1]
                name = " ".join(tokens[:i-1])
            else:
                name = " ".join(tokens[:i])
            return name.strip(), bb, gg
    # no colon ticker found — try "SYM LN ETF" style
    for i in range(len(tokens)-2, -1, -1):
        if tokens[i] in ("LN","GR","US","PW") and i+1 < len(tokens) and tokens[i+1]=="ETF":
            bb = tokens[i-1]+" "+tokens[i]+" ETF" if i>0 else ""
            gg = tokens[i-1] if i > 0 else ""
            name = " ".join(tokens[:max(0, i-1)])
            return name.strip(), bb.strip(), gg.strip()
    return chunk.strip(), "", ""

def yf_from_bb(bb):
    if not bb: return ""
    parts = bb.split(":")
    if len(parts)==2:
        sym, exch = parts[0], parts[1].strip()
        sfx = {"GR":".DE","LN":".L","US":"","PW":".WA","LI":".L"}.get(exch,"")
        return sym+sfx
    parts = bb.split()
    if len(parts)>=2:
        sfx = {"LN":".L","GR":".DE","US":"","PW":".WA"}.get(parts[1],"")
        return parts[0]+sfx
    return ""

def parse_line(line):
    line = line.strip()
    exchange_name, mic, mkt_code, ccy = detect_exchange(line)
    if not mic: return None
    rest = strip_prefix(line, exchange_name)
    m = ISIN_TYPE_RE.match(rest)
    if not m: return None
    prefix, isin, raw_type = m.group(1).strip(), m.group(2), m.group(3).strip()
    raw_clean = re.sub(r'\s+\d+\)|\*+$','',raw_type).strip().upper()
    inst_type = TYPE_MAP.get(raw_clean, "UNKNOWN")
    name, bb, gg = parse_tickers(prefix)
    if not name: name = prefix.split()[0] if prefix else "?"
    return {
        "exchange_name": exchange_name,
        "mic": mic,
        "market_code": mkt_code,
        "currency": ccy,
        "name": name,
        "ticker_bloomberg": bb,
        "ticker_google": gg,
        "isin": isin,
        "instrument_type": inst_type,
        "yf_symbol": yf_from_bb(bb),
    }

def extract(pdf_path):
    instruments, seen = [], set()
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            for line in (page.extract_text() or "").splitlines():
                rec = parse_line(line)
                if not rec: continue
                key = (rec["isin"], rec["mic"])
                if key in seen: continue
                seen.add(key)
                instruments.append(rec)
    return instruments

def build_seed(instruments):
    gfi_map, qfi_list, vfi_list, seen_vfi = {}, [], [], set()
    for i in instruments:
        isin = i["isin"]
        if isin not in gfi_map:
            gfi_map[isin] = {"isin":isin,"name":i["name"],"description":i["name"],
                             "fit_name":FIT_MAP.get(i["instrument_type"],"Shares")}
        qfi_list.append({"isin":isin,"name":i["name"],"mic":i["mic"],
                         "market_code":i["market_code"],"currency":i["currency"],
                         "instrument_type":i["instrument_type"]})
        for vendor, sym in [("Bloomberg",i["ticker_bloomberg"]),("Google",i["ticker_google"])]:
            if sym and sym not in ("-",""):
                k=(isin,vendor,sym)
                if k not in seen_vfi:
                    seen_vfi.add(k)
                    vfi_list.append({"isin":isin,"vendor":vendor,"symbol":sym,
                                     "yf_symbol":i["yf_symbol"]})
    return {
        "source": "mBank Biuro maklerskie",
        "extracted_date": str(date.today()),
        "totals": {"unique_gfi":len(gfi_map),"listings_qfi":len(qfi_list),
                   "vendor_tickers_vfi":len(vfi_list)},
        "gfi_candidates": list(gfi_map.values()),
        "qfi_candidates": qfi_list,
        "vfi_candidates": vfi_list,
        "raw_instruments": instruments,
    }

FIELDS = ["isin","name","mic","market_code","currency","instrument_type",
          "ticker_bloomberg","ticker_google","yf_symbol","exchange_name"]

def main():
    print("--- Running process_mbank_foreign_pdf.py ---")
    # pdf_path = Path(sys.argv[1]) if len(sys.argv)>1 else Path("mbank_assets.pdf")
    # if not pdf_path.exists(): sys.exit(f"Not found: {pdf_path}")
    pdf_path = MBANK_PDF_DATA_PATH
    print(f"Reading {pdf_path} …")
    instruments = extract(pdf_path)
    print(f"  Deduped rows: {len(instruments)}")
    seed = build_seed(instruments)
    t = seed["totals"]
    print(f"  Gfi: {t['unique_gfi']}  Qfi: {t['listings_qfi']}  Vfi: {t['vendor_tickers_vfi']}")

    # writing output files ─────────────────────────────────────────────
    out_json = MBANK_OUT_JSON_PATH
    with open(out_json,"w",encoding="utf-8") as f:
        json.dump(seed, f, ensure_ascii=False, indent=2)

    out_csv = MBANK_OUT_CSV_PATH
    with open(out_csv,"w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader(); w.writerows(instruments)
    
    print(f"✓ {out_json}\n✓ {out_csv}")

    types = Counter(i["instrument_type"] for i in instruments)
    print("\nType:"); [print(f"  {k:<12}{v:>5}") for k,v in sorted(types.items(), key=lambda x:-x[1])]
    exchanges = Counter(i["mic"] for i in instruments)
    print("\nExchange:"); [print(f"  {k:<8}{v:>5}") for k,v in sorted(exchanges.items(), key=lambda x:-x[1])]
    print("\nSample:")
    for r in instruments[:6]:
        print(f"  {r['isin']}  {r['mic']:<6}  {r['name'][:40]:<40}  {r['instrument_type']:<10}  {r['ticker_bloomberg']}")

if __name__=="__main__":
    main()

# ── patched main for final output ─────────────────────────────────────────────
