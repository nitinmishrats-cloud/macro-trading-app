import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import urllib.parse

st.set_page_config(page_title="MacroGuard Terminal", page_icon="🛡️", layout="centered")
st.title("🌐 MacroGuard: All-Market Engine")
st.caption("Automated Global News & Fundamentals Filter")

# Core Nifty benchmarks to screen cross-sector market leaders instantly on mobile
NIFTY_LEADERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", 
    "INFY.NS", "SBIN.NS", "LTIM.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", 
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS", "NTPC.NS", 
    "SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "TATAMOTORS.NS", "M&M.NS",
    "HAL.NS", "BEL.NS", "BHEL.NS", "BPCL.NS", "IOC.NS", "WIPRO.NS"
]

SCENARIOS = {
    "Global Supply Shocks": ["export ban", "anti-dumping", "factory closure", "supply shortage"],
    "Disaster Disruption": ["flood halts", "mine suspended", "crop damage", "refinery fire"],
    "Geopolitical Conflicts": ["sanctions", "shipping blocked", "military spending", "tariffs"]
}

def analyze_any_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        company_sector = info.get("sector", "Other Sectors")
        company_name = info.get("shortName", ticker)
        pe_ratio = info.get("trailingPE", None)
        roe = (info.get("returnOnEquity", 0) or 0) * 100
        debt = (info.get("debtToEquity", 0) or 0) / 100
        
        # UNDER THE HOOD SHIELDS: Drop junk stocks instantly
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

st.info("🔄 Scraping macro events and executing multi-point structural checks...")

for name, keywords in SCENARIOS.items():
    query = urllib.parse.quote(" OR ".join([f'"{k}"' for k in keywords[:2]]))
    feed = feedparser.parse(f"https://google.com{query}&hl=en-US&gl=US&ceid=US:en")
    
    if feed.entries:
        entry = feed.entries[0]
        with st.expander(f"🔥 ALERT: {name}", expanded=True):
            st.markdown(f"**Live Trigger Headline:** {entry.title}")
            st.markdown(f"[View Global News Coverage]({entry.link})")
            st.markdown("**🛡️ Governance-Approved Opportunities Found:**")
            
            vetted_opportunities = []
            for ticker in NIFTY_LEADERS:
                analysis = analyze_any_stock(ticker)
                if analysis:
                    vetted_opportunities.append(analysis)
            
            if vetted_opportunities:
                df = pd.DataFrame(vetted_opportunities)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.caption("No stocks currently satisfy corporate governance safety buffers for this event.")
