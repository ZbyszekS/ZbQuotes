"""
resolve_lista_a1.py
-------------------
Resolves the 95 ISINs from mBank lista A1 to full instrument names.

Strategy (in order of preference):
  1. OpenFIGI API  — free, no key needed for basic use, returns name + ticker + exchange
  2. yfinance      — fallback for any ISIN that OpenFIGI didn't resolve
  3. Manual        — anything still missing is flagged for manual lookup

Output:
  lista_a1_names.json   — full structured results
  lista_a1_names.csv    — flat table for quick review

Requirements:
    pip install requests yfinance pandas

Usage:
    python resolve_lista_a1.py
    python resolve_lista_a1.py --no-yf       # skip yfinance fallback
"""

import argparse
import csv
import json
import time
from pathlib import Path

import requests

# ── Data from PDF ─────────────────────────────────────────────────────────────
INSTRUMENTS = [
    ("11BIT",     "PL11BTS00015"),  ("ABPL",      "PLAB00000019"),
    ("AGORA",     "PLAGORA00067"),  ("ALIOR",     "PLALIOR00045"),
    ("ALLEGRO",   "LU2237380790"),  ("AMICA",     "PLAMICA00010"),
    ("AMREST",    "ES0105375002"),  ("ANSWEAR",   "PLANSWR00019"),
    ("APATOR",    "PLAPATR00018"),  ("ARCTIC",    "PLARTPR00012"),
    ("ARLEN",     "PLARLEN00012"),  ("ASBIS",     "CY1000031710"),
    ("ASSECOBS",  "PLABS0000018"),  ("ASSECOPOL", "PLSOFTB00016"),
    ("ASSECOSEE", "PLASSEE00014"),  ("ATAL",      "PLATAL000046"),
    ("ATREM",     "PLATREM00017"),  ("AUTOPARTN", "PLATPRT00018"),
    ("BENEFIT",   "PLBNFTS00018"),  ("BLOOBER",   "PLBLOBR00014"),
    ("BNPPPL",    "PLBGZ0000010"),  ("BOGDANKA",  "PLLWBGD00016"),
    ("BORYSZEW",  "PLBRSZW00011"),  ("BUDIMEX",   "PLBUDMX00013"),
    ("CCC",       "PLCCC0000016"),  ("CDPROJEKT", "PLOPTTC00011"),
    ("CEZ",       "CZ0005112300"),  ("CIGAMES",   "PLCTINT00018"),
    ("COGNOR",    "PLCNTSL00014"),  ("COMP",      "PLCMP0000017"),
    ("CREEPYJAR", "PLCRPJR00019"),  ("CYBERFLKS", "PLR220000018"),
    ("CYFRPLSAT", "PLCFRPT00013"),  ("DADELO",    "PLDADEL00013"),
    ("DATAWALK",  "PLPILAB00012"),  ("DEVELIA",   "PLLCCRP00017"),
    ("DIAG",      "PLDGNST00012"),  ("DINOPL",    "PLDINPL00011"),
    ("DOMDEV",    "PLDMDVL00012"),  ("ELEKTROTI", "PLELEKT00016"),
    ("ENEA",      "PLENEA000013"),  ("ENERGA",    "PLENERG00022"),
    ("ENTER",     "PLENTER00017"),  ("EUROCASH",  "PLEURCH00011"),
    ("FERRO",     "PLFERRO00016"),  ("GPW",       "PLGPW0000047"),
    ("GRUPAAZOTY","PLZATRM00012"),  ("GRUPRACUJ", "PLGRPRC00015"),
    ("HANDLOWY",  "PLBH00000012"),  ("HUUUGE",    "US44853H1086"),
    ("INGBSK",    "PLBSK0000017"),  ("INTERCARS", "PLINTCS00010"),
    ("JSW",       "PLJSW0000015"),  ("KETY",      "PLKETY000011"),
    ("KGHM",      "PLKGHM000017"),  ("KRUK",      "PLKRK0000010"),
    ("LPP",       "PLLPP0000011"),  ("LUBAWA",    "PLLUBAW00013"),
    ("MBANK",     "PLBRE0000012"),  ("MILLENNIUM","PLBIG0000016"),
    ("MIRBUD",    "PLMRBUD00015"),  ("MOBRUK",    "PLMOBRK00013"),
    ("MOL",       "HU0000153937"),  ("MURAPOL",   "PLMURPL00190"),
    ("NEUCA",     "PLTRFRM00018"),  ("NEWAG",     "PLNEWAG00012"),
    ("ORANGEPL",  "PLTLKPL00017"),  ("PEKAO",     "PLPEKAO00016"),
    ("PEPCO",     "NL0015000AU7"),  ("PGE",       "PLPGER000010"),
    ("PKNORLEN",  "PLPKN0000018"),  ("PKOBP",     "PLPKO0000016"),
    ("PKPCARGO",  "PLPKPCR00011"),  ("PLAYWAY",   "PLPLAYW00015"),
    ("PZU",       "PLPZU0000011"),  ("QUERCUS",   "PLQRCUS00012"),
    ("RAINBOW",   "PLRNBWT00031"),  ("SANPL",     "PLBZ00000044"),
    ("SELVITA",   "PLSLVCR00029"),  ("SHOPER",    "PLSHPR000021"),
    ("STALEXP",   "PLSTLEX00019"),  ("SYGNITY",   "PLCMPLD00016"),
    ("SYNEKTIK",  "PLSNKTK00019"),  ("TAURONPE",  "PLTAURN00011"),
    ("TEXT",      "PLLVTSF00010"),  ("TORPOL",    "PLTORPL00016"),
    ("TOYA",      "PLTOYA000011"),  ("TSGAMES",   "PLTSQGM00016"),
    ("UNIMOT",    "PLUNMOT00013"),  ("VERCOM",    "PLVRCM000016"),
    ("VOXEL",     "PLVOXEL00014"),  ("WIRTUALNA", "PLWRTPL00027"),
    ("WITTCHEN",  "PLWTCHN00030"),  ("XTB",       "PLXTRDM00011"),
    ("ZABKA",     "LU2910446546"),
]

