from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from chart_utils import BLUE, GREEN, RED, horizontal_bar, line_chart, style_figure
from metrics import compact_number, percent, safe_divide, service_summary


def _by_line(frame):
    rows = []
    for line, group in frame.groupby("line", observed=True):
        rows.append({"line": line, **service_summary(group)})
    return __import__("pandas").DataFrame(rows).sort_values("service_delivery", ascending=False).reset_index(drop=True)


def _by_period(frame):
    rows = []
    for period, group in frame.groupby("period", observed=True):
        rows.append({"reporting_period": int(period), **service_summary(group)})
    return __import__("pandas").DataFrame(rows).sort_values("reporting_period")


def render(data: dict[str, object]) -> None:
    source = data["service_records"]
    years = sorted(source["financial_year"].unique().tolist(), reverse=True)
    financial_year = st.sidebar.selectbox("Financial year", years, key="service_year")
    fy = source.loc[source["financial_year"] == financial_year]
    line_options = ["All lines"] + sorted(fy["line"].unique().tolist())
    selected_line = st.sidebar.selectbox("Underground line", line_options, key="service_line")
    selected = fy if selected_line == "All lines" else fy.loc[fy["line"] == selected_line]

    summary = service_summary(selected)
    lines = _by_line(fy)
    periods = _by_period(selected)
    rank = "—" if selected_line == "All lines" else int(lines.index[lines["line"] == selected_line][0]) + 1

    st.title("Underground line performance")
    st.caption("Actual versus scheduled kilometres by financial year, reporting period, and line")
    st.markdown(
        f'<div class="scope-note">Financial year <b>{financial_year}</b> · <b>{selected_line}</b>. '
        'This TfL financial-year view remains separate from calendar-year passenger demand.</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    cols[0].metric("Service delivery", percent(summary["service_delivery"]))
    cols[1].metric("Peak delivery", percent(summary["peak_delivery"]))
    cols[2].metric("Off-peak delivery", percent(summary["off_peak_delivery"]))
    cols[3].metric("Undelivered km", compact_number(summary["scheduled_total_km"] - summary["actual_total_km"]))
    cols[4].metric("Line service rank", rank)
    totals = st.columns(2)
    totals[0].metric("Actual kilometres", compact_number(summary["actual_total_km"]))
    totals[1].metric("Scheduled kilometres", compact_number(summary["scheduled_total_km"]))

    st.plotly_chart(line_chart(periods, "reporting_period", {"service_delivery": "Service delivery", "peak_delivery": "Peak delivery", "off_peak_delivery": "Off-peak delivery"}, f"Service delivery by reporting period — {selected_line}", percent_axis=True, height=430), width="stretch", config={"displayModeBar": False})
    left, right = st.columns(2)
    with left:
        st.plotly_chart(horizontal_bar(lines, "service_delivery", "line", f"Service delivery by line — {financial_year}", color=BLUE, percent_axis=True), width="stretch", config={"displayModeBar": False})
    with right:
        fig = go.Figure()
        fig.add_bar(x=lines["line"], y=lines["peak_delivery"], name="Peak", marker_color=RED)
        fig.add_bar(x=lines["line"], y=lines["off_peak_delivery"], name="Off-peak", marker_color=GREEN)
        fig.update_layout(title="Peak versus off-peak delivery", barmode="group")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})

    if financial_year == "2024-25":
        st.warning("TfL identifies periods 6 and 8 as partial and period 7 as unavailable following the September 2024 cyber incident.")
    with st.expander("View line performance data"):
        st.dataframe(lines, width="stretch", hide_index=True)
