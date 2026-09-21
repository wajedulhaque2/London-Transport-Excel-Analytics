from __future__ import annotations

import streamlit as st

from data_loader import load_snapshot
from styles import APP_CSS
from views import data_notes, executive, line_performance, network_trends, peak_flow, station_explorer


st.set_page_config(
    page_title="London Transport Analytics",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(APP_CSS, unsafe_allow_html=True)

data = load_snapshot()

st.sidebar.title("London transport")
st.sidebar.caption("Cached portfolio dashboard")
page = st.sidebar.radio(
    "View",
    [
        "Executive dashboard",
        "Network trends",
        "Station explorer",
        "Line performance",
        "Peak flow analysis",
        "Data notes",
    ],
)
st.sidebar.divider()
st.sidebar.caption("Data provided by Transport for London")

PAGES = {
    "Executive dashboard": executive.render,
    "Network trends": network_trends.render,
    "Station explorer": station_explorer.render,
    "Line performance": line_performance.render,
    "Peak flow analysis": peak_flow.render,
    "Data notes": data_notes.render,
}
PAGES[page](data)