ISIN_TO_YF = {
    "PL11BTS00015": "11B.WA",
    "PLAB00000019": "ABP.WA",
    "PLAGORA00067": "AGO.WA",
    "PLALIOR00045": "ALR.WA",
    "LU2237380790": "ALE.WA",
    "PLAMICA00010": "AMC.WA",
    "ES0105375002": "EAT.MC",
    "PLANSWR00019": "ANR.WA",
    "PLAPATR00018": "APT.WA",
    "PLARTPR00012": "ATP.WA",
    "PLARLEN00012": "ARL.WA",
    "CY1000031710": "ASB.WA",
    "PLABS0000018": "ABS.WA",
    "PLSOFTB00016": "ACP.WA",
    "PLASSEE00014": "ASE.WA",
    "PLATAL000046": "1AT.WA",
    "PLATREM00017": "ATR.WA",
    "PLATPRT00018": "APR.WA",
    "PLBNFTS00018": "BFT.WA",
    "PLBLOBR00014": "BLO.WA",
    "PLBGZ0000010": "BNP.WA",
    "PLLWBGD00016": "LWB.WA",
    "PLBRSZW00011": "BRS.WA",
    "PLBUDMX00013": "BDX.WA",
    "PLCCC0000016": "CCC.WA",
    "PLOPTTC00011": "CDR.WA",
    "CZ0005112300": "CEZ.PR",
    "PLCTINT00018": "CIG.WA",
    "PLCNTSL00014": "COG.WA",
    "PLCMP0000017": "CMP.WA",
    "PLCRPJR00019": "CRJ.WA",
    "PLR220000018": "CBF.WA",
    "PLCFRPT00013": "CPS.WA",
    "PLDADEL00013": "DDL.WA",
    "PLPILAB00012": "DAT.WA",
    "PLLCCRP00017": "DVL.WA",
    "PLDGNST00012": "DIA.WA",
    "PLDINPL00011": "DNP.WA",
    "PLDMDVL00012": "DOM.WA",
    "PLELEKT00016": "ELT.WA",
    "PLENEA000013": "ENA.WA",
    "PLENERG00022": "ENG.WA",
    "PLENTER00017": "ENT.WA",
    "PLEURCH00011": "EUR.WA",
    "PLFERRO00016": "FER.WA",
    "PLGPW0000047": "GPW.WA",
    "PLZATRM00012": "ATT.WA",
    "PLGRPRC00015": "GPP.WA",
    "PLBH00000012": "BHW.WA",
    "US44853H1086": "HUGS",
    "PLBSK0000017": "ING.WA",
    "PLINTCS00010": "CAR.WA",
    "PLJSW0000015": "JSW.WA",
    "PLKETY000011": "KTY.WA",
    "PLKGHM000017": "KGH.WA",
    "PLKRK0000010": "KRU.WA",
    "PLLPP0000011": "LPP.WA",
    "PLLUBAW00013": "LBW.WA",
    "PLBRE0000012": "MBK.WA",
    "PLBIG0000016": "MIL.WA",
    "PLMRBUD00015": "MRB.WA",
    "PLMOBRK00013": "MBR.WA",
    "HU0000153937": "MOL.BD",
    "PLMURPL00190": "MUR.WA",
    "PLTRFRM00018": "NEU.WA",
    "PLNEWAG00012": "NWG.WA",
    "PLTLKPL00017": "OPL.WA",
    "PLPEKAO00016": "PEO.WA",
    "NL0015000AU7": "PCO.AS",
    "PLPGER000010": "PGE.WA",
    "PLPKN0000018": "PKN.WA",
    "PLPKO0000016": "PKO.WA",
    "PLPKPCR00011": "PKP.WA",
    "PLPLAYW00015": "PLW.WA",
    "PLPZU0000011": "PZU.WA",
    "PLQRCUS00012": "QRS.WA",
    "PLRNBWT00031": "RBW.WA",
    "PLBZ00000044": "SPL.WA",
    "PLSLVCR00029": "SLV.WA",
    "PLSHPR000021": "SHO.WA",
    "PLSTLEX00019": "STX.WA",
    "PLCMPLD00016": "SGN.WA",
    "PLSNKTK00019": "SNT.WA",
    "PLTAURN00011": "TPE.WA",
    "PLLVTSF00010": "TXT.WA",
    "PLTORPL00016": "TOR.WA",
    "PLTOYA000011": "TOA.WA",
    "PLTSQGM00016": "TEN.WA",
    "PLUNMOT00013": "UNT.WA",
    "PLVRCM000016": "VRC.WA",
    "PLVOXEL00014": "VOX.WA",
    "PLWRTPL00027": "WPL.WA",
    "PLWTCHN00030": "WTN.WA",
    "PLXTRDM00011": "XTB.WA",
    "LU2910446546": "ZAB.WA",
}


