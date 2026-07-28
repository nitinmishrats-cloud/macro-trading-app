import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import ta
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(layout="wide")
st.title("🚀 V9 NSE Institutional Scanner")

# ==============================
# LOAD NSE STOCK LIST
# ==============================
@st.cache_data(ttl=86400)
def load_nse_stocks():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    symbols = df['SYMBOL'].tolist()
    return [s + ".NS" for s in symbols]

# ==============================
# BULK DATA FETCH
# ==============================
@st.cache_data(ttl=3600)
def fetch_data(symbols):
    return yf.download(
        tickers=symbols,
        period="1y",
        interval="1d",
        group_by='ticker',
        threads=True
    )

# ==============================
# ANALYSIS ENGINE (V9)
# ==============================
def analyze_stock(symbol, data):
    try:
        df = data[symbol].dropna()

        if len(df) < 120:
            return None

        close = df['Close']
        high = df['High']
        low = df['Low']
        volume_series = df['Volume']

        price = close.iloc[-1]
        volume = volume_series.iloc[-1]
        avg_vol = volume_series.rolling(20).mean().iloc[-1]

        # Liquidity filter
        if volume < 200000 or price < 20:
            return None

        # Indicators
        rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]
        sma200 = close.rolling(200).mean().iloc[-1]

        high_50 = high.rolling(50).max().iloc[-1]
        low_50 = low.rolling(50).min().iloc[-1]

        drawdown = (price - high_50) / high_50

        score = 0
        signals = []

        # =====================
        # TREND + STRUCTURE
        # =====================
        if price > sma50:
            score += 1
            signals.append("Above 50DMA")

        if sma50 > sma200:
            score += 1
            signals.append("Bullish Trend")

        # =====================
        # REVERSAL ZONE
        # =====================
        if rsi < 40:
            score += 1
            signals.append("Oversold")

        if price < sma50 * 1.05:
            score += 1
            signals.append("Near Support")

        # =====================
        # VOLUME ACCUMULATION
        # =====================
        if volume > 1.5 * avg_vol:
            score += 2
            signals.append("Volume Spike")

        # =====================
        # BREAKOUT SETUP
        # =====================
        if price >= high_50 * 0.95:
            score += 2
            signals.append("Near Breakout")

        # =====================
        # DRAWDOWN RECOVERY
        # =====================
        if drawdown > -0.25:
            score += 1
            signals.append("Strong Structure")

        # =====================
        # TREND SHIFT
        # =====================
        if close.iloc[-1] > sma50 and close.iloc[-10] < sma50:
            score += 2
            signals.append("Fresh Breakout")

        return {
            "Stock": symbol.replace(".NS", ""),
            "Price": round(price, 2),
            "RSI": round(rsi, 1),
            "Volume": int(volume),
            "Score": score,
            "Signals": ", ".join(signals)
        }

    except:
        return None

# ==============================
# PARALLEL SCAN
# ==============================
def run_scan(symbols, data):
    def task(symbol):
        return analyze_stock(symbol, data)

    with ThreadPoolExecutor(max_workers=25) as executor:
        results = list(executor.map(task, symbols))

    results = [r for r in results if r is not None]
    return pd.DataFrame(results)

# ==============================
# UI CONTROLS
# ==============================
st.sidebar.header("⚙️ Settings")

max_stocks = st.sidebar.slider("Max Stocks to Scan", 500, 2000, 1200)
min_score = st.sidebar.slider("Minimum Score", 1, 10, 5)

# ==============================
# MAIN EXECUTION
# ==============================
if st.button("🚀 Run Full Scan"):

    with st.spinner("Loading stocks..."):
        symbols = load_nse_stocks()

    symbols = symbols[:max_stocks]

    st.write(f"Scanning {len(symbols)} stocks...")

    with st.spinner("Fetching data..."):
        data = fetch_data(symbols)

    with st.spinner("Analyzing..."):
        df = run_scan(symbols, data)

    if df.empty:
        st.error("No results")
    else:
        df = df.sort_values(by="Score", ascending=False)
        df = df[df["Score"] >= min_score]

        st.success(f"Found {len(df)} strong candidates")

        st.subheader("🏆 Top Opportunities")
        st.dataframe(df.head(25), use_container_width=True)

        st.subheader("📊 Full Results")
        st.dataframe(df, use_container_width=True)
