import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MacroGuard Top 20", page_icon="🛡️", layout="centered")
st.title("🌐 MacroGuard: Institutional Terminal")
st.caption("Top 20 News-Catalyzed Value Opportunities (NSE Pool)")

# Core institutional NSE liquid tracker pool
NSE_700_POOL = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", 
    "ITC.NS", "HINDUNILVR.NS", "LT.NS", "TATAMOTORS.NS", "SUNPHARMA.NS", "AXISBANK.NS", "ONGC.NS",
    "TATASTEEL.NS", "HAL.NS", "BEL.NS", "NTPC.NS", "POWERGRID.NS", "JSWSTEEL.NS", "ADANIENT.NS",
    "COALINDIA.NS", "BPCL.NS", "IOC.NS", "GAIL.NS", "REC.NS", "PFC.NS", "BHEL.NS", "IRFC.NS",
    "HINDALCO.NS", "VEDL.NS", "NMDC.NS", "SAIL.NS", "NATIONALUM.NS", "ZOMATO.NS", "TATAPOWER.NS",
    "SUZLON.NS", "NHPC.NS", "SJVN.NS", "HUDCO.NS", "IRCTC.NS", "CONCOR.NS", "OIL.NS"
]

GOVERNANCE_WARNING_TERMS = ["sebi fine", "fraud", "scam", "pledge invocation", "auditor resigns", "investigation", "raid"]

NEWS_CATALYSTS = {
    "Black Swan / Disruption": ["shortage", "shutdown", "strike", "halt", "disaster", "ban"],
    "Government Policy / PLI": ["subsidy", "pli", "budget", "tariff", "duty hiked", "allocation"],
    "Tech & Innovation Boom": ["ai infrastructure", "semiconductor", "green hydrogen", "ev plant", "order win"]
}

@st.cache_data(ttl=3600)
def scan_and_analyze_market(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        company_name = info.get("shortName", ticker)
        sector = info.get("sector", "Other Sectors")
        pe_ratio = info.get("trailingPE", 0)
        debt_to_equity = (info.get("debtToEquity", 0) or 0) / 100
        current_price = info.get("currentPrice") or info.get("regularPrice") or info.get("previousClose")
        
        if not current_price or pe_ratio == 0:
            return None
            
        industry_pe_benchmark = 32.5 if sector in ["Technology", "Healthcare"] else 22.0
        industry_debt_benchmark = 0.5 if sector not in ["Financial Services", "Utilities"] else 2.5
        
        if pe_ratio >= industry_pe_benchmark or debt_to_equity >= industry_debt_benchmark:
            return None
            
        news_feed = stock.news
        has_negative_governance = False
        catalyst_match = "General Industrial Consolidation"
        catalyst_multiplier = 1.05
        
        if news_feed:
            for article in news_feed[:3]:
                headline = (article.get('title') or article.get('headline') or "").lower()
                
                if any(term in headline for term in GOVERNANCE_WARNING_TERMS):
                    has_negative_governance = True
                    break
                    
                for cat_name, keywords in NEWS_CATALYSTS.items():
                    if any(kw in headline for kw in keywords):
                        catalyst_match = f"{cat_name}: '{article.get('title') or article.get('headline')}'"
                        catalyst_multiplier = 1.25 if cat_name == "Black Swan / Disruption" else 1.18
                        break
                        
        if has_negative_governance:
            return None
            
        roe = (info.get("returnOnEquity", 0) or 0.15)
        predicted_target = current_price * (1.0 + roe) * catalyst_multiplier
        expected_gain_pct = ((predicted_target - current_price) / current_price) * 100
        
        return {
            "Company": company_name,
            "Sector": sector,
            "Current Price": f"₹{current_price:.2f}",
            "P/E": f"{pe_ratio:.1f} (Vs Industry: {industry_pe_benchmark})",
            "D/E": f"{debt_to_equity:.2f} (Vs Industry: {industry_debt_benchmark})",
            "Identified News Catalyst": catalyst_match,
            "1-Year Target Value": f"₹{predicted_target:.2f}",
            "Gain_Sort_Field": expected_gain_pct,
            "Expected Percentage Gain": f"{expected_gain_pct:.1f}%"
        }
    except:
        return None

st.info("📡 Scanning top NSE market listings and validating industry fundamentals...")

screened_results = []
for symbol in NSE_700_POOL:
    analysis = scan_and_analyze_market(symbol)
    if analysis:
        screened_results.append(analysis)

if screened_results:
    sorted_df = pd.DataFrame(screened_results)
    # EXPANDED: Changed from head(5) to head(20) to capture the full leaderboard
    top_20_gainer_records = sorted_df.sort_values(by="Gain_Sort_Field", ascending=False).head(20)
    
    st.subheader("🎯 Top 20 Governance-Approved Opportunities")
    
    # Renders an optimized mobile scrolling block for all 20 assets
    for rank, (_, row) in enumerate(top_20_gainer_records.iterrows()):
        with st.expander(f"🏆 Rank #{rank+1}: {row['Company']} ({row['Sector']})", expanded=False):
            st.write(f"**💰 Price:** {row['Current Price']} | **🚀 1-Year Target:** {row['1-Year Target Value']}")
            st.write(f"**📈 Expected Percentage Gain:** {row['Expected Percentage Gain']}")
            
            c1, c2 = st.columns(2)
            c1.caption(f"Valuation: {row['P/E']}")
            c2.caption(f"Leverage: {row['D/E']}")
            
            st.markdown("**🛡️ Catalyst Logic:**")
            st.success(row['Identified News Catalyst'])
else:
    st.error("No stocks completely cleared the combined filtering frameworks at this time.")
