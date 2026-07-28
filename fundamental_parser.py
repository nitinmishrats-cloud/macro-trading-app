import pandas as pd
import re
import os


RAW_FILE = "data/database.csv"
OUTPUT_FILE = "data/processed_database.csv"


# ---------------------------------
# Extract numbers from text
# ---------------------------------

def extract_number(pattern, text):

    try:

        result = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if result:
            return float(
                result.group(1)
            )

    except:
        pass

    return None



# ---------------------------------
# Parse one company
# ---------------------------------

def parse_company(row):

    text = row["Raw"]


    data = {

        "Symbol":
        row["Symbol"],


        "Date":
        row["Date"],


        # Market Cap
        "MarketCap":
        extract_number(
            r"Market Cap\s*₹?\s*([\d,.]+)",
            text
        ),


        # PE
        "PE":
        extract_number(
            r"P/E\s*([\d,.]+)",
            text
        ),


        # ROCE
        "ROCE":
        extract_number(
            r"ROCE\s*([\d,.]+)",
            text
        ),


        # Debt
        "Debt":
        extract_number(
            r"Debt\s*([\d,.]+)",
            text
        ),


        # Promoter
        "Promoter":
        extract_number(
            r"Promoter Holding\s*([\d,.]+)",
            text
        ),


        # Pledge
        "Pledge":
        extract_number(
            r"Pledged\s*([\d,.]+)",
            text
        )

    }


    return data



# ---------------------------------
# PEG calculation
# ---------------------------------

def calculate_score(row):

    score = 0


    # ROCE

    if pd.notna(row["ROCE"]):

        if row["ROCE"] > 25:
            score += 3

        elif row["ROCE"] > 15:
            score += 2



    # Debt

    if pd.notna(row["Debt"]):

        if row["Debt"] < 0.5:
            score += 2



    # Promoter

    if pd.notna(row["Promoter"]):

        if row["Promoter"] > 50:
            score += 2



    # Pledge

    if pd.notna(row["Pledge"]):

        if row["Pledge"] == 0:
            score += 2


    return score



# ---------------------------------
# MAIN PROCESS
# ---------------------------------

def process_data():


    if not os.path.exists(RAW_FILE):

        return None



    raw = pd.read_csv(
        RAW_FILE
    )


    processed=[]


    for _,row in raw.iterrows():

        processed.append(
            parse_company(row)
        )


    df=pd.DataFrame(
        processed
    )


    df["Quality Score"] = (
        df.apply(
            calculate_score,
            axis=1
        )
    )


    # Governance flags

    df["Risk"] = "LOW"


    df.loc[
        df["Pledge"] > 10,
        "Risk"
    ] = "HIGH"


    df.loc[
        df["Debt"] > 1,
        "Risk"
    ] = "MEDIUM"



    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    return df
