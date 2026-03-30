import streamlit as st
from api import get_prices
import pandas as pd

def market_dashboard():
    prices = get_prices()

    data = []
    for coin, val in prices.items():
        data.append({
            "Coin": coin,
            "Price": val.get("usd",0)
        })

    df = pd.DataFrame(data)
    st.dataframe(df)