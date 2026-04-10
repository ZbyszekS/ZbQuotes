GFI_NAMES_2_ACTIVATE = [
    "PKNORLEN",
    "PKOBP",
    "SANPL",
    "PEKAO",
    "PZU",
    "KGHM",
    "INGBSK",
    "MBANK",
    "DINOPL",
    "LPP",
    "CDPROJEKT",
    "PGE",
    "BNPPPL",
    "MILLENNIUM",
    "ORANGEPL",
    "BUDIMEX",
    "TAURONPE",
    "HANDLOWY"
]
GFI_NAMES_2_ACTIVATE_2 = [
    "NVIDIA Corporation",
    "Apple Inc.",
    "Alphabet Inc.",
    "MOL HUNGARIAN OIL",
    "Microsoft Corporation",
    "Amazon.com, Inc.",
    "Taiwan Semiconductor Manufactur",
    "Meta Platforms, Inc.",
    "Broadcom Inc.",
    "Tesla, Inc.",
    "Walmart Inc.",
    "Eli Lilly and Company",
    "JP Morgan Chase & Co.",
    "Exxon Mobil Corporation",
    "CEZ",
    "Visa Inc.",
    "Tencent Holding Ltd."
    "Johnson & Johnson",
    "ASML Holding N.V. - New York Re",
    "Micron Technology, Inc.",
    "Mastercard Incorporated",
    "Costco Wholesale Corporation",
    "Oracle Corporation",
    "Chevron Corporation",
    "Netflix, Inc.",
    "AbbVie Inc.",
    "Palantir Technologies Inc.",
    "Bank of America Corporation",
    "Procter & Gamble Company (The)",
    "Advanced Micro Devices, Inc.",
    "Coca-Cola Company (The)",
    "Home Depot, Inc. (The)",
    "Caterpillar, Inc.",
    "Cisco Systems, Inc.",
    "Roche Holding Ltd",
    "GE Aerospace",
    "Alibaba Group Holding Limited",
    "AstraZeneca PLC US0463531089 AZN",
    "Applied Materials, Inc.",
    "Merck & Company, Inc.",
    "Novartis AG",
    "China Construction Bank Corp.",
    "Agricultural Bank of China",
    "Toyota Motor Corporation",
    "RTX Corporation",
    "HSBC Holdings, plc.",
    "Morgan Stanley",
    "Shell PLC",
    "Philip Morris International Inc",
    "UnitedHealth Group Incorporated",
    "AstraZeneca PLC",
    "Nestle S.A.",
    "Goldman Sachs Group, Inc. (The)",
    "Wells Fargo & Company",
    "Bank of China, Ltd.",
    "T-Mobile US, Inc.",
    "GE Vernova Inc.",
    "International Business Machines",
    "LVMH EO 0,3",
    "Linde plc",
    "Royal Bank Of Canada",
    "McDonald's Corporation",
    "Intel Corporation",
    "NESR.DE",
    "Verizon Communications Inc.",
    "SAP SE US8030542042 SAP",
    "Pepsico, Inc.",
    "American Express Company",
    "AT&T Inc.",
    "KLA Corporation",
    "HSBC HOLDINGS PLC ORD $0.50 (UK",
    "SHELL PLC ORD EUR0.07",
    "Citigroup, Inc.",
    "Amgen Inc.",
    "NextEra Energy, Inc.",
    "Abbott Laboratories",
    "Salesforce, Inc.",
    "SAP SE",
    "Walt Disney Company (The)",
    "Thermo Fisher Scientific Inc",
    "TJX Companies, Inc. (The)",
    "Texas Instruments Incorporated",
    "Gilead Sciences, Inc.",
    "Intuitive Surgical, Inc.",
    "Charles Schwab Corporation (The",
    "BHP Group Limited",
]

# script to activate getting quotes for financial instrument
# declare FI to activate in FITS_TO_ACTIVATE list and run this script
from dataclasses import dataclass, field
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine
# importing models from zb_quotes package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from zb_quotes.models.models import Gfi, Timeframe, Qfi, Vfi, VfiTimeSeries

