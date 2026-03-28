from dataclasses import dataclass

@dataclass
class QfiInput:
    gfi_name: str
    market_name: str
    currency_name: str
    quoted_unit_name: str
    qfi_name: str
    qfi_description: str
    quoted_amount: int
    
@dataclass
class VtsInput:
    vendor_ticker: str
    ts_name: str
QFI_SEED = [
    QfiInput(gfi_name="PGE", market_name="WSE", currency_name="PLN", quoted_unit_name="STOCK", qfi_name="PGE", qfi_description="PGE", quoted_amount=1),
]

VFI_TS_SEED = [
    VtsInput(vendor_ticker="PGE.WA", ts_name="1h"),
    VtsInput(vendor_ticker="TPE.WA", ts_name="1h"),
    VtsInput(vendor_ticker="PKO.WA", ts_name="1h"),
    VtsInput(vendor_ticker="INTC", ts_name="1h"),
    VtsInput(vendor_ticker="DBK.DE", ts_name="1h"),
    VtsInput(vendor_ticker="SAN", ts_name="1h"),
]
    