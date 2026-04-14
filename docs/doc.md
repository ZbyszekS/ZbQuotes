# Fetching quote data from Yahoo Finance:
uses yf.download() with:
- ticker_list - list of tickers to download
- interval    - interval of data to download ex. 1m, 1h, 1d...
- auto_adjust - whether to adjust data for splits and dividends => False
- actions     - whether to include dividends and splits in data => True

- time_window - time window for data to download
    - period - period of data to download ex. 1d, 1w, 1mo...
    - fetch_range - start and end dates for data to download

# Max length for ticker list 
- is unspecified for sure
- but it is recommended to keep it under 100-200 tickers
- longer lists -> less request => positive, because yfinance has limits on requests per time unit

# For db writings I need:
- vfi_ts_id
- timestamp or date
- quote values