# ── Database connection ───────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
DATABASE_URL = os.getenv("DATABASE_URL") # e.g., "sqlite:////path/to/your/database.db" defined in .env file
print(f"DEBUG: DATABASE_URL = {DATABASE_URL}")
engine = create_engine(DATABASE_URL, echo=False)


# ── What to activate ───────────────────────────────────────────────────────
@dataclass
class TsFi:
    time_frames:list[str] = field(default_factory=lambda: ['1d'])
    gfi_name:   str = None
    qfi_name:   str = None
    vfit_name:  str = None

FITS_TO_ACTIVATE = [
    # TsFi(gfi_name="PGE", time_frames=["1d"]),
    # TsFi(gfi_name='TAURONPE'),
    # TsFi(gfi_name='PKNORLEN'),
    # TsFi(gfi_name='KGHM'),
]

for gfi_name in GFI_NAMES_2_ACTIVATE:
    FITS_TO_ACTIVATE.append(TsFi(gfi_name=gfi_name, time_frames=["1d"]))
for gfi_name in GFI_NAMES_2_ACTIVATE_2:
    FITS_TO_ACTIVATE.append(TsFi(gfi_name=gfi_name, time_frames=["1d"]))




# ── Helper functions ───────────────────────────────────────────────────────
def get_gfi_qfi_vfi(session, gfi_name, qfi_name, vfit_name)->tuple[Gfi, Qfi, Vfi]:
    gfi, qfi, vfi = None, None, None
    
    if gfi_name:
        stmt = select(Gfi).where(Gfi.name == gfi_name)
        gfi = session.execute(stmt).scalar_one_or_none()
    if qfi_name:
        stmt = select(Qfi).where(Qfi.name == qfi_name)
        qfi = session.execute(stmt).scalar_one_or_none()
    if vfit_name:
        stmt = select(Vfi).where(Vfi.name == vfit_name)
        vfi = session.execute(stmt).scalar_one_or_none()
    return gfi, qfi, vfi

def activate_quotes_version_orig(time_frame: str, 
                    gfi_name:   str = None, 
                    qfi_name:   str = None, 
                    vfit_name:  str = None) -> bool:
    try:
        session: Session
        with Session(engine) as session:
            gfi, qfi, vfi = get_gfi_qfi_vfi(session, gfi_name, qfi_name, vfit_name)
            if vfi:
                vif_id = vfi.id
            elif qfi:
                if len(qfi.vfis) > 1:
                    raise ValueError(f"Multiple VFI '{vfit_name}' found for QFI '{qfi_name}'")
                else:
                    vfi_id = qfi.vfis[0].id
            elif gfi:
                if len(gfi.qfis) > 1:
                    raise ValueError(f"Multiple QFI found for GFI '{gfi.name}'")
                else:
                    if len(gfi.qfis[0].vfis) > 1:
                        raise ValueError(f"Multiple VFI found for QFI '{gfi.qfis[0].name}'")
                    else:
                        vfi_id = gfi.qfis[0].vfis[0].id
            
            stmt = select(Timeframe).where(Timeframe.code == time_frame)
            timeframe = session.execute(stmt).scalar_one_or_none()
            if not timeframe:
                raise ValueError(f"Timeframe '{time_frame}' not found")
            timeframe_id = timeframe.id
            
            # TODO: Create VfiTimeSeries record
            stmt = select(VfiTimeSeries).where(VfiTimeSeries.vfi_id == vfi_id, VfiTimeSeries.timeframe_id == timeframe_id)
            vfits = session.execute(stmt).scalar_one_or_none()
            if not vfits:
                raise ValueError(f"Timeframe '{time_frame}' not found")
            
            vfits.enabled = True
            session.commit()
            print(f"Activated quotes for {gfi_name if gfi_name else '--'} {qfi_name if qfi_name else '--'} {vfit_name if vfit_name else '--'} timeframe '{time_frame}'")
            return True
    except Exception as e:
        print(f"Error activating quotes: {e}")
        return False

