import streamlit as st
import pandas as pd
import requests
import time

# --- TERMINAL UI STYLE ---
st.set_page_config(page_title="Smart-OI Live Terminal", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00FF41; }
    .terminal-box { border: 2px solid #00FF41; padding: 20px; background-color: #0a0a0a; }
    .timer-text { font-size: 20px; font-weight: bold; color: #fbff00; }
    </style>
    """, unsafe_allow_html=True)

# --- LIVE NSE ENGINE ---
def get_live_nse():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9"
    }
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        data = session.get(url, headers=headers, timeout=5).json()
        spot = data['records']['underlyingValue']
        atm = round(spot / 50) * 50
        raw_data = data['records']['data']
        strikes = [x for x in raw_data if atm - 400 <= x['strikePrice'] <= atm + 350]
        
        final_rows = []
        for item in strikes:
            s_price = item['strikePrice']
            ce = item.get('CE', {})
            pe = item.get('PE', {})
            final_rows.append({
                "Strike": f"{s_price} ({'ATM' if s_price==atm else 'OTM' if s_price>atm else 'ITM'})",
                "Call OI": f"{ce.get('openInterest', 0):,}",
                "Signal": "😈 DEVIL" if ce.get('openInterest', 0) > 80000 else "🚀 ROCKET" if pe.get('openInterest', 0) > 80000 else "",
                "Put OI": f"{pe.get('openInterest', 0):,}"
            })
        return pd.DataFrame(final_rows), spot, atm
    except:
        return None, 0, 0

# --- TOP NAVIGATION (Timer & Button) ---
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown('<h2 style="margin:0;">📟 NSE LIVE TERMINAL</h2>', unsafe_allow_html=True)

with col2:
    # Refresh Button
    if st.button('🔄 REFRESH NOW'):
        st.rerun()

with col3:
    # Timer Display
    timer_placeholder = st.empty()

# --- FETCH & DISPLAY DATA ---
df, spot, atm = get_live_nse()

if df is not None:
    st.write(f"**NIFTY SPOT:** {spot} | **ATM:** {atm}")
    st.table(df)
else:
    st.warning("NSE Server Connection Pending... Waiting for Market Open.")
import yfinance as yf

# --- LIVE GLOBAL MARKET MONITOR ---
st.markdown("---")
st.subheader("🌍 Global Market Sentiment (Live)")

def get_global_live():
    # Symbols: Gifty Nifty (NSE), Nasdaq, Dow, Crude, Brent
    symbols = {
        "GIFTY NIFTY": "^NSEI", # Nifty 50 ko reference le rahe hain
        "NASDAQ": "^IXIC",
        "DOW JONES": "^DJI",
        "CRUDE OIL": "CL=F",
        "BRENT": "BZ=F"
    }
    
    data_list = {}
    for name, sym in symbols.items():
        ticker = yf.Ticker(sym)
        info = ticker.fast_info
        price = round(info.last_price, 2)
        prev_close = info.previous_close
        change = round(((price - prev_close) / prev_close) * 100, 2)
        
        # Bullish/Bearish Logic
        sentiment = "Bullish" if change >= 0 else "Bearish"
        status = "Gap Up 🚀" if change > 0.5 else ("Gap Down 📉" if change < -0.5 else "Steady")
        
        data_list[name] = {"Price": price, "Change": change, "Status": status, "Sentiment": sentiment}
    return data_list

# Data fetch karo
try:
    live_data = get_global_live()
    cols = st.columns(5)
    for i, (name, data) in enumerate(live_data.items()):
        with cols[i]:
            color = "green" if data['Sentiment'] == "Bullish" else "red"
            st.markdown(f"**{name}**")
            st.markdown(f"### :{color}[{data['Price']}]")
            st.caption(f"{data['Change']}% | {data['Status']}")
            st.write(f"{'🟢' if color == 'green' else '🔴'} {data['Sentiment']}")
except:
    st.write("Fetching Live Global Data...")
# --- PCR (PUT-CALL RATIO) MONITOR ---
st.markdown("---")
st.subheader("📊 Option Chain Sentiment (PCR)")

def calculate_pcr(df):
    try:
        total_put_oi = df['PE_OI'].sum()
        total_call_oi = df['CE_OI'].sum()
        pcr_val = round(total_put_oi / total_call_oi, 2)
        
        # PCR Interpretation
        if pcr_val > 1.2:
            mood = "Extremely Bullish (Overbought)"
            color = "green"
        elif pcr_val < 0.7:
            mood = "Extremely Bearish (Oversold)"
            color = "red"
        else:
            mood = "Neutral / Sideways"
            color = "white"
            
        return pcr_val, mood, color
    except:
        return "Wait", "Market Open Hone Ka Wait Karein", "white"

# Display PCR
if df is not None:
    pcr_value, pcr_mood, pcr_colorprefix = calculate_pcr(df)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("NIFTY PCR", pcr_value)
    with c2:
        st.markdown(f"**Market Sentiment:** :{pcr_colorprefix}[{pcr_mood}]")
else:
    st.info("PCR Data Monday morning 9:15 AM par live hoga. 😈")
# Sabse niche st.rerun() rehne dena
st.rerun()
