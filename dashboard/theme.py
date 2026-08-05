"""Shared colors and Plotly layout helpers for the Django dashboard."""
from __future__ import annotations

import plotly.graph_objects as go

# IWMI brand palette — Dark Blue core (branding.iwmi.org).
PRIMARY = "#28537D"   # dark blue
ACCENT = "#E86933"    # orange
NEUTRAL = "#5B6B7A"
GREEN = "#5088C6"     # light blue (secondary series)
ORANGE = "#DD9103"    # yellow
TEXT = "#1C2B3A"
MUTED = "#93A1AE"
GRID = "#E8E7E7"

PLOTLY_LAYOUT = dict(
    template="simple_white",
    font=dict(family="Public Sans, Helvetica, Arial, sans-serif", color=TEXT, size=12),
    title=dict(font=dict(size=14, color=TEXT, weight=600)),
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)",
    margin=dict(l=54, r=18, t=42, b=46),
    legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=11), title_text=""),
    hoverlabel=dict(bgcolor="#1F4266", bordercolor="#1F4266", font=dict(color="white")),
)


def apply_layout(fig: go.Figure, **overrides) -> go.Figure:
    fig.update_layout(**{**PLOTLY_LAYOUT, **overrides})
    fig.update_xaxes(showgrid=False, ticks="outside", tickcolor="#D8DCE0", linecolor="#D8DCE0")
    fig.update_yaxes(showgrid=True, gridcolor=GRID, ticks="outside", tickcolor="#D8DCE0", linecolor="#D8DCE0")
    return fig
