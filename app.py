# =========================================
# 🚀 V9 INDIA PRO - STABLE SCREENER ENGINE
# =========================================

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import streamlit as st
import time

st.set_page_config(layout="wide")
st.title("🚀 V9 INDIA PRO - NSE 10x Screener (Stable)")

# ================================
# 📥 NSE STOCK LIST (FIXED)
# ================================
@st.cache_data(ttl=86400)
def get_nse_stocks():
    try:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        df = pd.read_csv(url)

        # ✅ CLEAN COLUMN NAMES (CRITICAL FIX)
        df.columns = df.columns.str.strip().str.upper()

        # ✅ SAFE FILTER
        if "SERIES" in df.columns:
            df = df[df["SERIES"] == "EQ"]

        symbols = df["SYMBOL"].dropna().tolist()

        return symbols

    except Exception as e:
        st.error(f"NSE fetch failed: {e}")
        # fallback
        return ["RELIANCE", "TCS", "INFY", "HDFCBANK"]


# ================================
# 🔍 SCREENER SCRAPER (ROBUST)
# ================================
@st.cache_data(ttl=86400)
def get_screener_data(symbol):
    try:
        url = f"https://www.screener.in/company/{symbol}/"
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        def get_value(label):
            try:
                x = soup.find("span", string=label)
                if x:
                    return x.find_next("span").text
                return np.nan
            except:
                return np.nan

        def clean(x):
            try:
                return float(str(x).replace("%", "").replace(",", "").strip())
            except:
                return np.nan

        return {
            "roe": clean(get_value("ROE")),
            "roce": clean(get_value("ROCE")),
            "pe": clean(get_value("P/E")),
            "debtToEquity": clean(get_value("Debt to equity")),
            "salesGrowth_3Y": clean(get_value("Sales growth 3Years")),
            "profitGrowth_3Y": clean(get_value("Profit growth 3Years")),
            "promoterHolding": clean(get_value("Promoter holding")),
        }

    except:
        return None


# ================================
# 📈 PRICE DATA
# ================================
@st.cache_data(ttl=86400)
def get_price(symbol):
    try:
        stock = yf.Ticker(symbol + ".NS")
        hist = stock.history(period="1y")

        if hist.empty or len(hist) < 200:
            return None

        return {
            "price_6M_return": ((hist["Close"].iloc[-1] / hist["Close"].iloc[-126]) - 1) * 100,
            "above_200DMA": hist["Close"].iloc[-1] > hist["Close"].rolling(200).mean().iloc[-1]
        }

    except:
        return None


# ================================
# 🔄 LOAD STOCKS
# ================================
tickers = get_nse_stocks()

# ⚠️ LIMIT FOR SPEED
MAX_STOCKS = 120
tickers = tickers[:MAX_STOCKS]

data = []

with st.spinner(f"Scanning {len(tickers)} stocks..."):
    for symbol in tickers:

        f = get_screener_data(symbol)
        p = get_price(symbol)

        if not f or not p:
            continue

        row = {"symbol": symbol}
        row.update(f)
        row.update(p)

        data.append(row)

        time.sleep(1)  # IMPORTANT (avoid blocking)

df = pd.DataFrame(data)

# ================================
# 🛑 HANDLE EMPTY DATA
# ================================
if df.empty:
    st.warning("No data found. Try reducing filters or increasing stock limit.")
    st.stop()

# ================================
# 🧠 DERIVED METRICS
# ================================
df["peg"] = df["pe"] / df["profitGrowth_3Y"]

# ================================
# 🚫 BASE FILTERS
# ================================
df = df[
    (df["promoterHolding"] > 50) &
    (df["debtToEquity"] < 1.5)
]

# ================================
# 📈 GROWTH FILTER
# ================================
df = df[
    (df["salesGrowth_3Y"] > 10) &
    (df["profitGrowth_3Y"] > 12)
]

# ================================
# ⚖️ QUALITY
# ================================
df = df[
    (df["roe"] > 15) &
    (df["roce"] > 15)
]

# ================================
# 🧠 PEG FILTER
# ================================
df = df[(df["peg"] > 0) & (df["peg"] < 1.5)]

# ================================
# 🔥 MOMENTUM
# ================================
df = df[
    (df["price_6M_return"] > 20) &
    (df["above_200DMA"] == True)
]

# ================================
# 🚨 REMOVE CYCLICAL SPIKES
# ================================
df = df[df["profitGrowth_3Y"] < 80]

# ================================
# 🏆 SCORING
# ================================
df["score"] = (
    df["salesGrowth_3Y"] * 0.25 +
    df["profitGrowth_3Y"] * 0.3 +
    df["roe"] * 0.2 +
    df["price_6M_return"] * 0.15 +
    (1 / df["peg"]) * 10 * 0.1
)

df = df.sort_values(by="score", ascending=False)

# ================================
# 📊 OUTPUT
# ================================
st.subheader("🏆 Top 10x Candidates")
st.dataframe(df.head(20))
