import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


st.set_page_config(
    page_title="NSE 10X Scanner",
    layout="wide"
)


st.title("🚀 NSE 10X Multibagger Scanner V11.2")


# ============================================
# LOAD NSE STOCK LIST
# ============================================

@st.cache_data(ttl=86400)
def load_nse_stocks():

    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

    df = pd.read_csv(url)

    symbols = df["SYMBOL"].tolist()

    return symbols



symbols = load_nse_stocks()


st.write(
    f"Total NSE stocks available: {len(symbols)}"
)


# For Streamlit free stability
limit = st.sidebar.slider(
    "Stocks to scan",
    200,
    1500,
    500
)


symbols = symbols[:limit]



# ============================================
# FETCH DATA
# ============================================


def fetch_company(symbol):

    try:

        ticker = yf.Ticker(symbol + ".NS")

        info = ticker.fast_info


        market_cap = info.get(
            "market_cap",
            None
        )


        if market_cap is None:
            return None


        return {

            "Stock": symbol,

            "MarketCap":
            market_cap / 10000000,

        }


    except Exception:

        return None




def run_scan(symbols):

    output=[]


    progress = st.progress(0)

    completed=0


    with ThreadPoolExecutor(max_workers=15) as executor:


        jobs=[
            executor.submit(fetch_company,s)
            for s in symbols
        ]


        for job in as_completed(jobs):

            result=job.result()

            if result:
                output.append(result)


            completed += 1

            progress.progress(
                completed/len(symbols)
            )


    return pd.DataFrame(output)



# ============================================
# RUN SCANNER
# ============================================


if st.button("🚀 Start NSE Scan"):


    with st.spinner(
        "Downloading NSE data..."
    ):


        df = run_scan(symbols)



    st.write(
        "Companies downloaded:",
        len(df)
    )


    if df.empty:

        st.error(
            """
            No data received from Yahoo Finance.

            Possible reasons:
            1. Yahoo blocked requests
            2. Too many requests
            3. Temporary API issue

            Try again after some time or reduce stock count.
            """
        )

        st.stop()



    # ============================================
    # MARKET CAP FILTER
    # ============================================


    df = df[
        (df["MarketCap"] > 1000)
        &
        (df["MarketCap"] < 10000)
    ]



    if df.empty:

        st.warning(
            "No companies in ₹1000Cr-₹10000Cr range"
        )

        st.stop()



    # ============================================
    # QUALITY SCORING
    # ============================================


    df["Score"] = 0


    # Midcap sweet spot
    df["Score"] += 3



    # Random placeholder quality score
    # will be replaced by Screener data in V12

    df["Reason"] = (
        "Midcap opportunity - needs fundamental validation"
    )


    df=df.sort_values(
        "Score",
        ascending=False
    )


    st.success(
        f"Found {len(df)} companies"
    )


    st.subheader(
        "🔥 Potential 10X Watchlist"
    )


    st.dataframe(
        df.head(50),
        use_container_width=True
    )
