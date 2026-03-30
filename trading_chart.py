import streamlit as st
import plotly.graph_objects as go
from api import get_candles

def show_chart():
    coin = st.selectbox("Coin", ["bitcoin","ethereum","solana"])
    df = get_candles(coin)

    fig = go.Figure(data=[go.Candlestick(
        x=df["time"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"]
    )])

    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig)