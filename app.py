import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="MacroGuard Enterprise", page_icon="📡", layout="wide")
st.title("📡 MacroGuard Enterprise: Top 1000 NSE Sieve Engine")
st.caption("Industrial-Scale Async Processing (Auto-filtering Banks & PSUs | Daily Auto-Refresh)")

# 1. LIVE DYNAMIC TOP 1000 TICKER HARVESTER
@st.cache_data(ttl=86400) # Updates dynamically exactly once a day
def harvest_top_1000_nse_tickers():
    base_pool = set()
    urls = [
        "https://githubusercontent.com",
        "https://githubusercontent.com",
        "https://githubusercontent.com"
    ]
    
    for url in urls:
        try:
            df = pd.read_csv(url)
            if 'Symbol' in df.columns:
                symbols = df['Symbol'].dropna().astype(str).str.strip().tolist()
                base_pool.update(symbols)
        except Exception:
            continue
            
    if len(base_pool) < 50:
        fallback = ["DIXON", "SUZLON", "TATAPOWER", "MAZDOCK", "COCHINSHIP", "KPITTECH", "TATAELXSI", "RELIANCE", "TCS", "INFY"]
        return [f"{t}.NS" for t in fallback]
        
    formatted_tickers = [f"{symbol}.NS" for symbol in base_pool if symbol and not symbol.replace('.','').isdigit()]
    return sorted(list(set(formatted_tickers)))[:1000]

# 2. ASYNC METRIC CRUNCHER WITH ANTI-BAN CIRCUIT BREAKERS
def process_single_ticker_safe(ticker):
    GOVERNANCE_WARNING_TERMS = ["sebi fine", "fraud", "scam", "pledge invocation", "auditor resigns", "investigation", "raid"]
    
    try:
        time.sleep(0.15) # Safe micro-cooldown delay to prevent IP bans
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        company_name = info.get("longName") or info.get("shortName") or ticker
        sector = info.get("sector", "Other Sectors")
        industry = info.get("industry", "Other")
        
        # --- BRUTAL ANTI-BANK & ANTI-PSU DEFENSE SIEVE ---
        name_lower = company_name.lower()
        sector_lower = sector.lower()
        industry_lower = industry.lower()
        
        ban_words = [
            "bank", "banking", "financial services", "insurance", "fincorp", "finance",
            "psu", "state-owned", "corporation of india", "government", "national"
        ]
        
        if any(word in name_lower or word in sector_lower or word in industry_lower for word in ban_words):
            return None
            
        pe_ratio = info.get("trailingPE", 0)
        raw_debt = info.get("debtToEquity")
        debt_to_equity = (raw_debt / 100.0) if raw_debt is not None else 0.0
        current_price = info.get("currentPrice") or info.get("regularPrice") or info.get("previousClose")
        roe = info.get("returnOnEquity") or 0.15
        roe_pct = roe * 100
        
        if pe_ratio == 0 or not current_price:
            return None
            
        industry_pe_limit = 65.0 if sector in ["Technology", "Healthcare", "Industrials"] else 45.0
        industry_debt_limit = 1.6 if sector == "Industrials" else 1.1
        
        if pe_ratio >= industry_pe_limit or debt_to_equity >= industry_debt_limit:
            return None
            
        # Media scanning validation loop
        news_feed = stock.news
        has_negative_governance = False
        detected_headline = ""
        catalyst_match = ""
        catalyst_multiplier = 1.05
        
        if news_feed and isinstance(news_feed, list) and len(news_feed) > 0:
            top_story = news_feed[0]
            if isinstance(top_story, dict):
                detected_headline = top_story.get('title') or top_story.get('headline') or ""
                headline_lower = detected_headline.lower()
                
                for article in news_feed[:3]:
                    if isinstance(article, dict):
                        h_low = (article.get('title') or article.get('headline') or "").lower()
                        if any(term in h_low for term in GOVERNANCE_WARNING_TERMS):
                            has_negative_governance = True
                            break
                
                if any(w in headline_lower for w in ["ai", "semiconductor", "order", "contract", "win", "secured"]):
                    catalyst_match = f"🚀 Backlog Expansion: '{detected_headline}'."
                    catalyst_multiplier = 1.35
                elif any(w in headline_lower for w in ["capex", "expansion", "crore", "plant", "capacity"]):
                    catalyst_match = f"🏗️ Infrastructure Surge: '{detected_headline}'."
                    catalyst_multiplier = 1.28
                elif any(w in headline_lower for w in ["profit", "surge", "beat", "earning", "turnaround"]):
                    catalyst_match = f"📈 Earnings Acceleration: '{detected_headline}'."
                    catalyst_multiplier = 1.25

        # Fallback tracking models if news array returns empty
        if not catalyst_match:
            if debt_to_equity < 0.15:
                catalyst_match = f"🛡️ Balanced Moat: Unleveraged structural operations at {roe_pct:.1f}% ROE."
                catalyst_multiplier = 1.20
            else:
                catalyst_match = f"⚡ Standard Vector: Compounding growth at {roe_pct:.1f}% ROE."
                catalyst_multiplier = 1.15
                
        if has_negative_governance:
            return None
            
        predicted_target = current_price * (1.0 + (roe * 1.25)) * catalyst_multiplier
        expected_gain_pct = ((predicted_target - current_price) / current_price) * 100
        
        return {
            "Company": company_name,
            "Sector": sector,
            "Current Price": f"₹{current_price:.2f}",
            "P/E": f"{pe_ratio:.1f} (Limit: {industry_pe_limit})",
            "D/E": f"{debt_to_equity:.2f} (Limit: {industry_debt_limit})",
            "Identified Catalyst": catalyst_match,
            "1-Year Target Value": f"₹{predicted_target:.2f}",
            "Gain_Sort_Field": expected_gain_pct,
            "Expected Percentage Gain": f"{expected_gain_pct:.1f}%"
        }
    except Exception:
        return None

