from zb_quotes.reference_data.time_frame import TIME_FRAME


class YF:
    # IS_MAX_PERIOD_ALLOWED = {
    #     TIME_FRAME.ID._1m: False,
    #     TIME_FRAME.ID._1h: True,
    #     TIME_FRAME.ID._1d: True,
    #     TIME_FRAME.ID._1w: True,
    #     TIME_FRAME.ID._1M: True
    # }

    MAX_PERIOD_CODE = "max"

    INTERVAL_NAME = {
        TIME_FRAME.ID._1m: "1m",
        TIME_FRAME.ID._1h: "1h",
        TIME_FRAME.ID._1d: "1d",
        TIME_FRAME.ID._1w: "1w",
        TIME_FRAME.ID._1M: "1M"
    }

    MAX_DAYS_BACK = {
        TIME_FRAME.ID._1m: 30,
        TIME_FRAME.ID._1h: 730,
        TIME_FRAME.ID._1d: None,
        TIME_FRAME.ID._1w: None,
        TIME_FRAME.ID._1M: None
    }

    MAX_DAYS_IN = {
        TIME_FRAME.ID._1m: 7,
        TIME_FRAME.ID._1h: MAX_DAYS_BACK[TIME_FRAME.ID._1h],
        TIME_FRAME.ID._1d: MAX_DAYS_BACK[TIME_FRAME.ID._1d],
        TIME_FRAME.ID._1w: MAX_DAYS_BACK[TIME_FRAME.ID._1w],
        TIME_FRAME.ID._1M: MAX_DAYS_BACK[TIME_FRAME.ID._1M]
    }

    class DF_COLS:
        SPLIT    = "Stock Splits"
        DIVIDEND = "Dividends"

    class TICKERS_PER_DOWNLOAD:
        MAX      = 100
        MODERATE =  50
        SAFE     =  30