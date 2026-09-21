from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from chart_utils import BLUE, RED, line_chart, style_figure
from metrics import annual_network_kpis, compact_number, percent


def render(data: dict[str, object]) -> None:
    monthly = data["network_monthly"]
    annual = data["network_annual"]
    weekday = data["network_weekday"]
    metadata = data["metadata"]

    years = sorted(annual["year"].astype(int).tolist(), reverse=True)
    selected_year = st.sidebar.selectbox("Calendar year", years, index=0, key="network_year")
    st.sidebar.selectbox("Day type", ["All days (cached)"], disabled=True, key="network_day_type")
    kpis = annual_network_kpis(annual, selected_year)
    selected_months = monthly.loc[monthly["month"].dt.year == selected_year]

    st.title("Network trends")
    st.caption("Tube and Bus demand, recovery and weekly travel patterns")
    st.markdown(
        '<div class="scope-note">The year filter applies to the KPI cards and monthly trend. '
        'The weekday profile is an all-period cached comparison.</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    cols[0].metric("Average daily Tube journeys", compact_number(kpis["tube_avg_daily"]))
    cols[1].metric("Average daily Bus journeys", compact_number(kpis["bus_avg_daily"]))
    cols[2].metric("Tube demand vs 2019", percent(kpis["tube_vs_2019"]))
    cols[3].metric("Bus demand vs 2019", percent(kpis["bus_vs_2019"]))
    cols[4].metric("Latest journey date", metadata["journey_data_through"])

    st.plotly_chart(
        line_chart(
            selected_months,
            "month",
            {"tube_avg_daily": "Tube", "bus_avg_daily": "Bus"},
            f"Monthly average daily demand — {selected_year}",
            height=420,
        ),
        width="stretch",
        config={"displayModeBar": False},
    )

    left, right = st.columns(2)
    with left:
        fig = go.Figure()
        fig.add_bar(x=weekday["day_of_week"], y=weekday["tube_avg_daily"], name="Tube", marker_color=BLUE)
        fig.add_bar(x=weekday["day_of_week"], y=weekday["bus_avg_daily"], name="Bus", marker_color=RED)
        fig.update_layout(title="Demand by day of week", barmode="group")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})
    with right:
        fig = go.Figure()
        fig.add_bar(x=annual["year"], y=annual["tube_avg_daily"], name="Tube", marker_color=BLUE)
        fig.add_bar(x=annual["year"], y=annual["bus_avg_daily"], name="Bus", marker_color=RED)
        fig.update_layout(title="Annual average daily demand", barmode="group")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})
