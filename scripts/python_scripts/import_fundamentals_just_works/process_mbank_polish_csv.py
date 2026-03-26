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


YF_ALL_INFO_FILE_NAME = "yf_info_polish.json"
YF_ALL_INFO_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" / YF_ALL_INFO_FILE_NAME
YF_ALL_INFO_SKIPPED_FILE_NAME = "yf_info_skipped_polish.json"
YF_ALL_INFO_SKIPPED_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" / YF_ALL_INFO_SKIPPED_FILE_NAME


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




@dataclass
class mBankCsvInfoShort:
    isin:             str
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









def isin_ticker_list_to_list_of_mbank_infos(isin_ticker_dict: dict[str, str]) -> list[mBankCsvInfoShort]:
    mbank_infos = []
    for isin, yf_ticker in isin_ticker_dict.items():
        mbank_infos.append(mBankCsvInfoShort(
            isin            =isin,
            yf_ticker       =yf_ticker
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


def mbank_infos_to_yf_infos(mbank_infos: list[mBankCsvInfoShort]) -> tuple[dict[str, dict], list[str]]:
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
    mbank_infos = isin_ticker_list_to_list_of_mbank_infos(ISIN_TO_YF)
    yf_infos, all_skipped = mbank_infos_to_yf_infos(mbank_infos)
    # Save to JSON
    with open(YF_ALL_INFO_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(yf_infos, f, indent=2)
    with open(YF_ALL_INFO_SKIPPED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(all_skipped, f, indent=2)
    logger.info(f'Saved  : {len(yf_infos)} YF infos to {YF_ALL_INFO_DATA_PATH}')
    logger.info(f'Skipped: {len(all_skipped)} YF skipped infos to {YF_ALL_INFO_SKIPPED_DATA_PATH}')
