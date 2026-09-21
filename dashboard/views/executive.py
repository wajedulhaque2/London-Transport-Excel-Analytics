from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from chart_utils import BLUE, RED, horizontal_bar, line_chart, style_figure
from metrics import annual_network_kpis, compact_number, percent


def render(data: dict[str, object]) -> None:
    annual = data["network_annual"]
    monthly = data["network_monthly"]
    top_stations = data["top_stations"]
    service_by_line = data["executive_service_by_line"]
    metadata = data["metadata"]

    years = sorted(annual["year"].astype(int).tolist(), reverse=True)
    selected_year = st.sidebar.selectbox("Calendar year", years, index=0, key="executive_year")
    st.sidebar.selectbox(
        "Service financial year context",
        [metadata["executive_service_context"]],
        disabled=True,
        key="executive_service_year",
    )
    kpis = annual_network_kpis(annual, selected_year)
    executive = metadata["kpis"]["executive"]
    top_station = top_stations.sort_values("average_daily_footfall", ascending=False).iloc[0]

    st.title("London transport demand and station performance")
    st.caption("Executive view of network demand, station activity and Underground service delivery")
    st.markdown(
        f'<div class="scope-note">Demand KPIs use calendar year <b>{selected_year}</b>. '
        'Station and service cards retain their separately documented cached contexts.</div>',
        unsafe_allow_html=True,
    )

    first = st.columns(3)
    first[0].metric("Average daily Tube journeys", compact_number(kpis["tube_avg_daily"]))
    first[1].metric("Tube demand vs 2019", percent(kpis["tube_vs_2019"]))
    first[2].metric("Average daily Bus journeys", compact_number(kpis["bus_avg_daily"]))
    second = st.columns(3)
    second[0].metric("Bus demand vs 2019", percent(kpis["bus_vs_2019"]))
    second[1].metric("Average daily station footfall", compact_number(executive["Average Daily Footfall"]))
    second[2].metric("Service delivery", percent(executive["Service Delivery %"]))

    st.markdown(
        f'<div class="leader"><b>Highest-footfall station in the cached 2026 ranking:</b> '
        f'{top_station["station"]} — {compact_number(top_station["average_daily_footfall"])} average daily footfall.</div>',
        unsafe_allow_html=True,
    )

    selected_months = monthly.loc[monthly["month"].dt.year == selected_year]
    left, right = st.columns([1.35, 1])
    with left:
        st.plotly_chart(
            line_chart(
                selected_months,
                "month",
                {"tube_avg_daily": "Tube", "bus_avg_daily": "Bus"},
                f"Monthly average daily demand — {selected_year}",
            ),
            width="stretch",
            config={"displayModeBar": False},
        )
    with right:
        st.plotly_chart(
            horizontal_bar(
                top_stations.head(10),
                "average_daily_footfall",
                "station",
                "Leading stations by average daily footfall",
                color=BLUE,
            ),
            width="stretch",
            config={"displayModeBar": False},
        )

    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(
            horizontal_bar(
                service_by_line,
                "service_delivery",
                "line",
                "Underground service delivery by line",
                color=BLUE,
                percent_axis=True,
            ),
            width="stretch",
            config={"displayModeBar": False},
        )
    with right:
        intensity = data["executive_numbat_intensity"].sort_values(
            "passengers_per_scheduled_train", ascending=True
        )
        fig = go.Figure(
            go.Bar(
                x=intensity["passengers_per_scheduled_train"],
                y=intensity["link"],
                orientation="h",
                marker_color=RED,
                hovertemplate="%{y}<br>%{x:,.1f} passengers per scheduled train<extra></extra>",
            )
        )
        fig.update_layout(title="Highest demand per scheduled train")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})
        st.caption("Demand intensity only. Train capacity is not part of this measure.")

    with st.expander("Data freshness and interpretation"):
        st.write(f"Journey data through: {metadata['journey_data_through']}")
        st.write(f"Station data through: {metadata['station_data_through']}")
        st.write(f"Service context: {metadata['executive_service_context']}")
        st.write("2024/25 P6 and P8 are partial; P7 is unavailable following the TfL cyber incident.")
