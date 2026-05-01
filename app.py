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

# --- 14 SEC COUNTDOWN LOGIC ---
for i in range(14, 0, -1):
    timer_placeholder.markdown(f'<p class="timer-text">⏳ NEXT REFRESH: {i}s</p>', unsafe_allow_html=True)
    time.sleep(1)

st.rerun()