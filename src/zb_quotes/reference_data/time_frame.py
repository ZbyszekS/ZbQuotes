from zb_quotes.models.models import Quote_1day, Quote_1hour, Quote_1min, Quote_1month, Quote_1week


class TIME_FRAME:
    class ID:
        _1m = 1
        _1h = 2
        _1d = 3
        _1w = 4
        _1M = 5

    TO_QUOTE_MODEL = {
        ID._1m: Quote_1min,
        ID._1h: Quote_1hour,
        ID._1d: Quote_1day,
        ID._1w: Quote_1week,
        ID._1M: Quote_1month
    }

    YF_MAX_PERIOD_ALLOWED = {
        ID._1m: False,
        ID._1h: True,
        ID._1d: True,
        ID._1w: True,
        ID._1M: True,
    }

    YF_TF_NAME = {
        ID._1m: "1m",
        ID._1h: "1h",
        ID._1d: "1d",
        ID._1w: "1w",
        ID._1M: "1M"
    }