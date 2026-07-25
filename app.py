import streamlit as st
import yfinance as yf
import pandas as pd

st.title("🚀 10X Engine – Full NSE Scanner")

st.info("📡 Fetching NSE stock universe...")

# Step 1: Get NSE list
url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
nse_df = pd.read_csv(url)

# Step 2: Convert symbols
tickers = nse_df["SYMBOL"].tolist()
tickers = [t + ".NS" for t in tickers]

# Limit scan (IMPORTANT)
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

        if pe == 0 or growth == 0:
            continue

        peg = pe / (growth * 100) if growth > 0 else 999

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

        # Penalty
        if peg > 1.5:
            penalty += 10
        if roe < 0.15:
            penalty += 10
        if growth < 0.12:
            penalty += 10
        if debt > 0.6:
            penalty += 10

        final_score = score - penalty

        results.append({
            "Stock": t,
            "Score": final_score,
            "Growth %": growth * 100,
            "ROE %": roe * 100,
            "PEG": peg,
            "Debt": debt
        })

    except:
        continue

df = pd.DataFrame(results)

st.write(f"Total stocks scanned: {len(tickers)}")
st.write(f"Valid stocks analyzed: {len(df)}")

if not df.empty:
    df = df.sort_values(by="Score", ascending=False)

    st.success("🏆 Top 15 Opportunities")
    st.dataframe(df.head(15), use_container_width=True)

else:
    st.error("No stocks found. Try again.")
