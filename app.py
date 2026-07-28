import streamlit as st
import pandas as pd

from scanner import run_batch


st.set_page_config(
    page_title="NSE 10X Scanner Debug",
    layout="wide"
)


st.title("🚀 NSE 10X Scanner V12 Debug")


st.write(
    "Testing Screener data extraction with one stock"
)


# ----------------------------------
# RUN TEST
# ----------------------------------

if st.button("Run Test Scan"):

    with st.spinner(
        "Scanning KPITTECH..."
    ):

        raw = run_batch(
            1
        )


    st.success(
        "Scan completed"
    )


    st.subheader(
        "Downloaded Data"
    )


    st.write(raw)


    if len(raw) > 0:


        st.subheader(
            "Raw Screener Text"
        )


        raw_text = raw.iloc[0]["Raw"]


        st.text(
            raw_text[:3000]
        )


    else:

        st.error(
            """
            No data received.

            Screener may be blocking the request.
            """
        )
