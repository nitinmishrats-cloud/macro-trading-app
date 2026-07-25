import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import io
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(page_title="10X Engine", page_icon="🚀", layout="centered")
st.title("🚀 10X Stock Engine (High Conviction)")
st.caption("Focused Portfolio | PEG < 1.2 | High ROE | Structural Growth")

# -------------------------------
# FETCH NSE STOCKS
# -------------------------------
@st.cache_data(ttl=43200)
def fetch_tickers():
    try:
        url = "https://raw.githubusercontent.com/stockindia/nse-data/main/nse_all_stocks.csv"
        res = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(res.text))

        symbols = df.iloc[:, 0].dropna().unique().tolist()
        return [f"{s}.NS" for s in symbols if len(str(s)) > 1]

    except:
        fallback = ["DIXON", "KAYNES", "HAL", "BEL", "MAZDOCK", "ASTRAL", "SRF"]
        return [f"{t}.NS" for t in fallback]


# -------------------------------
# HIGH GROWTH THEMES
# -------------------------------
THEMES = [
    "technology",
    "defense",
    "industrial",
    "manufacturing",
    "chemical",
    "renewable",
    "electronics"
]


# -------------------------------
# 10X SCORING ENGINE
# -------------------------------
@st.cache_data(ttl=3600)
def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)

        hist = stock.history(period="6mo")
        if hist.empty:
            return None

        price = hist["Close"].iloc[-1]

        fast = stock.fast_info
        mcap = fast.get("market_cap", 0)

        if not mcap:
            return None

        mcap_cr = mcap / 1e7

        # Focus: 1k Cr to 50k Cr sweet spot
        if mcap_cr < 1000 or mcap_cr > 50000:
            return None

        info = stock.info

        sector = (info.get("sector") or "").lower()
        name = info.get("shortName", ticker)

        pe = info.get("trailingPE") or 0
        peg = info.get("pegRatio") or 0
        roe = info.get("returnOnEquity") or 0
        debt = (info.get("debtToEquity") or 0) / 100
        rev = info.get("revenueGrowth") or 0
        earn = info.get("earningsGrowth") or 0

        # -------------------------------
        # HARD FILTERS (STRICT)
        # -------------------------------
        if "financial" in sector or "bank" in sector:
            return None

        if peg <= 0 or peg > 1.2:
            return None

        if roe < 0.18:
            return None

        if rev < 0.15:
            return None

        if debt > 0.5:
            return None

        # -------------------------------
        # SCORING
        # -------------------------------
        score = 0

        # Core financial strength
        if roe > 0.20:
            score += 20
        else:
            score += 15

        if rev > 0.20:
            score += 20
        else:
            score += 10

        if earn > rev:
            score += 20
        else:
            score += 10

        # Valuation
        if peg < 1:
            score += 20
        else:
            score += 10

        # Balance sheet
        if debt < 0.25:
            score += 10

        # Theme bonus
        if any(t in sector for t in THEMES):
            score += 10

        # -------------------------------
        # 10X POTENTIAL SCORE (CUSTOM)
        # -------------------------------
        potential = min(100, score)

        # Expected CAGR estimate
        est_cagr = min(0.30, roe + rev / 2)

        return {
            "Company": name,
            "Sector": sector.title(),
            "Price": f"₹{price:.2f}",
            "Market Cap": f"₹{mcap_cr:,.0f} Cr",
            "PEG": round(peg, 2),
            "ROE": f"{roe*100:.1f}%",
            "Revenue Growth": f"{rev*100:.1f}%",
            "Debt": f"{debt:.2f}",
            "Score": potential,
            "Est CAGR": f"{est_cagr*100:.1f}%"
        }

    except Exception as e:
        print(f"Error: {ticker} {e}")
        return None


# -------------------------------
# MAIN
# -------------------------------
st.info("🔍 Scanning market for 10X candidates...")

tickers = fetch_tickers()

results = []

# Limit for stability
for t in tickers[:60]:
    res = analyze_stock(t)
    if res:
        results.append(res)

if results:
    df = pd.DataFrame(results).sort_values(by="Score", ascending=False).head(10)

    st.subheader("🔥 Top 10 10X Candidates (High Conviction)")

    for i, row in df.iterrows():
        with st.expander(f"🚀 {row['Company']} | Score: {row['Score']}"):
            st.write(f"**Price:** {row['Price']}")
            st.write(f"**Market Cap:** {row['Market Cap']}")
            st.write(f"**Sector:** {row['Sector']}")
            
            c1, c2 = st.columns(2)
            c1.metric("PEG", row["PEG"])
            c2.metric("ROE", row["ROE"])

            c3, c4 = st.columns(2)
            c3.metric("Revenue Growth", row["Revenue Growth"])
            c4.metric("Debt", row["Debt"])

            st.success(f"📈 Estimated CAGR: {row['Est CAGR']}")

else:
    st.error("No high-conviction 10X candidates found.")