def activate_quotes(time_frame: str, 
                    gfi_name:   str = None, 
                    qfi_name:   str = None, 
                    vfit_name:  str = None) -> bool:
    try:
        session: Session
        with Session(engine) as session:
            vfits = get_vfits(time_frame, gfi_name, qfi_name, vfit_name, session)
            if not vfits:
                raise ValueError(f"VFI Time Series not found for timeframe '{time_frame}' and GFI '{gfi_name}', QFI '{qfi_name}', or VFI '{vfit_name}'")
            else:
                if not vfits.enabled:
                    vfits.enabled = True
                    session.commit()
                    print(f"Activated quotes for {gfi_name if gfi_name else '--'} {qfi_name if qfi_name else '--'} {vfit_name if vfit_name else '--'} timeframe '{time_frame}'")
                    return True
                else:
                    print(f"Quotes for {gfi_name if gfi_name else '--'} {qfi_name if qfi_name else '--'} {vfit_name if vfit_name else '--'} timeframe '{time_frame}' are already active")
                    return False
    except Exception as e:
        print(f"Error activating quotes: {e}")
        return False

def deactivate_quotes(time_frame: str, 
                      gfi_name:   str = None, 
                      qfi_name:   str = None, 
                      vfit_name:  str = None) -> bool:
    try:
        session: Session
        with Session(engine) as session:
            vfits = get_vfits(time_frame, gfi_name, qfi_name, vfit_name, session)
            if not vfits:
                raise ValueError(f"VFI Time Series not found for timeframe '{time_frame}' and GFI '{gfi_name}', QFI '{qfi_name}', or VFI '{vfit_name}'")
            else: 
                if vfits.enabled:
                    vfits.enabled = False
                    session.commit()
                    print(f"Deactivated quotes for {gfi_name if gfi_name else '--'} {qfi_name if qfi_name else '--'} {vfit_name if vfit_name else '--'} timeframe '{time_frame}'")
                    return True
                else:
                    print(f"Quotes for {gfi_name if gfi_name else '--'} {qfi_name if qfi_name else '--'} {vfit_name if vfit_name else '--'} timeframe '{time_frame}' are already inactive")
                    return True
    except Exception as e:
        print(f"Error deactivating quotes: {e}")
        return False


def get_vfits(time_frame: str, 
             gfi_name:   str, 
             qfi_name:   str, 
             vfit_name:  str, 
             session:    Session) -> VfiTimeSeries:
    gfi, qfi, vfi = get_gfi_qfi_vfi(session, gfi_name, qfi_name, vfit_name)
    vfi_id = None
    
    if vfi:
        vfi_id = vfi.id
    elif qfi:
        if len(qfi.vfis) > 1:
            raise ValueError(f"Multiple VFI '{vfit_name}' found for QFI '{qfi_name}'")
        else:
            vfi_id = qfi.vfis[0].id
    elif gfi:
        if len(gfi.qfis) > 1:
            raise ValueError(f"Multiple QFI found for GFI '{gfi.name}'")
        else:
            if len(gfi.qfis[0].vfis) > 1:
                raise ValueError(f"Multiple VFI found for QFI '{gfi.qfis[0].name}'")
            else:
                vfi_id = gfi.qfis[0].vfis[0].id
    
    if vfi_id is None:
        raise ValueError(f"No VFI found for GFI '{gfi_name}', QFI '{qfi_name}', or VFI '{vfit_name}'")
    
    stmt = select(Timeframe).where(Timeframe.code == time_frame)
    timeframe = session.execute(stmt).scalar_one_or_none()
    if not timeframe:
        raise ValueError(f"Timeframe '{time_frame}' not found")
    timeframe_id = timeframe.id
    
    # TODO: Create VfiTimeSeries record
    stmt = select(VfiTimeSeries).where(VfiTimeSeries.vfi_id == vfi_id, VfiTimeSeries.timeframe_id == timeframe_id)
    vfits = session.execute(stmt).scalar_one_or_none()
    return vfits


def main():
    c = [0,0]
    for tsvi in FITS_TO_ACTIVATE:
        for tf_code in tsvi.time_frames:
            result = activate_quotes(
                time_frame=tf_code,
                gfi_name=  tsvi.gfi_name,
                qfi_name=  tsvi.qfi_name,
                vfit_name= tsvi.vfit_name
            )
            if result:
                c[0] += 1
            else:
                c[1] += 1
    print('-----------------------------')
    print('   summary of activation')
    print(f"Activated: {c[0]}, Not activated: {c[1]}")

if __name__ == "__main__":
    main()