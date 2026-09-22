from __future__ import annotations

import pandas as pd
import streamlit as st

from chart_utils import BLUE, RED, horizontal_bar, line_chart
from metrics import TIME_BANDS, columns_for_time_band, compact_number, numbat_profile


def _filter(frame, station: str, line: str):
    selected = frame
    if station != "All stations" and "station" in selected:
        selected = selected.loc[selected["station"] == station]
    if line != "All lines" and "line" in selected:
        selected = selected.loc[selected["line"] == line]
    return selected


def _link_metrics(frame: pd.DataFrame, line: str, time_band: str) -> pd.DataFrame:
    selected = frame if line == "All lines" else frame.loc[frame["line"] == line]
    columns = columns_for_time_band(selected, time_band)
    keys = ["link", "line", "direction", "from_station", "to_station"]
    values = selected[keys + ["metric_type"]].copy()
    values["value"] = selected[columns].sum(axis=1, min_count=1)
    pivot = values.pivot_table(index=keys, columns="metric_type", values="value", aggfunc="sum").reset_index()
    pivot = pivot.rename(columns={"Passenger load": "passenger_load", "Scheduled trains": "scheduled_trains"})
    pivot["link_label"] = pivot["from_station"] + " → " + pivot["to_station"]
    pivot["passengers_per_scheduled_train"] = pivot["passenger_load"] / pivot["scheduled_trains"].replace(0, float("nan"))
    return pivot


def render(data: dict[str, object]) -> None:
    station_source = data["numbat_station"]
    platform_source = data["numbat_platform"]
    link_source = data["numbat_links"]
    time_band = st.sidebar.selectbox("Time band", list(TIME_BANDS), key="numbat_time")
    station_options = ["All stations"] + sorted(station_source["station"].dropna().unique().tolist())
    station = st.sidebar.selectbox("Station", station_options, key="numbat_station")
    line_scope = platform_source if station == "All stations" else platform_source.loc[platform_source["station"] == station]
    line_options = ["All lines"] + sorted(line_scope["line"].dropna().unique().tolist())
    line = st.sidebar.selectbox("NUMBAT line", line_options, key="numbat_line")

    station_data = _filter(station_source, station, line)
    platform_data = _filter(platform_source, station, line)
    gate_profile = numbat_profile(station_data, time_band)
    platform_profile = numbat_profile(platform_data, time_band)
    links = _link_metrics(link_source, line, time_band)
    gate_totals = station_data.groupby("flow_type")[columns_for_time_band(station_data, time_band)].sum().sum(axis=1)
    platform_totals = platform_data.groupby("flow_type")[columns_for_time_band(platform_data, time_band)].sum().sum(axis=1)

    st.title("Peak flow analysis")
    st.caption("NUMBAT 2024 TWT typical-day station, platform, and link demand")
    st.markdown(
        f'<div class="scope-note"><b>{time_band}</b> · <b>{station}</b> · <b>{line}</b>. '
        'Quarter-hour ordering follows the NUMBAT traffic day from 05:00 to 05:00.</div>',
        unsafe_allow_html=True,
    )
    st.caption("The station filter applies to gate and platform flows. The line filter applies to platform and link flows because gate counts are not line-coded.")

    cols = st.columns(5)
    entries = float(gate_totals.get("Entries", 0))
    exits = float(gate_totals.get("Exits", 0))
    cols[0].metric("Gate footfall", compact_number(entries + exits))
    cols[1].metric("Entries", compact_number(entries))
    cols[2].metric("Exits", compact_number(exits))
    cols[3].metric("Boarders", compact_number(platform_totals.get("Boarders", 0)))
    cols[4].metric("Alighters", compact_number(platform_totals.get("Alighters", 0)))

    left, right = st.columns(2)
    with left:
        st.plotly_chart(line_chart(gate_profile, "quarter_hour", {"Entries": "Entries", "Exits": "Exits"}, "15-minute station entry and exit profile"), width="stretch", config={"displayModeBar": False})
    with right:
        st.plotly_chart(line_chart(platform_profile, "quarter_hour", {"Boarders": "Boarders", "Alighters": "Alighters"}, "Platform boarders and alighters"), width="stretch", config={"displayModeBar": False})

    intensity_fig = horizontal_bar(links.nlargest(15, "passengers_per_scheduled_train"), "passengers_per_scheduled_train", "link_label", "Highest demand per scheduled train", color=RED, height=540)
    intensity_fig.update_xaxes(title_text="Passengers per scheduled train")
    intensity_fig.update_yaxes(title_text=None)
    st.plotly_chart(intensity_fig, width="stretch", config={"displayModeBar": False})

    loads_fig = horizontal_bar(links.nlargest(15, "passenger_load"), "passenger_load", "link_label", "Busiest inter-station links", color=BLUE, height=540)
    loads_fig.update_xaxes(title_text="Passenger load")
    loads_fig.update_yaxes(title_text=None)
    st.plotly_chart(loads_fig, width="stretch", config={"displayModeBar": False})

    st.warning("Passengers per scheduled train measures demand intensity. It is not train occupancy, crowding, or capacity utilisation.")
    with st.expander("View filtered link data"):
        st.dataframe(links[["line", "direction", "from_station", "to_station", "passenger_load", "scheduled_trains", "passengers_per_scheduled_train"]].sort_values("passenger_load", ascending=False), width="stretch", hide_index=True)
