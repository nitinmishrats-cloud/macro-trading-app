import pandas as pd
import os


INPUT_FILE = "data/database.csv"
OUTPUT_FILE = "data/processed_database.csv"


def calculate_quality_score(row):

    score = 0


    # ROCE
    if pd.notna(row["ROCE (%)"]):

        if row["ROCE (%)"] >= 25:
            score += 3

        elif row["ROCE (%)"] >= 15:
            score += 2



    # ROE
    if pd.notna(row["ROE (%)"]):

        if row["ROE (%)"] >= 20:
            score += 2

        elif row["ROE (%)"] >= 12:
            score += 1



    # Valuation
    if pd.notna(row["Stock P/E"]):

        if row["Stock P/E"] < 25:
            score += 2

        elif row["Stock P/E"] < 40:
            score += 1



    return score



def process_data():


    if not os.path.exists(INPUT_FILE):

        return None



    df = pd.read_csv(
        INPUT_FILE
    )



    # Convert N/A to numeric

    numeric_columns = [

        "Market Cap (Cr)",
        "Stock P/E",
        "ROCE (%)",
        "ROE (%)"

    ]


    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )



    # Your 10X sweet spot

    df = df[
        (df["Market Cap (Cr)"] >= 1000)
        &
        (df["Market Cap (Cr)"] <= 10000)
    ]



    # Quality score

    df["Quality Score"] = df.apply(
        calculate_quality_score,
        axis=1
    )



    # Basic risk flags

    df["Risk"] = "LOW"


    df.loc[
        df["ROCE (%)"] < 10,
        "Risk"
    ] = "MEDIUM"



    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    return df
