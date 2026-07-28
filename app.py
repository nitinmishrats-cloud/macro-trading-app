import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed


st.set_page_config(layout="wide")

st.title("🚀 NSE 10X Candidate Scanner V11.1")


# ----------------------------
# LOAD NSE STOCKS
# ----------------------------

@st.cache_data(ttl=86400)
def load_stocks():

    url="https://archives.nseindia.com/content/equities/EQUITY_L.csv"

    df=pd.read_csv(url)

    return df["SYMBOL"].tolist()


symbols=load_stocks()


# increase gradually
symbols=symbols[:1200]


# ----------------------------
# FETCH FUNDAMENTALS
# ----------------------------

def get_data(symbol):

    try:

        ticker=yf.Ticker(symbol+".NS")

        info=ticker.info


        return {

        "Stock":symbol,

        "MarketCap":
        info.get("marketCap",np.nan)/1e7,

        "PEG":
        info.get("pegRatio",np.nan),

        "PE":
        info.get("trailingPE",np.nan),

        "ROE":
        info.get("returnOnEquity",np.nan),

        "Debt":
        info.get("debtToEquity",np.nan),

        "RevenueGrowth":
        info.get("revenueGrowth",np.nan),

        "ProfitGrowth":
        info.get("earningsGrowth",np.nan)

        }


    except:

        return None



# ----------------------------
# PARALLEL DOWNLOAD
# ----------------------------

results=[]


with ThreadPoolExecutor(max_workers=20) as exe:


    jobs=[
        exe.submit(get_data,s)
        for s in symbols
    ]


    for job in as_completed(jobs):

        r=job.result()

        if r:

            results.append(r)



df=pd.DataFrame(results)



st.write(
"Companies scanned:",
len(df)
)



# ----------------------------
# CLEAN DATA
# ----------------------------


# DO NOT DROP ALL NA


df=df[
(df["MarketCap"]>1000)
&
(df["MarketCap"]<10000)
]


# PEG filter
df=df[
(df["PEG"].notna())
&
(df["PEG"]>0)
&
(df["PEG"]<1.5)
]



# ----------------------------
# MULTIBAGGER SCORE
# ----------------------------


def score(row):

    s=0


    # PEG

    if row["PEG"]<1:
        s+=3

    elif row["PEG"]<1.5:
        s+=2



    # ROE

    if pd.notna(row["ROE"]):

        if row["ROE"]>0.20:
            s+=3

        elif row["ROE"]>0.15:
            s+=2



    # Debt

    if pd.notna(row["Debt"]):

        if row["Debt"]<50:
            s+=2



    # Growth

    if pd.notna(row["RevenueGrowth"]):

        if row["RevenueGrowth"]>0.15:
            s+=2



    if pd.notna(row["ProfitGrowth"]):

        if row["ProfitGrowth"]>0.15:
            s+=2


    return s



df["Score"]=df.apply(score,axis=1)



df=df.sort_values(
"Score",
ascending=False
)



# ----------------------------
# DISPLAY
# ----------------------------


st.subheader("🔥 Top 50 10X Candidates")


st.dataframe(
df.head(50),
use_container_width=True
)


st.write(
"Final candidates:",
len(df)
)
