# app.py
import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
from sklearn.linear_model import LinearRegression

from db import *
from api import get_prices, get_market
from utils import calc
from auth import create_token, verify_token
from report import create_pdf
from email_utils import send_email
from live_ticker import live_ticker
from trading_chart import show_chart

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide")
create_tables()

# ---------------- STYLING ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#020617,#0f172a);
    color:white;
}
.card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 20px;
}
h1,h2,h3 {color:#38bdf8;}
</style>
""", unsafe_allow_html=True)

# ---------------- CACHE ----------------
@st.cache_data(ttl=60)
def load_prices():
    return get_prices()

@st.cache_data(ttl=60)
def load_market():
    return get_market()

# ---------------- SESSION ----------------
if "token" not in st.session_state:
    st.session_state.token = None

user = verify_token(st.session_state.token)

# ---------------- LOGIN ----------------
if not user:
    st.title("🔐 Crypto Portfolio Manager")

    menu = st.radio("Select", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Login":
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.token = create_token(username)
                st.rerun()
            else:
                st.error("Invalid Login")

    elif menu == "Signup":
        if st.button("Create Account"):
            if add_user(username, password):
                st.success("Account created! Please login.")
            else:
                st.error("Username already exists")
# ---------------- MAIN APP ----------------
if user:

    st.sidebar.title(f"👤 {user}")

    page = st.sidebar.radio(
        "Menu",
        ["Dashboard","Market","Trading","Portfolio","Alerts","AI"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.rerun()

    # 🔄 Manual Refresh Button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    # ---------------- FETCH DATA ----------------
    with st.spinner("Loading Market Data..."):
        time.sleep(0.5)

    prices = load_prices()

    # ---------------- DASHBOARD ----------------
    if page == "Dashboard":
        st.title("📊 Live Dashboard")

        live_ticker()

        st.subheader("Market Table")

        try:
            df_market = load_market()
        except:
            df_market = pd.DataFrame()
            st.error("API Error")

        if not df_market.empty:

            search = st.text_input("🔍 Search coin")
            if search:
                df_market = df_market[df_market["Name"].str.contains(search, case=False)]

            top_n = st.slider("Top N coins", 5, 50, 20)
            df_market = df_market.head(top_n)

            def color_change(val):
                if val > 0:
                    return "color: green"
                elif val < 0:
                    return "color: red"
                return ""

            styled_df = df_market.style.map(color_change, subset=["24h Change (%)"])
            styled_df = styled_df.format({
                "Price ($)": "${:,.2f}",
                "Market Cap": "${:,.0f}",
                "Volume": "${:,.0f}",
                "24h Change (%)": "{:.2f}%"
            })

            st.dataframe(styled_df, width="stretch")

    # ---------------- MARKET ----------------
    elif page == "Market":
        st.title("📊 Crypto Market")

        try:
            df_market = load_market()
        except:
            df_market = pd.DataFrame()
            st.warning("Market API unavailable")

        if not df_market.empty:

            search = st.text_input("🔍 Search coin")
            if search:
                df_market = df_market[df_market["Name"].str.contains(search, case=False)]

            top_n = st.slider("Top N coins", 5, 50, 20)
            df_market = df_market.head(top_n)

            def color_change(val):
                if val > 0:
                    return "color: green"
                elif val < 0:
                    return "color: red"
                return ""

            styled_df = df_market.style.map(color_change, subset=["24h Change (%)"])
            styled_df = styled_df.format({
                "Price ($)": "${:,.2f}",
                "Market Cap": "${:,.0f}",
                "Volume": "${:,.0f}",
                "24h Change (%)": "{:.2f}%"
            })

            st.dataframe(styled_df, width="stretch")

    # ---------------- TRADING ----------------
    elif page == "Trading":
        st.title("📈 Trading Chart")
        show_chart()

    # ---------------- PORTFOLIO ----------------
    elif page == "Portfolio":
        st.title("💼 Portfolio")

        coin = st.text_input("Coin")
        inv = st.number_input("Investment")
        cur = st.number_input("Current")

        if st.button("Add Asset"):
            add_crypto(coin, inv, cur)
            st.rerun()

        data = get_data()
        df = pd.DataFrame(data, columns=["Coin","Investment","Current"])

        if not df.empty:
            df = calc(df)

            c1,c2,c3 = st.columns(3)
            c1.metric("💰 Investment", int(df["Investment"].sum()))
            c2.metric("📈 Profit", int(df["Profit"].sum()))
            c3.metric("🪙 Coins", len(df))

            st.dataframe(df)

            fig = px.bar(df, x="Coin", y="Profit", title="Profit Chart")
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            pie = px.pie(df, names="Coin", values="Investment", title="Portfolio Allocation")
            st.plotly_chart(pie)

            d = st.selectbox("Delete Coin", df["Coin"])
            if st.button("Delete"):
                delete_coin(d)
                st.rerun()

            pdf = create_pdf(data)
            with open(pdf,"rb") as f:
                st.download_button("Download PDF", f)

    # ---------------- ALERTS ----------------
    elif page == "Alerts":
        st.title("🚨 Alerts")

        coin = st.selectbox("Coin", list(prices.keys()))
        target = st.number_input("Target Price")
        email = st.text_input("Email")

        if st.button("Set Alert"):
            add_alert(coin, target)
            st.success("Alert Added!")

        alerts = get_alerts()
        alerts = get_alerts()

        for c, t, sent in alerts:
           if c in prices:
             price = prices[c].get("usd", 0)

             if price >= t and sent == 0:
                 st.warning(f"{c.upper()} reached {t}")

                 if email:
                   if send_email(email, c, price):
                     mark_alert_sent(c, t)

    # ---------------- AI ----------------
    elif page == "AI":
        st.title("🤖 Prediction")

        X = np.array([1,2,3,4,5]).reshape(-1,1)
        y = np.array([100,200,300,400,500])

        model = LinearRegression()
        model.fit(X,y)

        d = st.slider("Days Ahead",1,10)
        pred = model.predict([[d]])

        st.success(f"Predicted Price: {pred[0]:.2f}")