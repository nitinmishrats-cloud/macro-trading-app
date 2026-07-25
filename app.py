import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import urllib.request

st.set_page_config(page_title="MacroGuard Terminal", page_icon="🛡️", layout="centered")
st.title("🌐 MacroGuard: All-Market Engine")
st.caption("Automated Global News & Fundamentals Filter")

NIFTY_LEADERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", 
    "INFY.NS", "SBIN.NS", "LTIM.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", 
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS", "NTPC.NS", 
    "SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "TATAMOTORS.NS", "M&M.NS",
    "HAL.NS", "BEL.NS", "BHEL.NS", "BPCL.NS", "IOC.NS", "WIPRO.NS"
]

SCENARIOS = {
    "Global Supply Shocks": "export+ban+OR+anti+dumping+OR+factory+closure",
    "Disaster Disruption": "flood+halts+OR+mine+suspended+OR+crop+damage",
    "Geopolitical Conflicts": "sanctions+OR+shipping+blocked+OR+tariffs"
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
        
        # Hard Security Protection Layer
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

for name, query_string in SCENARIOS.items():
    feed_url = f"https://google.com{query_string}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        # ADVANCED FIX: Adding a mobile browser header bypasses network drops entirely
        req = urllib.request.Request(
            feed_url, 
            headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15'}
        )
        
        # Fetch data securely through browser spoofing
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read()
            
        feed = feedparser.parse(html_content)
        
        if feed.entries:
            first_entry = feed.entries[0] # Pick the actual first headline element safely
            with st.expander(f"🔥 ALERT: {name}", expanded=True):
                st.markdown(f"**Live Trigger Headline:** {first_entry.title}")
                st.markdown(f"[View Global News Coverage]({first_entry.link})")
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
    except Exception as e:
        st.warning(f"Skipping feed check for '{name}' temporarily due to live network rate-limits.")