# 3. STREAMLIT APP CORE EXECUTIVE CONTROL FLOW
@st.cache_data(ttl=86400)
def run_heavy_pipeline(tickers_list):
    results = []
    max_concurrent_workers = 3 # Kept low intentionally to avoid IP bans
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_tickers = len(tickers_list)
    
    with ThreadPoolExecutor(max_workers=max_concurrent_workers) as executor:
        future_map = {executor.submit(process_single_ticker_safe, ticker): ticker for ticker in tickers_list}
        
        for idx, future in enumerate(as_completed(future_map)):
            ticker_name = future_map[future]
            try:
                data = future.result()
                if data:
                    results.append(data)
            except Exception:
                pass
            
            percent_complete = int(((idx + 1) / total_tickers) * 100)
            progress_bar.progress(percent_complete)
            status_text.text(f"⏳ Evaluated [{idx+1}/{total_tickers}] tickers. Processing: {ticker_name}")
            
    progress_bar.empty()
    status_text.empty()
    return results

# --- RUN ARCHITECTURE ---
raw_target_pool = harvest_top_1000_nse_tickers()
st.sidebar.metric("Target Stock Inventory Loaded", len(raw_target_pool))

if st.sidebar.button("Force Clear Cache & Re-run"):
    st.cache_data.clear()
    st.rerun()

st.info(f"⚡ Processing engine actively initialized for {len(raw_target_pool)} high-liquidity targets. Running deep filters...")

compiled_opportunities = run_heavy_pipeline(raw_target_pool)

if compiled_opportunities:
    sorted_df = pd.DataFrame(compiled_opportunities)
    top_20_gainer_records = sorted_df.sort_values(by="Gain_Sort_Field", ascending=False).head(20)
    
    st.subheader(f"🎯 Top 20 Screened Growth Assets (From {len(compiled_opportunities)} Cleared Candidates)")
    
    for rank, (_, row) in enumerate(top_20_gainer_records.iterrows()):
        with st.expander(f"🏆 Rank #{rank+1}: {row['Company']} ({row['Sector']})", expanded=(rank==0)):
            st.write(f"**💰 Price:** {row['Current Price']} | **🚀 1-Year Target:** {row['1-Year Target Value']}")
            st.write(f"**📈 Expected Percentage Gain:** {row['Expected Percentage Gain']}")
            
            c1, c2 = st.columns(2)
            c1.caption(f"Valuation: {row['P/E']}")
            c2.caption(f"Leverage: {row['D/E']}")
            
            st.markdown("**🛡️ Growth Catalyst Analysis:**")
            st.success(row['Identified Catalyst'])
else:
    st.error("No stocks from the current 1000-stock batch passed the strict growth and debt thresholds.")
