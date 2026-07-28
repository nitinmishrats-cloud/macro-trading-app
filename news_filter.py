import pandas as pd
import feedparser
import urllib.parse
import os


INPUT_FILE = "data/processed_fundamentals.csv"
OUTPUT_FILE = "data/final_candidates.csv"


# ---------------------------------------
# Negative news keywords
# ---------------------------------------

NEGATIVE_WORDS = [

    "fraud",
    "scam",
    "investigation",
    "sebi",
    "forensic",
    "accounting issue",
    "auditor resignation",
    "default",
    "loan default",
    "pledge",
    "promoter selling",
    "money laundering",
    "raid",
    "arrest"

]


# ---------------------------------------
# Google News Search
# ---------------------------------------

def get_news(symbol):

    try:

        query = urllib.parse.quote(
            symbol + " stock"
        )

        url = (
            "https://news.google.com/rss/search?q="
            + query
        )


        feed = feedparser.parse(url)


        headlines=[]


        for item in feed.entries[:10]:

            headlines.append(
                item.title.lower()
            )


        return headlines


    except:

        return []



# ---------------------------------------
# Risk scoring
# ---------------------------------------

def calculate_news_risk(symbol):

    headlines = get_news(symbol)


    risk = 0

    reasons=[]


    for headline in headlines:

        for word in NEGATIVE_WORDS:

            if word in headline:


                risk += 1

                reasons.append(
                    word
                )


    if risk == 0:

        return (
            0,
            "Clean"
        )


    elif risk <= 2:

        return (
            1,
            "Monitor: "
            +
            ",".join(
                reasons
            )
        )


    else:

        return (
            2,
            "Avoid: "
            +
            ",".join(
                reasons
            )
        )



# ---------------------------------------
# Apply news filter
# ---------------------------------------

def run_news_filter():


    if not os.path.exists(INPUT_FILE):

        return None



    df = pd.read_csv(
        INPUT_FILE
    )


    risks=[]
    reasons=[]


    for symbol in df["Symbol"]:


        risk,reason = calculate_news_risk(
            symbol
        )


        risks.append(
            risk
        )

        reasons.append(
            reason
        )



    df["News Risk"] = risks

    df["News Comment"] = reasons



    # Remove dangerous companies

    df = df[
        df["News Risk"] < 2
    ]



    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    return df
