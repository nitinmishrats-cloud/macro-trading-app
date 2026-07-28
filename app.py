import streamlit as st
import pandas as pd

from scanner import run_batch
from fundamental_parser import process_data


st.set_page_config(
    page_title="NSE 10X Scanner V12",
    layout="wide"
)


st.title("🚀 NSE 10X Multibagger Scanner V12")


st.write(
"""
Automatic NSE opportunity scanner

Filters:
- Market Cap ₹1,000 Cr - ₹10,000 Cr
- ROCE / ROE quality
- Valuation check
- Long term multibagger screening
"""
)


# -----------------------------
# Sidebar
# -----------------------------

batch_size = st.sidebar.slider(
    "Stocks to scan today",
    1,
    500,
    50
)



# -----------------------------
# Run Scan
# -----------------------------

if st.button("🚀 Run Daily Scan"):


    with st.spinner(
        "Collecting Screener data..."
    ):

        raw = run_batch(
            batch_size
        )


    st.success(
        f"Collected {len(raw)} companies"
    )


    with st.spinner(
        "Processing fundamentals..."
    ):

        df = process_data()



    if df is None or len(df)==0:

        st.error(
            "No stocks passed filters"
        )

        st.stop()



    st.success(
        f"Found {len(df)} potential candidates"
    )


    # Save in session

    st.session_state["results"] = df



# -----------------------------
# Show Results
# -----------------------------

if "results" in st.session_state:


    df = st.session_state["results"]


    st.subheader(
        "🔥 NSE 10X Watchlist"
    )


    if "Quality Score" in df.columns:

        df = df.sort_values(
            "Quality Score",
            ascending=False
        )



    columns = [

        "Symbol",
        "Market Cap (Cr)",
        "Stock P/E",
        "ROCE (%)",
        "ROE (%)",
        "Quality Score",
        "Risk"

    ]


    columns = [
        c for c in columns
        if c in df.columns
    ]


    st.dataframe(
        df[columns],
        use_container_width=True
    )


    st.download_button(

        "📥 Download CSV",

        df.to_csv(index=False),

        "NSE_10X_candidates.csv"

    )

else:

    st.info(
        "Click Run Daily Scan"
    )
