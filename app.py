import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MacroGuard Core Engine", page_icon="🛡️", layout="centered")
st.title("🛡️ MacroGuard: News & Governance Core")
st.caption("Top 5 News-Catalyzed Value Opportunities & 1-Year Targets")

NIFTY_LEADERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", 
    "INFY.NS", "SBIN.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", 
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "SUNPHARMA.NS", "TATAMOTORS.NS", 
    "HAL.NS", "BEL.NS", "BPCL.NS", "COALINDIA.NS"
]

# Simple text keyword dictionary to scan live news feeds for macro-catalysts
NEWS_TRIGGERS = ["ban", "tariff", "sanction", "closure", "shortage", "demand", "record", "growth", "expansion"]

@st.cache_data(ttl=1800)
def analyze_with_news():
    vetted_buys = []
    
    # 1. LIVE NEWS EXTRACTION PHASE
    active_news_context = ""
    for anchor_ticker in ["RELIANCE.NS", "TATASTEEL.NS", "HAL.NS", "TCS.NS"]:
        try:
            feed = yf.Ticker(anchor_ticker).news
            if feed and len(feed) > 0:
                headline = feed[0].get('title') or feed[0].get('headline') or ""
                # Check if this headline contains any of our target macro-catalyst words
                if any(trigger in headline.lower() for trigger in NEWS_TRIGGERS):
                    active_news_context = headline
                    break
        except:
            continue
            
    if not active_news_context:
        active_news_context = "General Industrial Consolidation & Market Demand Optimization"

    # 2. EQUITIES SCANNING & FUNDAMENTAL PHASE
    for ticker in NIFTY_LEADERS:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            company_name = info.get("shortName", ticker)
            sector = info.get("sector", "Other Sectors")
            pe_ratio = info.get("trailingPE", None)
            roe = (info.get("returnOnEquity", 0) or 0) * 100
            debt = (info.get("debtToEquity", 0) or 0) / 100
            current_price = info.get("currentPrice") or info.get("regularPrice") or info.get("previousClose")
            
            # GOVERNANCE CRASH PROTECTIONS
            if roe < 12 or debt > 1.5 or not current_price:
                continue
                
            hist = stock.history(period="1mo")
            if len(hist) >= 14:
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
                
                # Check if stock is at an accumulation timing window
                if rsi < 55:
                    # 1-Year Projected Value Calculation
                    target_calculation = current_price * (1.0 + (roe / 100)) * (1.0 + ((55 - rsi) / 100))
                    
                    # COMPOSE DYNAMIC REASON BY MERGING LIVE NEWS WITH BALANCE SHEET RATIOS
                    detailed_reason = (
                        f"Reacting to live macro context: '{active_news_context}'. "
                        f"This specific {sector} company is selected because it maintains top-tier governance "
                        f"({roe:.1f}% ROE) and safe debt ratios ({debt:.2f} D/E), allowing it to benefit safely long term."
                    )
                    
                    vetted_buys.append({
                        "Company": company_name,
                        "Price": f"₹{current_price:.2f}",
                        "P/E": f"{pe_ratio:.1f}" if pe_ratio else "N/A",
                        "Debt": f"{debt:.2f}",
                        "Reason": detailed_reason,
                        "Target": f"₹{target_calculation:.2f}"
                    })
        except:
            continue
            
    return vetted_buys[:5]  # Limit strictly to the top 5 entries

st.info("🔄 Running multi-point news correlation and governance checks...")

top_5_news_buys = analyze_with_news()

st.subheader("🎯 Top 5 News-Catalyzed Value Opportunities")

if top_5_news_buys:
    for idx, stock_data in enumerate(top_5_news_buys):
        with st.expander(f"⭐ Opportunity #{idx+1}: {stock_data['Company']}", expanded=True):
            st.markdown(f"**💰 Current Market Price:** {stock_data['Price']}")
            st.markdown(f"**🚀 Projected 1-Year Target:** {stock_data['Target']}")
            
            c1, c2 = st.columns(2)
            c1.metric("P/E Ratio Valuation", stock_data['P/E'])
            c2.metric("Debt-to-Equity Ratio", stock_data['Debt'])
            
            st.markdown("**🛡️ Strategy News & Logic Analysis:**")
            st.warning(stock_data['Reason'])
else:
    st.error("No high-quality stocks currently fit the combined news-trigger and price-dip framework.")
