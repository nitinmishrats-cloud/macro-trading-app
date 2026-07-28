import pandas as pd
import re
import os


INPUT_FILE = "data/database.csv"
OUTPUT_FILE = "data/processed_database.csv"


# -------------------------------------
# Extract value from Screener text
# -------------------------------------

def get_value(text, keyword):

    try:

        pattern = keyword + r"\s*([\d\.]+)"

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return float(
                match.group(1)
            )

    except:
        pass

    return None



# -------------------------------------
# Parse company
# -------------------------------------

def parse_company(row):

    text = str(row["Raw"])


    data = {

        "Symbol":
        row["Symbol"],


        "Date":
        row["Date"],


        "MarketCap":
        get_value(
            text,
            "Market Cap"
        ),


        "PE":
        get_value(
            text,
            "Stock P/E"
        ),


        "ROCE":
        get_value(
            text,
            "ROCE"
        ),


        "Debt":
        get_value(
            text,
            "Debt"
        ),


        "Promoter":
        get_value(
            text,
            "Promoter holding"
        ),


        "Pledge":
        get_value(
            text,
            "Pledged"
        )

    }


    return data



# -------------------------------------
# Quality Score
# -------------------------------------

def quality_score(row):

    score = 0


    # ROCE

    if pd.notna(row["ROCE"]):

        if row["ROCE"] >= 25:
            score += 3

        elif row["ROCE"] >= 15:
            score += 2



    # Debt

    if pd.notna(row["Debt"]):

        if row["Debt"] == 0:
            score += 3

        elif row["Debt"] < 1:
            score += 2



    # Promoter

    if pd.notna(row["Promoter"]):

        if row["Promoter"] >= 50:
            score += 2

        elif row["Promoter"] >= 35:
            score += 1



    # Pledge

    if pd.notna(row["Pledge"]):

        if row["Pledge"] == 0:
            score += 2


    return score



# -------------------------------------
# Process Database
# -------------------------------------

def process_data():


    if not os.path.exists(INPUT_FILE):

        return None



    raw = pd.read_csv(
        INPUT_FILE
    )


    companies=[]


    for _,row in raw.iterrows():

        companies.append(
            parse_company(row)
        )



    df=pd.DataFrame(
        companies
    )


    # Calculate score

    df["Quality Score"] = (
        df.apply(
            quality_score,
            axis=1
        )
    )


    # Risk classification

    df["Governance Risk"]="LOW"



    df.loc[
        df["Pledge"] > 10,
        "Governance Risk"
    ]="HIGH"



    df.loc[
        df["Debt"] > 2,
        "Governance Risk"
    ]="MEDIUM"



    # Save

    os.makedirs(
        "data",
        exist_ok=True
    )


    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    return df
