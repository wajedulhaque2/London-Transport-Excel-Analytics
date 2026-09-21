from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go


BLUE = "#0019A8"
RED = "#E32017"
GREEN = "#00782A"
LIGHT_BLUE = "#2D8BBA"
MUTED = "#64748B"


def style_figure(fig: go.Figure, height: int = 390) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=58, b=18),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial, sans-serif", color="#1F2937"),
        title_font=dict(size=17, color="#111827"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=13),
    )
    fig.update_xaxes(showgrid=False, linecolor="#D9E0EA")
    fig.update_yaxes(gridcolor="#E8EDF4", zeroline=False)
    return fig


def line_chart(frame, x, series, title, percent_axis=False, height=390):
    fig = go.Figure()
    colors = [BLUE, RED, GREEN, LIGHT_BLUE]
    for (column, label), color in zip(series.items(), colors, strict=False):
        fig.add_trace(
            go.Scatter(
                x=frame[x],
                y=frame[column],
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=3),
                marker=dict(size=5),
                hovertemplate=f"%{{x}}<br>{label}: %{{y:,.2f}}<extra></extra>",
            )
        )
    if percent_axis:
        fig.update_yaxes(tickformat=".0%")
    return style_figure(fig.update_layout(title=title), height)


def horizontal_bar(frame, x, y, title, color=BLUE, percent_axis=False, height=390):
    ordered = frame.sort_values(x, ascending=True)
    fig = px.bar(ordered, x=x, y=y, orientation="h", title=title)
    fig.update_traces(marker_color=color, hovertemplate="%{y}<br>%{x:,.2f}<extra></extra>")
    if percent_axis:
        fig.update_xaxes(tickformat=".0%")
    return style_figure(fig, height)
