import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime


DATA_FILE = "data/database.csv"


# -----------------------------
# Load NSE Universe
# -----------------------------

def load_universe():

    url = (
        "https://archives.nseindia.com/"
        "content/equities/EQUITY_L.csv"
    )

    df = pd.read_csv(url)

    return df["SYMBOL"].tolist()



# -----------------------------
# Screener Extractor
# -----------------------------

def scrape_screener(symbol):

    try:

        url = (
            "https://www.screener.in/company/"
            + symbol
            + "/"
        )


        headers = {
            "User-Agent":
            "Mozilla/5.0"
        }


        r = requests.get(
            url,
            headers=headers,
            timeout=10
        )


        if r.status_code != 200:
            return None



        soup = BeautifulSoup(
            r.text,
            "lxml"
        )


        text = soup.get_text(
            " ",
            strip=True
        )


        return {

            "Symbol": symbol,

            "Date":
            datetime.now().strftime(
                "%Y-%m-%d"
            ),

            "Raw":
            text[:5000]

        }


    except:

        return None



# -----------------------------
# Batch Scanner
# -----------------------------

def run_batch(batch_size=100):


    symbols = load_universe()


    # Existing database

    if os.path.exists(DATA_FILE):

        old = pd.read_csv(
            DATA_FILE
        )

        scanned = set(
            old["Symbol"]
        )

    else:

        old = pd.DataFrame()

        scanned=set()



    # Pick next batch

    pending=[
        s for s in symbols
        if s not in scanned
    ]


    batch = pending[:batch_size]



    results=[]



    for i,symbol in enumerate(batch):

        print(
            "Scanning:",
            symbol
        )


        data=scrape_screener(
            symbol
        )


        if data:

            results.append(
                data
            )


        # avoid blocking

        time.sleep(1)



    new=pd.DataFrame(results)



    if len(old)>0:

        final=pd.concat(
            [
                old,
                new
            ],
            ignore_index=True
        )

    else:

        final=new



    os.makedirs(
        "data",
        exist_ok=True
    )


    final.to_csv(
        DATA_FILE,
        index=False
    )



    return final
