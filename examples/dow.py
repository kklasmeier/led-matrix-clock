#!/usr/bin/env python3
"""
Fetch today's point change for Dow, S&P 500, and Nasdaq using
FMP's /stable/quote-short endpoint, one request per symbol.

API key is hard-coded below for simplicity.
"""

import json
import urllib.request

API_KEY = "mSfv65dpPcaXHOWPJnGEXtu9HDOkzYVQ"   # <--- your key here

API_URL = "https://financialmodelingprep.com/stable/quote-short?symbol={symbol}&apikey={api_key}"

SYMBOLS = {
    "^DJI": "Dow",
    "^GSPC": "S&P",
    "^IXIC": "Nasdaq",
}

def get_quote(symbol: str):
    """Fetch quote JSON for one symbol"""
    url = API_URL.format(symbol=symbol, api_key=API_KEY)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    return data[0] if data else {}

def main():
    for sym, label in SYMBOLS.items():
        q = get_quote(sym)
        change = q.get("change", 0)
        sign = "+" if change >= 0 else ""
        print(f"{label} {sign}{int(round(change))}")

if __name__ == "__main__":
    main()
