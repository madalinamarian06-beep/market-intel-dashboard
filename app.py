"""
Market Intelligence Dashboard — MVP
Author: Madalina Marian & Levin B. Gutsmuths
Purpose: Minimal Streamlit scaffold for a lightweight market dashboard.
"""

from __future__ import annotations
from datetime import datetime
from typing import List
import pytz
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

#Configurating page layout
st.set_page_config(
    page_title="Market Intelligence Dashboard — MVP",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.caption(f"Loaded file: {__file__}")

st.title("Market Intelligence Dashboard — MVP")
st.caption(
    "Goal: First sketch of a small, personal market monitor. "
    "Built with Python + Streamlit. Data source: Yahoo Finance."
)

#Timezone and basic tickers 
BERLIN_TZ = pytz.timezone("Europe/Berlin")
DEFAULT_TICKERS: List[str] = ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA"]

# Sidebar seetup
st.sidebar.header("Settings")
raw_tickers = st.sidebar.text_input(
    label="Tickers (comma-separated)",
    value=",".join(DEFAULT_TICKERS),
    help="Example: AAPL, MSFT, NVDA"
)


def parse_tickers(s: str) -> List[str]:
    return [t.strip().upper() for t in s.split(",") if t.strip()]

tickers: List[str] = parse_tickers(raw_tickers)

# Refresh button for updates on data
refresh = st.sidebar.button("Refresh data")

# Lookback period for trailing growth calculation
lookback_days = st.sidebar.slider(
    "Lookback for trailing growth (trading days)",
    min_value=182, max_value=1095, value=252, step=21
)
now_local = datetime.now(BERLIN_TZ)
# A nonce to force-refresh cache when you click the button
nonce = int(now_local.timestamp()) if refresh else 0

# Data fetching with caching to avoid redundant calls
@st.cache_data(ttl=120)
def get_snapshot(tickers: list[str], lookback_days: int, _nonce: int = 0) -> pd.DataFrame:
    rows = []
    for t in tickers:
        row = {"Ticker": t, "Name": "—", "Currency": "—",
               "Price": np.nan, "Day %": np.nan, "Predicted Growth (ann.)": np.nan}
        try:
            tk = yf.Ticker(t)

            # Name/Currency
            try:
                info = tk.get_info()
            except Exception:
                info = {}
            row["Name"] = info.get("shortName") or info.get("longName") or t
            row["Currency"] = info.get("currency") or "—"

            # Price & Day % 
            h = tk.history(period="5d", interval="1d", auto_adjust=False).dropna(how="all")
            if not h.empty:
                last_close = float(h["Close"].iloc[-1])
                prev_close = float(h["Close"].iloc[-2]) if len(h) >= 2 else np.nan
                row["Price"] = last_close
                if np.isfinite(prev_close) and prev_close != 0:
                    row["Day %"] = (last_close / prev_close - 1.0) * 100.0

            # Trailing CAGR
            lb = f"{lookback_days}d"
            h2 = tk.history(period=lb, interval="1d", auto_adjust=True).dropna(how="all")
            if len(h2) >= 2:
                start_price = float(h2["Close"].iloc[0])
                end_price = float(h2["Close"].iloc[-1])
                n = len(h2)  # trading days
                if start_price > 0 and n > 1:
                    cagr = (end_price / start_price) ** (252.0 / (n - 1)) - 1.0
                    row["Predicted Growth (ann.)"] = cagr * 100.0

        except Exception:
            pass

        rows.append(row)
    return pd.DataFrame(rows)

@st.cache_data(ttl=300)
def get_history_for_chart(ticker: str, period: str = "1y") -> pd.DataFrame:
    df = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=True)
    return df.dropna(how="all")



# Main app logic
now_local = datetime.now(BERLIN_TZ)
st.markdown(
    f"**Last refreshed:** {now_local:%Y-%m-%d %H:%M:%S %Z}  •  "
    f"**Tickers:** {', '.join(tickers) if tickers else '—'}" 
    
)

snapshot = get_snapshot(tickers, lookback_days, nonce)

fmt = snapshot.copy()
fmt["Price"] = fmt["Price"].map(lambda x: "—" if pd.isna(x) else f"{x:,.2f}")
fmt["Day %"] = fmt["Day %"].map(lambda x: "—" if pd.isna(x) else f"{x:+.2f}%")
fmt["Predicted Growth (ann.)"] = fmt["Predicted Growth (ann.)"].map(lambda x: "—" if pd.isna(x) else f"{x:+.2f}%")

st.subheader("Watchlist")
st.dataframe(fmt[["Ticker","Name","Price","Currency","Day %","Predicted Growth (ann.)"]],
             use_container_width=True, hide_index=True)

# Chart for a selected ticker
if tickers:
    st.subheader("Price history")
    chosen = st.selectbox("Choose a ticker to chart", options=tickers, index=0)
    hist = get_history_for_chart(chosen, period="1y")
    if hist.empty:
        st.info("No history available.")
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Adj Close"))
        fig.update_layout(margin=dict(l=0,r=0,t=10,b=0), height=320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

st.caption("Data via Yahoo Finance. Past performance summary .")

