import streamlit as st
import pandas as pd
import requests
import time
# --- PASSWORD PROTECTION ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "Bhai@123": # <-- Ye aapka password hai
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Password to Access Terminal 😈", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Wrong Password! Try Again.", type="password", on_change=password_entered, key="password")
        st.error("❌ Access Denied")
        return False
    return True

if not check_password():
    st.stop() # Login ke bina niche ka code nahi chalega
# --- TERMINAL UI STYLE ---
st.set_page_config(page_title="Smart-OI Live Terminal", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00FF41; }
    .terminal-box { border: 2px solid #00FF41; padding: 20px; background-color: #0a0a0a; }
    .timer-text { font-size: 20px; font-weight: bold; color: #fbff00; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'last_df' not in st.session_state:
    st.session_state['last_df'] = None
    st.session_state['last_spot'] = "Loading..."
    st.session_state['last_atm'] = "Loading..."# --- LIVE NSE ENGINE ---
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
 # --- FETCH & DISPLAY DATA ---
data_tuple = get_live_nse()

# 1. Data Processing Logic
if data_tuple is not None:
    df_new, spot_new, atm_new = data_tuple
    # Memory mein save karo taki market band hone par bhi dikhe
    st.session_state['last_df'] = df_new
    st.session_state['last_spot'] = spot_new
    st.session_state['last_atm'] = atm_new

# 2. UI Display Logic (Memory se data uthao)
if 'last_df' in st.session_state and st.session_state['last_df'] is not None:
    df_final = st.session_state['last_df']
    spot_final = st.session_state['last_spot']
    atm_final = st.session_state['last_atm']
    
    # NIFTY Index aur ATM Header
    st.markdown(f"### 🎯 NIFTY SPOT: `{spot_final}` | ATM: `{atm_final}`")
    
    # Agar live data nahi mil raha (Market Closed)
    if data_tuple is None:
        st.info("🕒 Market Closed. Showing last available data.")
    
    # Final Option Chain Table
    st.table(df_final)
else:
    # Bilkul fresh start ke liye message
    st.warning("NSE Server se connect ho raha hai... Monday 9:15 AM tak wait karein! 😈")
st.rerun()
