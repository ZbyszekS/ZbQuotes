import requests

def search_yahoo_ticker(query: str, limit: int = 10):
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": query, "quotesCount": limit, "newsCount": 0}

    r = requests.get(url, params=params)
    data = r.json()

    results = []
    for item in data.get("quotes", []):
        results.append({
            "symbol": item.get("symbol"),
            "shortname": item.get("shortname"),
            "longname": item.get("longname"),
            "exchange": item.get("exchange"),
            "type": item.get("quoteType"),
        })

    return results
