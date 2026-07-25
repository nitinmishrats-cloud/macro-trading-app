import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MacroGuard Terminal", page_icon="🛡️", layout="centered")
st.title("🌐 MacroGuard: All-Market Engine")
st.caption("Automated Market News & Fundamentals Filter")

# Core Nifty benchmarks to screen cross-sector market leaders instantly on mobile
NIFTY_LEADERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", 
    "INFY.NS", "SBIN.NS", "LTIM.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", 
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS", "NTPC.NS", 
    "SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "TATAMOTORS.NS", "M&M.NS",
    "HAL.NS", "BEL.NS", "BHEL.NS", "WIPRO.NS"
]

def analyze_any_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        company_sector = info.get("sector", "Other Sectors")
        company_name = info.get("shortName", ticker)
        pe_ratio = info.get("trailingPE", None)
        roe = (info.get("returnOnEquity", 0) or 0) * 100
        debt = (info.get("debtToEquity", 0) or 0) / 100
        
        # Hard Security Protection Layer: Drop junk stocks instantly
        if roe < 12 or debt > 1.5:
            return None 
            
        hist = stock.history(period="1mo")
        if len(hist) >= 14:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            signal = "🟢 BUY ZONE" if rsi < 45 else "🟡 HOLD / WATCH"
            
            return {
                "Company": company_name,
                "Sector": company_sector,
                "P/E": f"{pe_ratio:.1f}" if pe_ratio else "N/A",
                "ROE": f"{roe:.1f}%",
                "Debt/Equity": f"{debt:.2f}",
                "Recommendation": signal
            }
        return None
    except:
        return None

st.info("🔄 Running multi-point structural checks over the Indian market...")

# Core Indian Market Headlines Section
st.subheader("📰 Recent Corporate Signals & News")

news_found = False
# Scan market leaders to fetch official news feeds directly from Yahoo Finance data portals
for ticker in ["RELIANCE.NS", "TATASTEEL.NS", "HAL.NS", "TCS.NS"]:
    try:
        stock_obj = yf.Ticker(ticker)
        ticker_news = stock_obj.news
        
        if ticker_news:
            # Grab the single freshest corporate article for this marker
            latest_story = ticker_news[0]
            news_found = True
            
            with st.expander(f"🔥 SIGNAL BREAKOUT: {ticker.replace('.NS','')}", expanded=True):
                st.markdown(f"**Headline:** {latest_story.get('title')}")
                st.markdown(f"[View Full Article Source]({latest_story.get('link')})")
                st.markdown("**🛡️ Governance-Approved Structural Opportunities Available:**")
                
                vetted_opportunities = []
                for lead_ticker in NIFTY_LEADERS:
                    analysis = analyze_any_stock(lead_ticker)
                    if analysis:
                        vetted_opportunities.append(analysis)
                
                if vetted_opportunities:
                    df = pd.DataFrame(vetted_opportunities)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.caption("No stocks currently satisfy corporate governance safety buffers.")
    except:
        continue

if not news_found:
    st.warning("Yahoo Finance data engines are updating information matrices. Please refresh in a moment.")
