from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from chart_utils import BLUE, RED, horizontal_bar, line_chart, style_figure
from metrics import compact_number, percent, ranked_station


DETAIL_STATION = "Langdon Park"


def render(data: dict[str, object]) -> None:
    top = data["top_stations"].sort_values("average_daily_footfall", ascending=False)
    metadata = data["metadata"]
    detail = metadata["kpis"]["station_detail"]
    options = [DETAIL_STATION] + [name for name in top["station"].tolist() if name != DETAIL_STATION]
    station = st.sidebar.selectbox("Station", options, key="station_name")
    if station == DETAIL_STATION:
        st.sidebar.selectbox("Calendar year", [2026], disabled=True, key="station_year")
        st.sidebar.selectbox("Day type", ["Weekday"], disabled=True, key="station_day_type")
    else:
        st.sidebar.selectbox("Ranking period", ["2026 YTD (cached)"], disabled=True, key="station_rank_period")

    st.title("Station explorer")
    st.caption("Station demand, directionality and weekday behaviour")

    if station == DETAIL_STATION:
        context = metadata["station_detail_context"]
        st.markdown(
            f'<div class="scope-note">Detailed cached context: <b>{context["station"]}</b>, '
            f'{context["calendar_year"]}, {context["day_type"]}. Missing station-day rows remain missing.</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(5)
        cols[0].metric("Average daily footfall", compact_number(detail["Average Daily Footfall"]))
        cols[1].metric("Average daily entries", compact_number(detail["Average Daily Entries"]))
        cols[2].metric("Average daily exits", compact_number(detail["Average Daily Exits"]))
        cols[3].metric("Network rank", f"{int(detail['Station Rank']):,}")
        cols[4].metric("Demand vs 2019", percent(detail["Demand vs 2019 %"]))

        secondary = st.columns(2)
        secondary[0].metric("Directionality index", percent(detail["Directionality Index"]))
        secondary[1].metric("Weekday / weekend ratio", f"{detail['Weekday Weekend Ratio']:.2f}x")

        left, right = st.columns(2)
        with left:
            st.plotly_chart(
                line_chart(
                    data["station_monthly_detail"],
                    "month",
                    {"average_daily_footfall": "Average daily footfall"},
                    "Monthly average daily footfall",
                ),
                width="stretch",
                config={"displayModeBar": False},
            )
        with right:
            weekday = data["station_weekday_detail"]
            fig = go.Figure(
                go.Bar(
                    x=weekday["day_of_week"],
                    y=weekday["average_daily_footfall"],
                    marker_color=BLUE,
                )
            )
            fig.update_layout(title="Demand by day of week")
            st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})

        entries = data["station_entries_exits_detail"]
        st.plotly_chart(
            line_chart(
                entries,
                "month",
                {
                    "average_daily_entries": "Entries",
                    "average_daily_exits": "Exits",
                },
                "Entries versus exits",
            ),
            width="stretch",
            config={"displayModeBar": False},
        )
        st.caption(
            "Directionality Index = ABS(entries − exits) / total footfall. Values nearer zero indicate more balanced flows."
        )
    else:
        selected = ranked_station(top, station)
        st.markdown(
            '<div class="warning-note">The cached workbook contains ranking output for this station, '
            'but not its monthly or day-level rows. Those views are intentionally unavailable until the source pack is added.</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(3)
        cols[0].metric("Station", station)
        cols[1].metric("Average daily footfall", compact_number(selected["average_daily_footfall"]))
        cols[2].metric("Rank within cached top 10", f"{selected['rank']}")

    st.plotly_chart(
        horizontal_bar(top, "average_daily_footfall", "station", "Cached 2026 leading-station ranking", color=BLUE),
        width="stretch",
        config={"displayModeBar": False},
    )
    with st.expander("View cached station ranking data"):
        st.dataframe(top, width="stretch", hide_index=True)
