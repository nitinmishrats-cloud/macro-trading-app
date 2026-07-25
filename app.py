import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")

st.title("🚀 10X Engine v4 (Pro Scanner)")
st.caption("Clean Data | Momentum | Smart Scoring | Realistic Output")

# --- Load NSE Stock List ---
url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
nse_df = pd.read_csv(url)

tickers = nse_df["SYMBOL"].tolist()
tickers = [t + ".NS" for t in tickers]

# Limit scan for performance
tickers = tickers[:300]

results = []

st.info(f"🔎 Scanning {len(tickers)} stocks...")

for t in tickers:
    try:
        stock = yf.Ticker(t)
        info = stock.info

        pe = info.get("trailingPE", 0) or 0
        growth = info.get("revenueGrowth", 0) or 0
        roe = info.get("returnOnEquity", 0) or 0
        debt = info.get("debtToEquity", 0) or 0

        # --- Skip missing critical data ---
        if pe <= 0 or growth <= 0:
            continue

        # --- REMOVE JUNK DATA ---
        if growth > 1:   # >100%
            continue
        if roe > 0.6:    # >60%
            continue

        # --- PRICE MOMENTUM FILTER ---
        hist = stock.history(period="6mo")

        if len(hist) < 50:
            continue

        price_return = (hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1

        # Skip falling stocks
        if price_return < 0:
            continue

        # --- PEG ---
        peg = pe / (growth * 100)

        # --- SCORING ---
        score = 0
        penalty = 0

        # Growth
        if growth > 0.25:
            score += 30
        elif growth > 0.15:
            score += 20
        else:
            score += 10

        # ROE
        if roe > 0.20:
            score += 25
        elif roe > 0.15:
            score += 15
        else:
            score += 5

        # PEG
        if peg < 1:
            score += 25
        elif peg < 1.5:
            score += 15
        else:
            score += 5

        # Debt
        if debt < 0.3:
            score += 20
        elif debt < 0.6:
            score += 10
        else:
            score += 5

        # --- PENALTIES ---
        if peg > 1.5:
            penalty += 10
        if roe < 0.15:
            penalty += 10
        if growth < 0.12:
            penalty += 10
        if debt > 0.6:
            penalty += 10

        final_score = score - penalty

        # --- CONVICTION TAG ---
        if final_score >= 80:
            tag = "🔥 Strong"
        elif final_score >= 65:
            tag = "👍 Good"
        else:
            tag = "⚠️ Watch"

        results.append({
            "Stock": t,
            "Score": round(final_score, 2),
            "Growth %": round(growth * 100, 2),
            "ROE %": round(roe * 100, 2),
            "PEG": round(peg, 2),
            "Debt": round(debt, 2),
            "6M Return %": round(price_return * 100, 2),
            "Conviction": tag
        })

    except:
        continue

df = pd.DataFrame(results)

st.write(f"Total stocks scanned: {len(tickers)}")
st.write(f"Valid stocks after filters: {len(df)}")

if not df.empty:
    df = df.sort_values(by="Score", ascending=False)

    st.success("🏆 Top 15 High-Conviction Stocks")
    st.dataframe(df.head(15), use_container_width=True)

else:
    st.error("No strong stocks found. Market may be weak.")
