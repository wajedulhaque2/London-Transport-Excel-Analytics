from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from chart_utils import BLUE, horizontal_bar, line_chart, style_figure
from metrics import compact_number, percent, safe_divide, station_monthly, station_ranking, station_weekday


def render(data: dict[str, object]) -> None:
    source = data["station_period"]
    metadata = data["metadata"]
    years = sorted(source["year"].unique().tolist(), reverse=True)
    year = st.sidebar.selectbox("Calendar year", years, key="station_year")
    day_type = st.sidebar.selectbox("Day type", ["All days", "Weekday", "Weekend"], key="station_day_type")
    available = sorted(source.loc[source["year"] == year, "station"].unique().tolist())
    default_station = "Kings Cross St Pancras" if "Kings Cross St Pancras" in available else available[0]
    station = st.sidebar.selectbox("Station", available, index=available.index(default_station), key="station_name")

    ranking = station_ranking(source, year, day_type)
    row = ranking.loc[ranking["station"] == station].iloc[0]
    monthly = station_monthly(source, station, year, day_type)
    weekday = station_weekday(source, station, year)
    baseline = station_ranking(source, 2019, day_type)
    baseline_row = baseline.loc[baseline["station"] == station]
    recovery = safe_divide(row["average_daily_footfall"], baseline_row.iloc[0]["average_daily_footfall"]) if not baseline_row.empty else float("nan")
    weekday_value = station_ranking(source, year, "Weekday").set_index("station")["average_daily_footfall"].get(station)
    weekend_value = station_ranking(source, year, "Weekend").set_index("station")["average_daily_footfall"].get(station)

    st.title("Station explorer")
    st.caption("Station demand, directionality, monthly patterns, and weekday behaviour")
    st.markdown(
        f'<div class="scope-note"><b>{station}</b> · {year} · {day_type} · '
        f'{int(row["active_dates"]):,} observed station-days. Missing station-days remain missing.</div>',
        unsafe_allow_html=True,
    )
    if year == max(years):
        st.info(f"{year} station data is year-to-date through {metadata['station_data_through']}.")

    cols = st.columns(5)
    cols[0].metric("Average daily footfall", compact_number(row["average_daily_footfall"]))
    cols[1].metric("Average daily entries", compact_number(row["average_daily_entries"]))
    cols[2].metric("Average daily exits", compact_number(row["average_daily_exits"]))
    cols[3].metric("Network rank", f"{int(row.name) + 1:,} of {len(ranking):,}")
    cols[4].metric("Demand vs 2019", percent(recovery))
    secondary = st.columns(2)
    secondary[0].metric("Directionality index", percent(row["directionality_index"]))
    secondary[1].metric("Weekday / weekend ratio", f"{safe_divide(weekday_value, weekend_value):.2f}x")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(line_chart(monthly, "month", {"average_daily_footfall": "Average daily footfall"}, "Monthly average daily footfall"), width="stretch", config={"displayModeBar": False})
    with right:
        fig = go.Figure(go.Bar(x=weekday["day_of_week"], y=weekday["average_daily_footfall"], marker_color=BLUE))
        fig.update_layout(title="Demand by day of week")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})

    st.plotly_chart(line_chart(monthly, "month", {"average_daily_entries": "Entries", "average_daily_exits": "Exits"}, "Average daily entries versus exits"), width="stretch", config={"displayModeBar": False})
    st.plotly_chart(horizontal_bar(ranking.head(15), "average_daily_footfall", "station", f"Leading stations — {year}, {day_type}", color=BLUE, height=500), width="stretch", config={"displayModeBar": False})
    with st.expander("View station ranking data"):
        st.dataframe(ranking[["station", "average_daily_footfall", "average_daily_entries", "average_daily_exits", "active_dates"]], width="stretch", hide_index=True)
