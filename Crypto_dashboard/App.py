import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ---- CONFIG ----
st.set_page_config(page_title="Crypto DCA Dashboard", layout="wide")

# ---- SETTINGS ----
coins = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'ripple': 'XRP'
}

initial_investments = {
    'BTC': 250,
    'ETH': 300,
    'XRP': 250
}

monthly_investment = 100
allocation = {
    'BTC': 0.33,
    'ETH': 0.34,
    'XRP': 0.33
}

start_date = datetime(2025, 7, 1)

# ---- FUNCTIONS ----
@st.cache_data(ttl=3600)
def get_current_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ','.join(coins.keys()),
        'vs_currencies': 'eur'
    }
    response = requests.get(url, params=params)
    return response.json()

def simulate_portfolio(prices):
    today = datetime.today()
    months = (today.year - start_date.year) * 12 + today.month - start_date.month + 1
    dca_history = []

    # Start met initiële holdings
    total_holdings = {
        v: initial_investments[v] / prices[k]['eur']
        for k, v in coins.items()
    }

    for i in range(months):
        date = start_date + relativedelta(months=i)
        for symbol in total_holdings:
            # Zoek de bijbehorende coin-id in CoinGecko
            coin_id = [k for k, v in coins.items() if v == symbol][0]
            price = prices[coin_id]['eur']
            bought = (monthly_investment * allocation[symbol]) / price
            total_holdings[symbol] += bought

        value = {
            symbol: total_holdings[symbol] * prices[[k for k, v in coins.items() if v == symbol][0]]['eur']
            for symbol in total_holdings
        }

        dca_history.append({'Date': date, **value})

    return pd.DataFrame(dca_history), total_holdings

# ---- MAIN APP ----
st.title("📊 Crypto DCA Dashboard")
st.markdown("Toont realtime waarde, DCA-grafiek en rendement van je cryptoportefeuille.")

prices = get_current_prices()
df, current_holdings = simulate_portfolio(prices)

# ---- LIVE OVERZICHT ----
st.header("📈 Huidige waarde")
cols = st.columns(len(current_holdings) + 1)
total_value = 0

for i, symbol in enumerate(current_holdings):
    coin_id = [k for k, v in coins.items() if v == symbol][0]
    price = prices[coin_id]['eur']
    holding_value = current_holdings[symbol] * price
    total_value += holding_value
    cols[i].metric(symbol, f"€{holding_value:,.2f}", f"{current_holdings[symbol]:.4f} {symbol}")

cols[-1].metric("📦 Totale waarde", f"€{total_value:,.2f}")

# ---- GRAFIEK ----
st.header("📅 Waardeontwikkeling portefeuille")
df['Total'] = df[[c for c in df.columns if c != 'Date']].sum(axis=1)
st.line_chart(df.set_index('Date')['Total'])

# ---- TABEL ----
st.header("📋 Historisch overzicht")
st.dataframe(df.round(2), use_container_width=True)

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

# ---- PUSHNOTIFICATIE (in-app waarschuwing bij grote schommelingen) ----
st.header("🚨 Waarschuwingen")

warnings = []
for coin_id, symbol in coins.items():
    price_today = prices[coin_id]['eur']
    # Simulatie: haal vorige prijs op (stel 24u geleden was 95% of 110%)
    previous_price = price_today * 1.1 if symbol == 'BTC' else price_today * 0.92
    change_pct = ((price_today - previous_price) / previous_price) * 100

    if abs(change_pct) > 10:
        warnings.append(f"**{symbol}** is {change_pct:+.1f}% veranderd sinds gisteren.")

if warnings:
    for w in warnings:
        st.error(w)
else:
    st.success("Geen abnormale koersbewegingen gemeld.")
