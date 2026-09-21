from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from chart_utils import BLUE, GREEN, RED, horizontal_bar, line_chart, style_figure
from metrics import compact_number, percent


def render(data: dict[str, object]) -> None:
    service = data["service_by_line"].sort_values("service_delivery", ascending=False)
    peak = data["service_peak_offpeak_by_line"]
    period = data["service_reporting_period"]
    metadata = data["metadata"]

    options = ["All lines"] + service["line"].tolist()
    selected_line = st.sidebar.selectbox("Underground line", options, key="service_line")
    st.sidebar.selectbox(
        "Financial year context",
        [metadata["service_detail_context"]],
        disabled=True,
        key="service_year",
    )

    st.title("Underground line performance")
    st.caption("Actual versus scheduled service, reporting-period trends and line comparisons")
    st.markdown(
        f'<div class="scope-note">{metadata["service_detail_context"]}. '
        'Calendar-year demand filters are deliberately separate from this view.</div>',
        unsafe_allow_html=True,
    )

    overall = metadata["kpis"]["service_detail"]
    if selected_line == "All lines":
        service_delivery = overall["Service Delivery %"]
        peak_delivery = overall["Peak Delivery %"]
        off_peak_delivery = overall["Off-Peak Delivery %"]
        rank = "—"
        undelivered = compact_number(overall["Undelivered KM"])
    else:
        service_row = service.loc[service["line"] == selected_line].iloc[0]
        peak_row = peak.loc[peak["line"] == selected_line].iloc[0]
        service_delivery = service_row["service_delivery"]
        peak_delivery = peak_row["peak_delivery"]
        off_peak_delivery = peak_row["off_peak_delivery"]
        rank = int(service.reset_index(drop=True).index[service.reset_index(drop=True)["line"] == selected_line][0]) + 1
        undelivered = "Not in cache"

    cols = st.columns(5)
    cols[0].metric("Service delivery", percent(service_delivery))
    cols[1].metric("Peak delivery", percent(peak_delivery))
    cols[2].metric("Off-peak delivery", percent(off_peak_delivery))
    cols[3].metric("Undelivered km", undelivered)
    cols[4].metric("Line service rank", rank)

    st.markdown(
        '<div class="warning-note">Actual and scheduled kilometre totals are not exposed in the '
        'cached Pivot Support output. The app preserves the documented delivery rates and marks those totals unavailable '
        'until the source data is added.</div>',
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        line_chart(
            period,
            "reporting_period",
            {
                "service_delivery": "Service delivery",
                "peak_delivery": "Peak delivery",
                "off_peak_delivery": "Off-peak delivery",
            },
            "Service delivery by reporting period",
            percent_axis=True,
            height=430,
        ),
        width="stretch",
        config={"displayModeBar": False},
    )
    st.caption("Reporting-period trend is the aggregate cached selection and does not change with the line selector.")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            horizontal_bar(
                service,
                "service_delivery",
                "line",
                "Service delivery by Underground line",
                color=BLUE,
                percent_axis=True,
            ),
            width="stretch",
            config={"displayModeBar": False},
        )
    with right:
        fig = go.Figure()
        fig.add_bar(x=peak["line"], y=peak["peak_delivery"], name="Peak", marker_color=RED)
        fig.add_bar(x=peak["line"], y=peak["off_peak_delivery"], name="Off-peak", marker_color=GREEN)
        fig.update_layout(title="Peak versus off-peak delivery", barmode="group")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})

    st.markdown(
        '<div class="warning-note"><b>Known source limitation:</b> 2024/25 P6 and P8 are partial. '
        'P7 is unavailable following the TfL cyber incident.</div>',
        unsafe_allow_html=True,
    )
    with st.expander("View cached line performance data"):
        st.dataframe(
            service.merge(peak, on="line", how="left"),
            width="stretch",
            hide_index=True,
        )
