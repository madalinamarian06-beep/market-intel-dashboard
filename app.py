"""
Market Intelligence Dashboard — MVP (Non-AI)
Author: <your name>
Purpose: Minimal Streamlit scaffold for a lightweight market dashboard.
"""

# ---------- Standard library imports ----------
from __future__ import annotations
from datetime import datetime
from typing import List

# ---------- Third-party imports ----------
import pytz
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# ---------- Basic page config ----------
st.set_page_config(
    page_title="Market Intelligence Dashboard — MVP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- App Title & Subtitle ----------
st.title("📈 Market Intelligence Dashboard — MVP (Non-AI)")
st.caption(
    "Goal: a tiny, fast, personal market monitor. "
    "Built with Python + Streamlit. Data source: Yahoo Finance."
)

# ---------- Constants ----------
BERLIN_TZ = pytz.timezone("Europe/Berlin")
DEFAULT_TICKERS: List[str] = ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA"]

# ---------- Sidebar: user inputs ----------
st.sidebar.header("Settings")
raw_tickers = st.sidebar.text_input(
    label="Tickers (comma-separated)",
    value=",".join(DEFAULT_TICKERS),
    help="Example: AAPL, MSFT, NVDA"
)

def parse_tickers(s: str) -> List[str]:
    return [t.strip().upper() for t in s.split(",") if t.strip()]

tickers: List[str] = parse_tickers(raw_tickers)

# Manual refresh button
refresh = st.sidebar.button("🔄 Refresh data")

# ---------- Main: status / timestamp ----------
now_local = datetime.now(BERLIN_TZ)
st.markdown(
    f"**Last refreshed:** {now_local:%Y-%m-%d %H:%M:%S %Z}  •  "
    f"**Tickers:** {', '.join(tickers) if tickers else '—'}"
)

st.info("✅ Scaffold loaded. Next step: add live data fetching.")



