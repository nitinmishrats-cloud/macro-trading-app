import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import numpy as np

st.set_page_config(layout="wide")

st.title("🚀 10X Engine PRO (Full NSE Scanner)")
st.caption("All Stocks | Governance | Momentum | Smart Alerts")

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "YOUR_API_KEY"   # replace if available

# -----------------------------
# STEP 1: LOAD NSE STOCK LIST
# -----------------------------
@st.cache_data(ttl=86400)
def load_nse_list():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    df["ticker"] = df["SYMBOL"] + ".NS"
    return df

nse_df = load_nse_list()
tickers = nse_df["ticker"].tolist()

st.info(f"🔎 Total NSE Stocks: {len(tickers)}")

# -----------------------------
# STEP 2: TRY API (FAST)
# -----------------------------
def fetch_api_data():
    try:
        url = f"https://data.businessquant.com/screener?api_key={API_KEY}"

        payload = {
            "filters": [
                {"metric": "revenue_growth", "operator": ">", "value": 0.1},
                {"metric": "roe", "operator": ">", "value": 0.12},
                {"metric": "debt_to_equity", "operator": "<", "value": 0.6}
            ],
            "columns": [
                "symbol",
                "revenue_growth",
                "roe",
                "pe_ratio",
                "debt_to_equity",
                "promoter_holding",
                "pledged_percent"
            ],
            "limit": 2000
        }

        r = requests.post(url, json=payload)
        data = r.json()

        df = pd.DataFrame(data["data"])
        df["ticker"] = df["symbol"] + ".NS"

        return df

    except:
        return None

api_df = fetch_api_data()

# -----------------------------
# STEP 3: FALLBACK (YFINANCE)
# -----------------------------
def fallback_data():
    results = []

    progress = st.progress(0)

    for i, t in enumerate(tickers[:500]):  # limit fallback
        try:
            stock = yf.Ticker(t)
            info = stock.info

            results.append({
                "ticker": t,
                "revenue_growth": info.get("revenueGrowth", 0),
                "roe": info.get("returnOnEquity", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "debt_to_equity": info.get("debtToEquity", 0),
                "promoter_holding": info.get("heldPercentInsiders", 0) * 100,
                "pledged_percent": 0
            })

        except:
            continue

        progress.progress((i + 1) / 500)

    return pd.DataFrame(results)

if api_df is None or api_df.empty:
    st.warning("API failed, using fallback (limited scan)...")
    df = fallback_data()
else:
    df = api_df

# -----------------------------
# STEP 4: GOVERNANCE FILTER
# -----------------------------
df = df[
    (df["promoter_holding"] > 50) &
    (df["pledged_percent"] < 5)
]

# -----------------------------
# STEP 5: MOMENTUM FILTER
# -----------------------------
@st.cache_data(ttl=3600)
def get_price_data(tickers):
    data = yf.download(tickers, period="6mo", group_by="ticker", threads=True)
    return data

price_data = get_price_data(df["ticker"].tolist())

momentum_list = []

for t in df["ticker"]:
    try:
        hist = price_data[t]

        if len(hist) < 50:
            continue

        ret = (hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1

        if ret > 0:
            momentum_list.append((t, ret))

    except:
        continue

momentum_df = pd.DataFrame(momentum_list, columns=["ticker", "return"])

df = df.merge(momentum_df, on="ticker")

# -----------------------------
# STEP 6: SCORING
# -----------------------------
df["PEG"] = df["pe_ratio"] / (df["revenue_growth"] * 100)

def score(row):
    s = 0

    # Growth
    if row["revenue_growth"] > 0.25:
        s += 30
    elif row["revenue_growth"] > 0.15:
        s += 20
    else:
        s += 10

    # ROE
    if row["roe"] > 0.20:
        s += 25
    elif row["roe"] > 0.15:
        s += 15
    else:
        s += 5

    # PEG
    if row["PEG"] < 1:
        s += 25
    elif row["PEG"] < 1.5:
        s += 15
    else:
        s += 5

    # Debt
    if row["debt_to_equity"] < 0.3:
        s += 20
    elif row["debt_to_equity"] < 0.6:
        s += 10
    else:
        s += 5

    return s

df["Score"] = df.apply(score, axis=1)

df = df.sort_values(by="Score", ascending=False)

# -----------------------------
# STEP 7: ALERT SYSTEM
# -----------------------------
def check_new_entries(df):
    try:
        old = pd.read_csv("last_run.csv")
        new = df.head(15)

        new_stocks = set(new["ticker"]) - set(old["ticker"])

        if len(new_stocks) > 0:
            st.warning(f"🚨 NEW STOCKS FOUND: {list(new_stocks)}")

        new.to_csv("last_run.csv", index=False)

    except:
        df.head(15).to_csv("last_run.csv", index=False)

check_new_entries(df)

# -----------------------------
# OUTPUT
# -----------------------------
st.success("🏆 Top 15 High-Conviction Stocks")
st.dataframe(df.head(15), use_container_width=True)
