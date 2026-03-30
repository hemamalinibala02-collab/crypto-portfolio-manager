from turtle import st

import requests
import pandas as pd

def get_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,solana,cardano,xrp",
            "vs_currencies": "usd"
        }
        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        # Validate response
        if not data or "bitcoin" not in data:
            raise Exception("Invalid API response")

        return data

    except Exception as e:
        print("API Error:", e)

        # 🔥 Fallback data (IMPORTANT)
        return {
            "bitcoin": {"usd": 65000},
            "ethereum": {"usd": 3200},
            "solana": {"usd": 150},
            "cardano": {"usd": 0.5},
            "xrp": {"usd": 0.6}
        }


import streamlit as st
import requests
import pandas as pd

@st.cache_data
def get_market():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1,
            "price_change_percentage": "24h"
        }

        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        df = pd.DataFrame(data)

        df = df[[
            "market_cap_rank",
            "name",
            "symbol",
            "current_price",
            "price_change_percentage_24h",
            "market_cap",
            "total_volume"
        ]]

        df.columns = [
            "Rank",
            "Name",
            "Symbol",
            "Price ($)",
            "24h Change (%)",
            "Market Cap",
            "Volume"
        ]

        return df

    except:
        return pd.DataFrame([
            {"Rank": 1, "Name": "Bitcoin", "Symbol": "BTC", "Price ($)": 65000, "24h Change (%)": 2.5, "Market Cap": 1e12, "Volume": 5e10}
        ])

import streamlit as st   # ✅ correct import
import requests
import pandas as pd

@st.cache_data
def get_candles(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin}/ohlc"
        params = {"vs_currency": "usd", "days": 1}

        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        df = pd.DataFrame(data, columns=["time","open","high","low","close"])
        return df

    except:
        return pd.DataFrame({
            "time": [1,2,3,4],
            "open": [100,110,120,130],
            "high": [120,130,140,150],
            "low": [90,100,110,120],
            "close": [110,120,130,140]
        })