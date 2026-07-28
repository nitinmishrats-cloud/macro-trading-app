import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

st.title("🚀 NSE Multibagger Scanner V11 (Governance + News Filter)")

# -------- LOAD NSE STOCK LIST --------
@st.cache_data
def load_nse_stocks():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    return df["SYMBOL"].tolist()

symbols = load_nse_stocks()
symbols = symbols[:800]  # stability limit

# -------- FETCH DATA --------
def fetch_stock(symbol):
    try:
        stock = yf.Ticker(symbol + ".NS")
        info = stock.info

        return {
            "symbol": symbol,
            "market_cap": info.get("marketCap", np.nan) / 1e7,
            "pe": info.get("trailingPE", np.nan),
            "peg": info.get("pegRatio", np.nan),
            "debt_to_equity": info.get("debtToEquity", np.nan),
            "roe": info.get("returnOnEquity", np.nan),
            "revenue_growth": info.get("revenueGrowth", np.nan),
            "profit_growth": info.get("earningsGrowth", np.nan),
        }
    except:
        return None

# -------- MULTITHREAD --------
data = []
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(fetch_stock, s) for s in symbols]

    for future in as_completed(futures):
        res = future.result()
        if res:
            data.append(res)

df = pd.DataFrame(data)
df = df.dropna()

# -------- STAGE 1: GOVERNANCE FILTER --------
df = df[
    (df["debt_to_equity"] < 0.6) &   # low debt
    (df["roe"] > 0.15)               # efficient business
]

# -------- STAGE 2: CORE MULTIBAGGER FILTER --------
df = df[
    (df["market_cap"] > 1000) & (df["market_cap"] < 10000) &
    (df["peg"] > 0) & (df["peg"] < 1)
]

# -------- STAGE 3: NEWS RISK FILTER (PROXY) --------
df = df[
    (df["revenue_growth"] > 0) &
    (df["profit_growth"] > 0)
]

# -------- RISK FLAGS --------
df["risk_flag"] = np.where(
    (df["debt_to_equity"] > 0.5) |
    (df["roe"] < 0.18),
    "⚠️ Medium Risk",
    "✅ Low Risk"
)

# -------- SCORE SYSTEM --------
df["score"] = (
    df["roe"] * 0.3 +
    df["revenue_growth"] * 0.25 +
    df["profit_growth"] * 0.25 +
    (1 - df["peg"]) * 0.2
)

df = df.sort_values(by="score", ascending=False)

# -------- OUTPUT --------
st.write("### 🔥 Top Multibagger Candidates (V11)")
st.dataframe(df.head(25))

st.write(f"Total stocks found: {len(df)}")
