import streamlit as st
import pandas as pd
import os

from scanner import run_batch
from fundamental_parser import process_data


# -----------------------------
# Page Setup
# -----------------------------

st.set_page_config(
    page_title="NSE 10X Scanner V12",
    layout="wide"
)


st.title("🚀 NSE 10X Multibagger Scanner V12")


st.write(
"""
Scanner objective:

Find companies with:
- Market Cap ₹1,000 Cr - ₹10,000 Cr
- Good ROCE / ROE
- Reasonable valuation
- Potential long-term growth
"""
)


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header(
    "Scanner Settings"
)


batch_size = st.sidebar.slider(
    "Stocks to scan today",
    min_value=1,
    max_value=500,
    value=50
)



# -----------------------------
# Run Scanner
# -----------------------------

if st.button(
    "🚀 Run Daily Scan"
):


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
        "Running fundamental filters..."
    ):


        df = process_data()



    if df is None or len(df)==0:


        st.error(
            "No stocks passed the filters"
        )

        st.stop()



    st.success(
        f"Found {len(df)} potential candidates"
    )



# -----------------------------
# Display Existing Results
# -----------------------------

if os.path.exists(
    "data/processed_database.csv"
):


    df = pd.read_csv(
        "data/processed_database.csv"
    )


    st.subheader(
        "🔥 NSE 10X Watchlist"
    )


    # Sort by score

    if "Quality Score" in df.columns:


        df = df.sort_values(
            "Quality Score",
            ascending=False
        )



    # Display columns

    display_columns = [

        "Symbol",
        "Market Cap (Cr)",
        "Stock P/E",
        "ROCE (%)",
        "ROE (%)",
        "Quality Score",
        "Risk"

    ]


    available_columns = [

        c for c in display_columns
        if c in df.columns

    ]


    st.dataframe(
        df[available_columns],
        use_container_width=True
    )



    st.download_button(

        label="📥 Download Watchlist",

        data=df.to_csv(
            index=False
        ),

        file_name=
        "NSE_10X_Watchlist.csv"

    )


else:


    st.info(
        """
        No database available.

        Click Run Daily Scan first.
        """
    )
