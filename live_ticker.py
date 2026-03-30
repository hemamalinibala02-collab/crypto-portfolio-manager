import streamlit as st
from api import get_prices

def live_ticker():
    prices = get_prices()
    cols = st.columns(len(prices))
    

    for i, (coin, val) in enumerate(prices.items()):
        cols[i].metric(coin.upper(), f"${val.get('usd',0)}")