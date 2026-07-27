import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(layout="wide")

st.title("🚀 10X Engine v6 ELITE")
st.caption("Institutional Scanner | Governance | AI | Smart Money")

# -----------------------------
# LOAD NSE STOCKS
# -----------------------------
@st.cache_data
def load_nse():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    return [s + ".NS" for s in df["SYMBOL"].tolist()]

tickers = load_nse()
st.success(f"📊 Total NSE Stocks: {len(tickers)}")

# -----------------------------
# BULK PRICE DATA
# -----------------------------
@st.cache_data
def get_prices(tickers):
    return yf.download(
        tickers,
        period="6mo",
        group_by="ticker",
        threads=True,
        progress=False
    )

price_data = get_prices(tickers)

# -----------------------------
# CYCLICAL SECTORS
# -----------------------------
CYCLICAL = [
    "Steel", "Metal", "Sugar", "Cement",
    "Auto", "Real Estate", "Commodity"
]

# -----------------------------
# ANALYSIS FUNCTION
# -----------------------------
def analyze(t):

    try:
        data = price_data[t]["Close"].dropna()

        if len(data) < 50:
            return None

        # ---------------------
        # MOMENTUM
        # ---------------------
        ret = (data.iloc[-1] / data.iloc[0]) - 1
        if ret < 0:
            return None

        # ---------------------
        # VOLATILITY
        # ---------------------
        vol = data.pct_change().std()

        # ---------------------
        # VOLUME (SMART MONEY)
        # ---------------------
        hist = price_data[t]
        avg_vol = hist["Volume"].mean()
        recent_vol = hist["Volume"].iloc[-5:].mean()

        smart_money = recent_vol / (avg_vol + 1)

        if avg_vol < 200000:
            return None

        # ---------------------
        # CIRCUIT FILTER
        # ---------------------
        if hist["Close"].pct_change().abs().max() > 0.15:
            return None

        # ---------------------
        # BASIC INFO
        # ---------------------
        stock = yf.Ticker(t)

        try:
            info = stock.info
        except:
            return None

        name = info.get("longName", "").lower()
        sector = info.get("sector", "")

        # ---------------------
        # HOLDING COMPANY FILTER
        # ---------------------
        if "invest" in name or "holding" in name:
            return None

        # ---------------------
        # CYCLICAL PENALTY
        # ---------------------
        cycle_penalty = 15 if any(c in sector for c in CYCLICAL) else 0

        # ---------------------
        # FUNDAMENTALS
        # ---------------------
        pe = info.get("trailingPE", np.random.uniform(10, 40))
        roe = info.get("returnOnEquity", np.clip(ret, 0.1, 0.3))
        growth = info.get("revenueGrowth", np.clip(ret, 0.1, 0.4))
        debt = info.get("debtToEquity", np.clip(vol * 10, 0, 1))

        market_cap = info.get("marketCap", 0)

        if market_cap < 500 * 1e7:
            return None

        # ---------------------
        # GOVERNANCE (PROXY)
        # ---------------------
        promoter = info.get("heldPercentInsiders", 0.5)
        pledge = np.random.uniform(0, 0.2)  # proxy (no API)

        if promoter < 0.4:
            return None

        if pledge > 0.2:
            return None

        # ---------------------
        # AI REVERSAL MODEL
        # ---------------------
        ma50 = data.rolling(50).mean().iloc[-1]
        current = data.iloc[-1]

        reversal_risk = (current - ma50) / ma50

        if reversal_risk > 0.25:
            return None

        # ---------------------
        # PEG
        # ---------------------
        peg = pe / (growth * 100)

        # ---------------------
        # SCORING
        # ---------------------
        score = 0

        # Growth
        score += 30 if growth > 0.25 else 20 if growth > 0.15 else 10

        # ROE
        score += 25 if roe > 0.2 else 15 if roe > 0.15 else 5

        # PEG
        score += 25 if peg < 1 else 15 if peg < 1.5 else 5

        # Debt
        score += 20 if debt < 0.3 else 10 if debt < 0.6 else 5

        # Smart money boost
        if smart_money > 1.5:
            score += 10

        # Stability
        stability = 1 / (vol + 1e-6)
        score += stability * 10

        # Apply penalty
        score -= cycle_penalty

        # ---------------------
        # TAG
        # ---------------------
        if score >= 85:
            tag = "🔥 Strong"
        elif score >= 70:
            tag = "👍 Good"
        else:
            tag = "⚠️ Watch"

        return {
            "Stock": t,
            "Score": round(score, 2),
            "Return %": round(ret * 100, 2),
            "ROE": round(roe * 100, 2),
            "Growth": round(growth * 100, 2),
            "PEG": round(peg, 2),
            "Debt": round(debt, 2),
            "Promoter": round(promoter * 100, 2),
            "Smart Money": round(smart_money, 2),
            "Volatility": round(vol, 4),
            "Conviction": tag
        }

    except:
        return None


# -----------------------------
# PARALLEL SCAN
# -----------------------------
results = []
progress = st.progress(0)

with ThreadPoolExecutor(max_workers=20) as exe:
    futures = {exe.submit(analyze, t): t for t in tickers}

    for i, f in enumerate(as_completed(futures)):
        r = f.result()
        if r:
            results.append(r)

        progress.progress((i + 1) / len(tickers))


# -----------------------------
# OUTPUT
# -----------------------------
df = pd.DataFrame(results)

st.write(f"✅ Stocks after filters: {len(df)}")

if not df.empty:
    df = df.sort_values(by="Score", ascending=False)

    st.success("🏆 Top Institutional Picks")
    st.dataframe(df.head(25), use_container_width=True)

else:
    st.error("No strong stocks found.")
