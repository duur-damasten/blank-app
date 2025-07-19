import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ---- CONFIG ----
st.set_page_config(page_title="Mijn Crypto Dashboard", layout="wide")

# ---- JOUW HOLDINGS ----
portfolio = {
    'ETH': {
        'amount': 0.09663165,
        'cost': 300.00
    },
    'BTC': {
        'amount': 0.00243040,
        'cost': 249.99
    },
    'XRP': {
        'amount': 82.96991000,
        'cost': 250.00
    }
}

# CoinGecko-IDs
coin_ids = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'XRP': 'ripple'
}

# ---- FUNCTIES ----
@st.cache_data(ttl=3600)
def get_current_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ','.join(coin_ids.values()),
        'vs_currencies': 'eur'
    }
    response = requests.get(url, params=params)
    return response.json()

# ---- HAAL DATA OP ----
prices = get_current_prices()

# ---- DASHBOARD: LIVE WAARDE EN WINST ----
st.title("📊 Mijn Crypto Dashboard")
st.subheader("Live waarde, winst/verlies en koersverwachting")

st.header("📈 Huidige waarde & winst/verlies")
cols = st.columns(len(portfolio) + 1)
total_value = 0
total_cost = 0

for i, symbol in enumerate(portfolio):
    amount = portfolio[symbol]['amount']
    cost = portfolio[symbol]['cost']
    price = prices[coin_ids[symbol]]['eur']
    current_value = amount * price
    pnl_eur = current_value - cost
    pnl_pct = (pnl_eur / cost) * 100

    total_value += current_value
    total_cost += cost

    cols[i].metric(
        label=f"{symbol}",
        value=f"€{current_value:,.2f}",
        delta=f"{pnl_eur:+.2f} EUR ({pnl_pct:+.1f}%)"
    )

cols[-1].metric("📦 Totaal", f"€{total_value:,.2f}", f"{(total_value - total_cost):+.2f} EUR")

# ---- KOERSVERWACHTING ----
st.header("🔮 Verwachting komende week (22–28 juli 2025)")

forecast = {
    'BTC': "€60.000 – €65.000 (ETF-instroom en positief macro-sentiment)",
    'ETH': "€3.400 – €3.700 (ETH-ETF’s + Layer 2 groei)",
    'XRP': "€0,48 – €0,56 (lichte stijging mogelijk, adoptie blijft traag)"
}

for symbol, msg in forecast.items():
    st.markdown(f"**{symbol}**: {msg}")

# ---- NIEUWS SAMENVATTING ----
st.header("📰 Laatste crypto-nieuws (samenvatting)")

news_summary = """
- **Bitcoin** blijft stijgen door institutionele vraag en nieuwe regelgeving (GENIUS Act).
- **Ethereum** profiteert van de spot-ETF’s en groeit via Layer 2-oplossingen.
- **XRP** beweegt zijwaarts, maar zoekt partners in het Midden-Oosten (CBDC’s).
"""

st.markdown(news_summary)

# ---- PUSHNOTIFICATIE SIMULATIE ----
st.header("🚨 Waarschuwingen (koersschommelingen >10%)")
for symbol in portfolio:
    price_now = prices[coin_ids[symbol]]['eur']
    # Simuleer prijs 24u geleden (stel 11% verschil)
    simulated_previous = price_now * (1.11 if symbol == 'BTC' else 0.88)
    delta_pct = ((price_now - simulated_previous) / simulated_previous) * 100

    if abs(delta_pct) > 10:
        st.error(f"{symbol} is {delta_pct:+.1f}% veranderd t.o.v. gisteren!")
    else:
        st.success(f"{symbol}: geen abnormale beweging gedetecteerd.")
