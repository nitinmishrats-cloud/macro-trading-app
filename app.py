import streamlit as st
import pandas as pd
import os

from scanner import run_batch
from fundamental_parser import process_data
from news_filter import run_news_filter


st.set_page_config(
    page_title="NSE 10X Scanner V12",
    layout="wide"
)


st.title(
    "🚀 NSE 10X Multibagger Scanner V12"
)


st.write(
"""
Automatic NSE stock discovery engine.

Filters:
- Market Cap ₹1,000 Cr - ₹10,000 Cr
- Quality business
- Governance risk
- Negative news risk
- Long-term multibagger potential
"""
)



# ----------------------------------
# SIDEBAR
# ----------------------------------

st.sidebar.header(
    "Scanner Settings"
)


batch_size = 1


min_score = st.sidebar.slider(
    "Minimum quality score",
    1,
    10,
    5
)



# ----------------------------------
# RUN SCAN BUTTON
# ----------------------------------

if st.button(
    "🚀 Run Daily Scan"
):


    with st.spinner(
        "Scanning next NSE batch..."
    ):


        raw = run_batch(
            batch_size
        )

st.write("Columns:")
st.write(raw.columns)

st.write("Sample raw data:")

st.write(
    raw.head(1)["Raw"].values[0][:2000]
)

    st.success(
        f"Collected {len(raw)} companies"
    )



    with st.spinner(
        "Processing fundamentals..."
    ):


        processed = process_data()



    if processed is None:

        st.error(
            "No processed data available"
        )

        st.stop()



    st.success(
        "Fundamental analysis completed"
    )



    with st.spinner(
        "Checking news risks..."
    ):


        final = run_news_filter()



    if final is None:

        st.error(
            "News filter failed"
        )

        st.stop()



    st.success(
        "News screening completed"
    )



# ----------------------------------
# DISPLAY RESULTS
# ----------------------------------


if os.path.exists(
    "data/final_candidates.csv"
):


    df = pd.read_csv(
        "data/final_candidates.csv"
    )


    st.subheader(
        "🔥 10X Candidate Watchlist"
    )


    # Score filter

    if "Quality Score" in df.columns:

        df = df[
            df["Quality Score"]
            >= min_score
        ]



    # Ranking

    if "Quality Score" in df.columns:

        df=df.sort_values(
            "Quality Score",
            ascending=False
        )


    st.dataframe(
        df.head(50),
        use_container_width=True
    )



    st.download_button(
        label="Download CSV",
        data=df.to_csv(
            index=False
        ),
        file_name=
        "NSE_10X_candidates.csv"
    )


else:


    st.info(
        """
        No scan completed yet.

        Click 'Run Daily Scan'
        """
    )