# ── Step 1: OpenFIGI batch lookup ─────────────────────────────────────────────

OPENFIGI_URL = "https://api.openfigi.com/v3/mapping"

def query_openfigi(isin_list: list[str], api_key: str = "") -> list[dict]:
    """
    Batch-query OpenFIGI for a list of ISINs.
    Returns list of result dicts, one per ISIN (same order).

    Rate limits:
      No key:       10 items/request, 25 requests/min
      Free API key: 100 items/request, 25 requests/min
    Get a free key at https://www.openfigi.com/api#get-started
    """
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-OPENFIGI-APIKEY"] = api_key

    batch_size = 100 if api_key else 10
    all_results = []

    chunks = [isin_list[i:i + batch_size] for i in range(0, len(isin_list), batch_size)]
    print(f"  Sending {len(chunks)} requests (batch size {batch_size}) …")

    for idx, chunk in enumerate(chunks, 1):
        jobs = [{"idType": "ID_ISIN", "idValue": isin} for isin in chunk]
        resp = requests.post(OPENFIGI_URL, headers=headers, json=jobs, timeout=30)

        if resp.status_code == 429:
            print(f"  Rate limited on chunk {idx} — waiting 60 seconds …")
            time.sleep(60)
            resp = requests.post(OPENFIGI_URL, headers=headers, json=jobs, timeout=30)

        resp.raise_for_status()
        all_results.extend(resp.json())

        if idx < len(chunks):
            time.sleep(2.5)   # stay safely under 25 req/min

    return all_results


def parse_figi_result(result: dict) -> dict:
    """Extract best hit from one OpenFIGI result entry."""
    if "error" in result or "data" not in result or not result["data"]:
        return {}
    # Prefer equity over other security types
    hits = result["data"]
    equity_hits = [h for h in hits if "Equity" in h.get("securityType", "")]
    hit = equity_hits[0] if equity_hits else hits[0]
    return {
        "full_name":     hit.get("name", ""),
        "figi_ticker":   hit.get("ticker", ""),
        "exchange_code": hit.get("exchCode", ""),
        "security_type": hit.get("securityType", ""),
        "market_sector": hit.get("marketSector", ""),
        "figi":          hit.get("figi", ""),
        "source":        "openfigi",
    }


# ── Step 2: yfinance fallback ─────────────────────────────────────────────────

