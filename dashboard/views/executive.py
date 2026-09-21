from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from chart_utils import BLUE, RED, horizontal_bar, line_chart, style_figure
from metrics import compact_number, network_monthly, network_summary, service_summary, station_ranking, percent


def _link_intensity(frame):
    loads = frame.loc[frame["metric_type"] == "Passenger load", ["link", "line", "Total"]].rename(columns={"Total": "passenger_load"})
    trains = frame.loc[frame["metric_type"] == "Scheduled trains", ["link", "line", "Total"]].rename(columns={"Total": "scheduled_trains"})
    result = loads.merge(trains, on=["link", "line"], how="inner")
    result["passengers_per_scheduled_train"] = result["passenger_load"] / result["scheduled_trains"].replace(0, float("nan"))
    return result.sort_values("passengers_per_scheduled_train", ascending=False)


def render(data: dict[str, object]) -> None:
    network = data["network_daily"]
    years = sorted(network["year"].unique().tolist(), reverse=True)
    selected_year = st.sidebar.selectbox("Calendar year", years, key="executive_year")
    kpis = network_summary(network, selected_year, "All days")
    monthly = network_monthly(network, selected_year, "All days")
    stations = station_ranking(data["station_period"], selected_year, "All days")

    service_years = sorted(data["service_records"]["financial_year"].unique().tolist(), reverse=True)
    service_year = st.sidebar.selectbox("Service financial year", service_years, key="executive_service_year")
    service = data["service_records"].loc[data["service_records"]["financial_year"] == service_year]
    service_kpis = service_summary(service)
    service_lines = []
    for line, group in service.groupby("line", observed=True):
        service_lines.append({"line": line, **service_summary(group)})
    service_lines = __import__("pandas").DataFrame(service_lines)
    intensity = _link_intensity(data["numbat_links"]).head(10)

    st.title("London transport demand and station performance")
    st.caption("Executive view of network demand, station activity, and Underground service delivery")
    st.markdown(
        f'<div class="scope-note">Passenger demand and station activity use calendar year <b>{selected_year}</b>. '
        f'Underground service uses financial year <b>{service_year}</b>. NUMBAT uses its separate 2024 typical-day model.</div>',
        unsafe_allow_html=True,
    )

    first = st.columns(3)
    first[0].metric("Average daily Tube journeys", compact_number(kpis["tube_avg_daily"]))
    first[1].metric("Tube demand vs 2019", percent(kpis["tube_vs_2019"]))
    first[2].metric("Average daily bus journeys", compact_number(kpis["bus_avg_daily"]))
    second = st.columns(3)
    second[0].metric("Bus demand vs 2019", percent(kpis["bus_vs_2019"]))
    second[1].metric("Leading station", stations.iloc[0]["station"])
    second[2].metric("Service delivery", percent(service_kpis["service_delivery"]))

    left, right = st.columns([1.35, 1])
    with left:
        st.plotly_chart(line_chart(monthly, "month", {"tube_avg_daily": "Tube", "bus_avg_daily": "Bus"}, f"Monthly average daily demand — {selected_year}"), width="stretch", config={"displayModeBar": False})
    with right:
        st.plotly_chart(horizontal_bar(stations.head(10), "average_daily_footfall", "station", f"Leading stations — {selected_year}", color=BLUE), width="stretch", config={"displayModeBar": False})

    left, right = st.columns(2)
    with left:
        st.plotly_chart(horizontal_bar(service_lines, "service_delivery", "line", f"Underground service delivery — {service_year}", color=BLUE, percent_axis=True), width="stretch", config={"displayModeBar": False})
    with right:
        fig = go.Figure(go.Bar(x=intensity["passengers_per_scheduled_train"], y=intensity["link"], orientation="h", marker_color=RED, hovertemplate="%{y}<br>%{x:,.1f} passengers per scheduled train<extra></extra>"))
        fig.update_layout(title="Highest all-day demand per scheduled train")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})
        st.caption("Demand intensity only; train capacity is not part of this measure.")

    with st.expander("Data freshness and interpretation"):
        st.write(f"Journey data: {data['metadata']['journey_data_from']} to {data['metadata']['journey_data_through']}")
        st.write(f"Station data: {data['metadata']['station_data_from']} to {data['metadata']['station_data_through']}")
        st.write("2024-25 service periods 6 and 8 are partial; period 7 is unavailable following the TfL cyber incident.")
