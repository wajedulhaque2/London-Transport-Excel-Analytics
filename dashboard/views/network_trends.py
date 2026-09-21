from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from chart_utils import BLUE, RED, line_chart, style_figure
from metrics import annual_network, compact_number, network_monthly, network_summary, network_weekday, percent


def render(data: dict[str, object]) -> None:
    network = data["network_daily"]
    metadata = data["metadata"]
    years = sorted(network["year"].unique().tolist(), reverse=True)
    selected_year = st.sidebar.selectbox("Calendar year", years, key="network_year")
    day_type = st.sidebar.selectbox("Day type", ["All days", "Weekday", "Weekend"], key="network_day_type")

    kpis = network_summary(network, selected_year, day_type)
    monthly = network_monthly(network, selected_year, day_type)
    weekday = network_weekday(network, selected_year)
    annual = annual_network(network, day_type)

    st.title("Network trends")
    st.caption("Daily Tube and bus demand, recovery, and weekly travel patterns")
    st.markdown(
        f'<div class="scope-note">Calendar year <b>{selected_year}</b> · <b>{day_type}</b> · '
        f'{kpis["active_dates"]:,} observed dates. Recovery compares like-for-like day types with 2019.</div>',
        unsafe_allow_html=True,
    )
    if selected_year == max(years):
        st.info(f"{selected_year} is year-to-date through {metadata['journey_data_through']}.")

    cols = st.columns(5)
    cols[0].metric("Average daily Tube journeys", compact_number(kpis["tube_avg_daily"]))
    cols[1].metric("Average daily bus journeys", compact_number(kpis["bus_avg_daily"]))
    cols[2].metric("Tube demand vs 2019", percent(kpis["tube_vs_2019"]))
    cols[3].metric("Bus demand vs 2019", percent(kpis["bus_vs_2019"]))
    cols[4].metric("Observed dates", f"{kpis['active_dates']:,}")

    st.plotly_chart(
        line_chart(monthly, "month", {"tube_avg_daily": "Tube", "bus_avg_daily": "Bus"}, f"Monthly average daily demand — {selected_year}", height=420),
        width="stretch", config={"displayModeBar": False},
    )
    left, right = st.columns(2)
    with left:
        fig = go.Figure()
        fig.add_bar(x=weekday["day_of_week"], y=weekday["tube_avg_daily"], name="Tube", marker_color=BLUE)
        fig.add_bar(x=weekday["day_of_week"], y=weekday["bus_avg_daily"], name="Bus", marker_color=RED)
        fig.update_layout(title=f"Demand by weekday — {selected_year}", barmode="group")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})
    with right:
        fig = go.Figure()
        fig.add_bar(x=annual["year"], y=annual["tube_avg_daily"], name="Tube", marker_color=BLUE)
        fig.add_bar(x=annual["year"], y=annual["bus_avg_daily"], name="Bus", marker_color=RED)
        fig.update_layout(title=f"Annual average daily demand — {day_type}", barmode="group")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})
