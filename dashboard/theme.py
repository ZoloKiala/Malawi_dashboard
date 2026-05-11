"""Shared colors and Plotly layout helpers for the Django dashboard."""
from __future__ import annotations

import plotly.graph_objects as go

PRIMARY = "#2F855A"
ACCENT = "#C2410C"
NEUTRAL = "#3B4A54"
GREEN = "#3A7CA5"
ORANGE = "#D97706"
TEXT = "#1F2A24"
MUTED = "#68756E"
GRID = "#E3E9E1"

PLOTLY_LAYOUT = dict(
    template="simple_white",
    font=dict(family="Inter, Helvetica, Arial, sans-serif", color=TEXT, size=12),
    title=dict(font=dict(size=14, color=TEXT, weight=600)),
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)",
    margin=dict(l=54, r=18, t=42, b=46),
    legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=11), title_text=""),
    hoverlabel=dict(bgcolor=TEXT, bordercolor=TEXT, font=dict(color="white")),
)


def apply_layout(fig: go.Figure, **overrides) -> go.Figure:
    fig.update_layout(**{**PLOTLY_LAYOUT, **overrides})
    fig.update_xaxes(showgrid=False, ticks="outside", tickcolor="#C9D4C8", linecolor="#C9D4C8")
    fig.update_yaxes(showgrid=True, gridcolor=GRID, ticks="outside", tickcolor="#C9D4C8", linecolor="#C9D4C8")
    return fig
