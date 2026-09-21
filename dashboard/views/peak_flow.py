from __future__ import annotations

import streamlit as st

from chart_utils import BLUE, RED, horizontal_bar, line_chart
from metrics import compact_number, percent


def render(data: dict[str, object]) -> None:
    metadata = data["metadata"]
    gate = data["numbat_gate_evening"]
    platform = data["numbat_platform_evening"]
    intensity = data["numbat_intensity_evening"]
    loads = data["numbat_link_load_evening"]

    st.sidebar.selectbox("Time band", ["Evening (19:00–22:00)"], disabled=True, key="numbat_time")
    st.sidebar.selectbox("Station", ["All stations in cached output"], disabled=True, key="numbat_station")
    st.sidebar.selectbox("NUMBAT line", ["All lines in cached output"], disabled=True, key="numbat_line")

    st.title("Peak flow analysis")
    st.caption("NUMBAT 2024 TWT typical-day station, platform and link flows")
    st.markdown(
        '<div class="scope-note">Quarter-hour ordering follows the NUMBAT traffic day. '
        'This cached slice covers 19:00–22:00; it is not an annual daily total.</div>',
        unsafe_allow_html=True,
    )

    entries = gate["entries"].sum()
    exits = gate["exits"].sum()
    boarders = platform["boarders"].sum()
    alighters = platform["alighters"].sum()
    cols = st.columns(5)
    cols[0].metric("Evening gate footfall", compact_number(entries + exits))
    cols[1].metric("Entries", compact_number(entries))
    cols[2].metric("Exits", compact_number(exits))
    cols[3].metric("Boarders", compact_number(boarders))
    cols[4].metric("Alighters", compact_number(alighters))

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            line_chart(
                gate,
                "quarter_hour",
                {"entries": "Entries", "exits": "Exits"},
                "15-minute station entry and exit profile",
            ),
            width="stretch",
            config={"displayModeBar": False},
        )
    with right:
        st.plotly_chart(
            line_chart(
                platform,
                "quarter_hour",
                {"boarders": "Boarders", "alighters": "Alighters"},
                "Platform boarders and alighters",
            ),
            width="stretch",
            config={"displayModeBar": False},
        )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            horizontal_bar(
                intensity,
                "passengers_per_scheduled_train",
                "link",
                "Highest demand per scheduled train",
                color=RED,
            ),
            width="stretch",
            config={"displayModeBar": False},
        )
    with right:
        st.plotly_chart(
            horizontal_bar(loads, "passenger_load", "link", "Busiest inter-station links", color=BLUE),
            width="stretch",
            config={"displayModeBar": False},
        )

    st.markdown(
        '<div class="warning-note"><b>Interpretation:</b> Passengers per Scheduled Train is a '
        'demand-intensity metric. It is not train occupancy, crowding percentage or capacity utilisation.</div>',
        unsafe_allow_html=True,
    )
    st.caption(metadata["numbat_context"])