# Polish WSE tickers use the pattern: <GPW_ticker>.WA
# For instruments we couldn't resolve via FIGI, try yfinance with .WA suffix
WA_TICKER_MAP = {
    short: f"{short}.WA" for short, _ in INSTRUMENTS
}
# Known non-WA tickers
WA_TICKER_MAP.update({
    "HUUUGE":  "HUUUGE.WA",  # listed on WSE
    "ALLEGRO": "ALE.WA",
    "PEPCO":   "PCO.WA",
    "MOL":     "MOL.WA",
    "CEZ":     "CEZ.WA",
    "AMREST":  "EAT.WA",
    "ZABKA":   "ZAB.WA",
})


def try_yfinance(short_name: str) -> dict:
    """Try to get info from yfinance using .WA ticker."""
    try:
        import yfinance as yf
        ticker_sym = WA_TICKER_MAP.get(short_name, f"{short_name}.WA")
        t = yf.Ticker(ticker_sym)
        info = t.info
        if info.get("longName") or info.get("shortName"):
            return {
                "full_name":     info.get("longName") or info.get("shortName", ""),
                "figi_ticker":   ticker_sym,
                "exchange_code": info.get("exchange", ""),
                "security_type": info.get("quoteType", ""),
                "market_sector": info.get("sector", ""),
                "figi":          "",
                "yf_symbol":     ticker_sym,
                "source":        "yfinance",
            }
    except Exception as e:
        pass
    return {}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-yf", action="store_true", help="Skip yfinance fallback")
    parser.add_argument("--api-key", default="", help="OpenFIGI API key (optional)")
    args = parser.parse_args()

    print(f"Resolving {len(INSTRUMENTS)} ISINs …\n")

    # ── OpenFIGI ──────────────────────────────────────────────────────────
    print("Step 1: OpenFIGI batch lookup …")
    isins = [isin for _, isin in INSTRUMENTS]

    # OpenFIGI allows max 100 per request; we have 95
    figi_raw = query_openfigi(isins, api_key=args.api_key)
    print(f"  Got {len(figi_raw)} results from OpenFIGI")

    results = []
    not_resolved = []

    for (short_name, isin), raw in zip(INSTRUMENTS, figi_raw):
        parsed = parse_figi_result(raw)
        rec = {
            "isin":       isin,
            "mbank_name": short_name,
            **parsed,
        }
        if not parsed:
            rec.update({
                "full_name": "", "figi_ticker": "", "exchange_code": "",
                "security_type": "", "market_sector": "", "figi": "",
                "source": "not_found",
            })
            not_resolved.append(rec)
        results.append(rec)

    resolved = len(results) - len(not_resolved)
    print(f"  Resolved: {resolved}  |  Not resolved: {len(not_resolved)}")

    # ── yfinance fallback ─────────────────────────────────────────────────
    if not args.no_yf and not_resolved:
        print(f"\nStep 2: yfinance fallback for {len(not_resolved)} unresolved …")
        for rec in not_resolved:
            time.sleep(0.5)  # be polite
            yf_data = try_yfinance(rec["mbank_name"])
            if yf_data:
                rec.update(yf_data)
                print(f"  ✓ {rec['mbank_name']:12}  {rec['full_name']}")
            else:
                print(f"  ✗ {rec['mbank_name']:12}  still unresolved")

    # ── Print summary table ───────────────────────────────────────────────
    print(f"\n{'#':<4} {'ISIN':<14} {'mBank':<12} {'Full Name':<50} {'Ticker':<10} {'Source'}")
    print("-" * 105)
    for i, rec in enumerate(results, 1):
        name = rec.get("full_name", "")[:49]
        ticker = rec.get("figi_ticker", rec.get("yf_symbol", ""))
        source = rec.get("source", "")
        flag = "⚠" if not rec.get("full_name") else " "
        print(f"{flag}{i:<3} {rec['isin']:<14} {rec['mbank_name']:<12} {name:<50} {ticker:<10} {source}")

    still_missing = [r for r in results if not r.get("full_name")]
    if still_missing:
        print(f"\n⚠  {len(still_missing)} instruments still unresolved:")
        for r in still_missing:
            print(f"   {r['isin']}  ({r['mbank_name']})")

    # ── Save outputs ──────────────────────────────────────────────────────
    out_json = Path("lista_a1_names.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ JSON → {out_json}")

    out_csv = Path("lista_a1_names.csv")
    fields = ["isin", "mbank_name", "full_name", "figi_ticker",
              "exchange_code", "security_type", "market_sector", "figi", "source"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(results)
    print(f"✓ CSV  → {out_csv}")

    print(f"\nNext step: use lista_a1_names.json to map ISINs → yfinance tickers")
    print("Tip: run  python resolve_lista_a1.py  (with yfinance installed for fallback)")


if __name__ == "__main__":
    main()