"""Django views that render the WASA baseline dashboard with Plotly.js."""
from __future__ import annotations

import json
from urllib.parse import urlencode

import pandas as pd
import plotly.graph_objects as go
from django.shortcuts import render
from plotly.subplots import make_subplots
from plotly.utils import PlotlyJSONEncoder

import data
from .theme import ACCENT, GREEN, GRID, NEUTRAL, ORANGE, PRIMARY, apply_layout

NAV_ITEMS = [
    ("overview", "Overview", "/"),
    ("demographics", "Demographics", "/demographics/"),
    ("production", "Production", "/production/"),
    ("adoption", "Adoption", "/adoption/"),
    ("recommendations", "Recommendations", "/recommendations/"),
]


def _filters(request):
    districts = request.GET.getlist("district") or data.DISTRICTS
    genders = request.GET.getlist("gender") or data.GENDERS
    districts = [d for d in districts if d in data.DISTRICTS]
    genders = [g for g in genders if g in data.GENDERS]
    return districts or data.DISTRICTS, genders or data.GENDERS


def _query_string(districts: list[str], genders: list[str]) -> str:
    params = [("district", d) for d in districts] + [("gender", g) for g in genders]
    return urlencode(params)


def _figure_json(fig: go.Figure) -> str:
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def _records(df: pd.DataFrame) -> dict:
    return {"columns": list(df.columns), "rows": df.to_dict("records")}


def _base_context(request, page: str, title: str, subtitle: str) -> dict:
    districts, genders = _filters(request)
    return {
        "active_page": page,
        "title": title,
        "subtitle": subtitle,
        "nav_items": NAV_ITEMS,
        "district_options": data.DISTRICTS,
        "gender_options": data.GENDERS,
        "selected_districts": districts,
        "selected_genders": genders,
        "query_string": _query_string(districts, genders),
        "focus": f"{len(districts)} districts / {len(genders)} gender groups",
    }


def _asset_chart() -> go.Figure:
    df = data.asset_ownership.sort_values("Yes")
    fig = go.Figure()
    fig.add_bar(
        y=df["Category"], x=df["Yes"], name="Owns asset", orientation="h",
        marker_color=PRIMARY, text=[f"{v:.1f}%" for v in df["Yes"]],
        textposition="inside", textfont=dict(color="white", size=11),
        hovertemplate="%{y}<br>%{x:.1f}% own assets<extra></extra>",
    )
    fig.add_bar(
        y=df["Category"], x=df["No"], name="Does not own", orientation="h",
        marker_color="#EEF3F8", hovertemplate="%{y}<br>%{x:.1f}% do not own<extra></extra>",
    )
    fig.update_layout(barmode="stack", height=340, xaxis_title="Share of households")
    fig.update_xaxes(range=[0, 100], ticksuffix="%")
    return apply_layout(fig, margin=dict(l=170, r=16, t=24, b=44))


def _household_stack(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.hh_by_district_gender, districts)
    fig = go.Figure()
    fig.add_bar(x=df["District"], y=df["Male-headed"], name="Male-headed", marker_color=PRIMARY)
    fig.add_bar(x=df["District"], y=df["Female-headed"], name="Female-headed", marker_color=ACCENT)
    fig.add_bar(x=df["District"], y=df["Child-headed"], name="Child-headed", marker_color=NEUTRAL)
    fig.update_layout(barmode="stack", height=330, yaxis_title="Households")
    return apply_layout(fig)


def _district_map(districts: list[str]) -> go.Figure:
    geo = data.load_malawi_districts()
    df = data.filter_by_district(data.hh_by_district_gender, districts).copy()
    if geo is None:
        fig = go.Figure()
        fig.add_annotation(
            text="District boundary file is unavailable.", x=0.5, y=0.5,
            xref="paper", yref="paper", showarrow=False, font=dict(size=15, color=NEUTRAL),
        )
        return apply_layout(fig, height=430, xaxis=dict(visible=False), yaxis=dict(visible=False))

    all_districts = [feature["properties"].get("NAME_1") for feature in geo["features"]]
    fig = go.Figure()
    fig.add_trace(
        go.Choropleth(
            geojson=geo,
            locations=all_districts,
            z=[1] * len(all_districts),
            featureidkey="properties.NAME_1",
            colorscale=[[0, "#EEF3F8"], [1, "#EEF3F8"]],
            showscale=False,
            marker_line_color="#FFFFFF",
            marker_line_width=0.7,
            hovertemplate="<b>%{location}</b><br>No WASA baseline sample<extra></extra>",
            name="Other districts",
        )
    )
    fig.add_trace(
        go.Choropleth(
            geojson=geo, locations=df["District"], z=df["Total"],
            featureidkey="properties.NAME_1",
            colorscale=[[0, "#EAF1F8"], [0.35, "#9EC0E0"], [0.7, "#5088C6"], [1, "#28537D"]],
            marker_line_color="#FFFFFF", marker_line_width=0.9,
            colorbar=dict(
                title="HHs", thickness=10, len=0.6, x=0.98, xanchor="right",
                y=0.5, bgcolor="rgba(255,255,255,0.78)", outlinewidth=0,
            ),
            customdata=df[["Region", "Female-headed", "Male-headed"]],
            hovertemplate=(
                "<b>%{location}</b><br>Region: %{customdata[0]}<br>"
                "Households: %{z:,}<br>Female-headed: %{customdata[1]:,}<br>"
                "Male-headed: %{customdata[2]:,}<extra></extra>"
            ),
            name="Surveyed districts",
        )
    )
    fig.update_geos(
        fitbounds="geojson", visible=False, bgcolor="rgba(255,255,255,0)",
        showcountries=False, showcoastlines=False, showland=False,
        projection=dict(type="mercator"),
        domain=dict(x=[0, 1], y=[0, 1]),
    )
    return apply_layout(fig, height=380, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)


def _yield_chart(districts: list[str], genders: list[str]) -> go.Figure:
    df = data.filter_long_by(data.maize_yield_long, districts, genders)
    fig = go.Figure()
    for gender, color in {"Female-headed": ACCENT, "Male-headed": PRIMARY}.items():
        sub = df[df["Gender"] == gender]
        if sub.empty:
            continue
        fig.add_bar(
            x=sub["District"], y=sub["Yield_kg_ha"], name=gender, marker_color=color,
            hovertemplate="%{x}<br>%{y:,.0f} kg/ha<extra>" + gender + "</extra>",
        )
    fig.update_layout(barmode="group", height=340, yaxis_title="Maize yield (kg/ha)")
    return apply_layout(fig)


def _adoption_heatmap(districts: list[str]) -> go.Figure:
    df = data.tech_adoption_counts.copy()
    cols = [d for d in data.DISTRICTS if d in districts]
    fig = go.Figure(
        go.Heatmap(
            z=df[cols].values, x=cols, y=df["Technology"],
            colorscale=[[0, "#F1F5FA"], [0.5, "#7FA8D0"], [1, PRIMARY]],
            colorbar=dict(title="HHs", thickness=10),
            hovertemplate="%{y}<br>%{x}: %{z} HHs<extra></extra>",
        )
    )
    fig.update_layout(height=360)
    return apply_layout(fig, margin=dict(l=150, r=18, t=18, b=54))


def _food_security_chart(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.food_security, districts)
    fig = go.Figure()
    fig.add_bar(x=df["District"], y=df["Food shortage (%)"], name="Food shortage", marker_color=ACCENT)
    fig.add_bar(x=df["District"], y=df["Income shock (%)"], name="Income shock", marker_color=ORANGE)
    fig.add_scatter(
        x=df["District"], y=df["Coping severity"], name="Coping severity",
        mode="lines+markers", yaxis="y2", line=dict(color=NEUTRAL, width=2.4), marker=dict(size=8),
    )
    fig.update_layout(
        barmode="group", height=350,
        yaxis=dict(title="Households (%)", range=[0, 105]),
        yaxis2=dict(title="Coping score", overlaying="y", side="right", showgrid=False),
    )
    return apply_layout(fig)


def _priority_chart(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.priority_scores, districts)
    dims = ["Productivity", "Adoption", "Food security", "Water access", "Market access", "Inclusion"]
    avg = df.melt(id_vars="District", value_vars=dims, var_name="Dimension", value_name="Score")
    avg = avg.groupby("Dimension", as_index=False)["Score"].mean().sort_values("Score")
    fig = go.Figure(
        go.Bar(
            x=avg["Score"], y=avg["Dimension"], orientation="h",
            marker_color=[ACCENT if v < 2.5 else GREEN if v >= 4 else PRIMARY for v in avg["Score"]],
            text=[f"{v:.1f}" for v in avg["Score"]], textposition="outside",
            hovertemplate="%{y}<br>Average priority score: %{x:.1f}<extra></extra>",
        )
    )
    fig.update_layout(height=330, xaxis_title="Average score", yaxis_title=None)
    fig.update_xaxes(range=[0, 5.4], dtick=1)
    return apply_layout(fig, margin=dict(l=120, r=28, t=18, b=44))


def _structure_chart(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.hh_structure, districts)
    parts = [
        "Child headed", "Female headed de facto", "Female headed single",
        "Male headed single", "Male headed with wife", "Male headed with wives",
    ]
    colors = ["#0297A6", ACCENT, ORANGE, "#46BBD4", PRIMARY, NEUTRAL]
    fig = go.Figure()
    for part, color in zip(parts, colors):
        fig.add_bar(x=df["District"], y=df[part], name=part, marker_color=color)
    fig.update_layout(barmode="stack", height=380, yaxis_title="Households")
    return apply_layout(fig)


def _land_chart(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.land_holdings, districts)
    parts = ["Food crop area (ha)", "Horticulture area (ha)", "Aquaculture area (ha)", "Fallow area (ha)"]
    colors = [PRIMARY, "#22AD7A", NEUTRAL, "#DD9103"]
    fig = go.Figure()
    for part, color in zip(parts, colors):
        fig.add_bar(x=df["District"], y=df[part], name=part, marker_color=color)
    fig.update_layout(barmode="stack", height=360, yaxis_title="Average area (ha)")
    return apply_layout(fig)


def _age_education_chart(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.hh_structure, districts)
    fig = go.Figure()
    fig.add_scatter(x=df["District"], y=df["HH age (avg yrs)"], name="Head age", mode="lines+markers", line=dict(color=PRIMARY, width=2))
    fig.add_scatter(x=df["District"], y=df["Education (yrs)"], name="Education", mode="lines+markers", line=dict(color=ACCENT, width=2))
    fig.add_scatter(x=df["District"], y=df["Adults (avg)"], name="Adults per HH", mode="lines+markers", line=dict(color=NEUTRAL, width=2, dash="dot"))
    fig.update_layout(height=360, yaxis_title="Average")
    return apply_layout(fig)


def _crop_alloc_chart(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.crop_allocation, districts)
    colors = {
        "Maize": PRIMARY, "Groundnuts": "#22AD7A", "Soybean": "#46BBD4",
        "Sweet Potato": ACCENT, "Cassava": "#DD9103", "Tobacco": "#0297A6", "Cowpea": GREEN,
    }
    fig = go.Figure()
    for crop, color in colors.items():
        fig.add_bar(x=df["District"], y=df[crop], name=crop, marker_color=color)
    fig.update_layout(barmode="stack", height=380, yaxis_title="Share of cultivated area (%)")
    return apply_layout(fig)


def _seasonal_chart(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.seasonal_participation, districts)
    fig = go.Figure()
    fig.add_bar(x=df["District"], y=df["Summer (%)"], name="Summer", marker_color=PRIMARY)
    fig.add_bar(x=df["District"], y=df["Winter (%)"], name="Winter", marker_color="#DD9103")
    fig.update_layout(barmode="group", height=340, yaxis_title="Participation (%)", yaxis=dict(range=[0, 105]))
    return apply_layout(fig)


def _gaps_chart(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.gender_gaps, districts)
    fig = make_subplots(rows=1, cols=3, subplot_titles=("Fertilizer use", "Intercropping", "Irrigation"), horizontal_spacing=0.10)
    xmax = max(abs(v) for col in ("Fertilizer", "Intercropping", "Irrigation") for v in df[col]) * 1.35 if not df.empty else 30
    for idx, col in enumerate(["Fertilizer", "Intercropping", "Irrigation"], start=1):
        sub = df.sort_values(col)
        vals = list(sub[col])
        fig.add_bar(
            x=vals, y=sub["District"], orientation="h", showlegend=False,
            marker_color=[GREEN if v >= 0 else ACCENT for v in vals],
            text=[f"{v:+.1f}" for v in vals], textposition="outside",
            hovertemplate="%{y}: %{x:+.1f} pp<extra>" + col + "</extra>",
            row=1, col=idx,
        )
        fig.update_xaxes(range=[-xmax, xmax], zeroline=True, zerolinecolor="#444", showgrid=True, gridcolor=GRID, row=1, col=idx)
    fig.add_bar(x=[None], y=[None], marker_color=GREEN, name="Male-headed adopt more")
    fig.add_bar(x=[None], y=[None], marker_color=ACCENT, name="Female-headed adopt more")
    fig.update_layout(height=420, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"), margin=dict(l=80, r=20, t=60, b=70))
    return apply_layout(fig)


def _csa_chart(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.csa_adoption, districts)
    fig = go.Figure()
    fig.add_bar(x=df["District"], y=df["TLC (%)"], name="Total LandCare", marker_color=PRIMARY)
    fig.add_bar(x=df["District"], y=df["CRS (%)"], name="Catholic Relief Services", marker_color=ACCENT)
    fig.add_bar(x=df["District"], y=df["Other (%)"], name="Other partners", marker_color="#DD9103")
    fig.update_layout(barmode="group", height=360, yaxis_title="CSA-supported HHs (%)")
    return apply_layout(fig)


def _priority_radar(districts: list[str]) -> go.Figure:
    df = data.filter_by_district(data.priority_scores, districts)
    dims = ["Productivity", "Adoption", "Food security", "Water access", "Market access", "Inclusion"]
    colors = [PRIMARY, ACCENT, GREEN, ORANGE, NEUTRAL, "#22AD7A", "#0297A6"]
    fig = go.Figure()
    for i, (_, row) in enumerate(df.iterrows()):
        vals = [row[d] for d in dims] + [row[dims[0]]]
        fig.add_trace(go.Scatterpolar(r=vals, theta=dims + [dims[0]], fill="toself", name=row["District"], line=dict(color=colors[i % len(colors)], width=2), opacity=0.55))
    fig.update_layout(height=520, polar=dict(radialaxis=dict(range=[0, 5], tickvals=[1, 2, 3, 4, 5], gridcolor=GRID), angularaxis=dict(gridcolor=GRID), bgcolor="rgba(255,255,255,0)"), margin=dict(l=40, r=40, t=40, b=40), legend=dict(orientation="v", x=1.05, y=1))
    return apply_layout(fig)


def _overview_table(districts: list[str]) -> pd.DataFrame:
    hh = data.filter_by_district(data.hh_by_district_gender, districts)
    land = data.filter_by_district(data.land_holdings, districts)[["District", "Owned land (ha)", "Food crop area (ha)"]]
    fs = data.filter_by_district(data.food_security, districts)[["District", "Food shortage (%)", "Coping severity"]]
    csa = data.filter_by_district(data.csa_adoption, districts)[["District", "TLC (%)", "CRS (%)"]]
    out = hh[["District", "Region", "Total", "Female-headed", "Male-headed"]]
    return out.merge(land, on="District").merge(fs, on="District").merge(csa, on="District").round(1)


def _render_dashboard(request, page: str, title: str, subtitle: str, charts: list[dict], table: pd.DataFrame, kpis: list[dict] | None = None):
    context = _base_context(request, page, title, subtitle)
    context.update(
        charts=[{**chart, "figure": _figure_json(chart["figure"])} for chart in charts],
        table=_records(table),
        kpis=kpis or [],
    )
    return render(request, "dashboard/page.html", context)


def overview(request):
    context = _base_context(request, "overview", "WASA Malawi baseline dashboard", "Explore household structure, production, adoption, food security, and district priorities.")
    districts, genders = context["selected_districts"], context["selected_genders"]
    df_hh = data.filter_by_district(data.hh_by_district_gender, districts)
    df_yield = data.filter_long_by(data.maize_yield_long, districts, genders)
    total_hh = int(df_hh["Total"].sum())
    female_hh = int(df_hh["Female-headed"].sum())
    female_share = (female_hh / total_hh * 100) if total_hh else 0
    winter = data.filter_by_district(data.seasonal_participation, districts)["Winter (%)"].mean()
    kpis = [
        {"label": "Households surveyed", "value": f"{total_hh:,}", "sub": "filtered baseline records"},
        {"label": "Female-headed HHs", "value": f"{female_share:.1f}%", "sub": f"{female_hh:,} households", "tone": "accent"},
        {"label": "Average maize yield", "value": f"{df_yield['Yield_kg_ha'].mean():,.0f}", "sub": "kg/ha in current view", "tone": "green"},
        {"label": "Winter participation", "value": f"{winter:.1f}%", "sub": "average by district", "tone": "orange"},
    ]
    charts = [
        {"id": "district-map", "title": "Spatial distribution", "subtitle": "Districts shaded by surveyed households. Muted districts shown for geographic context only.", "figure": _district_map(districts), "span": "wide"},
        {"id": "household-stack", "title": "Household head composition", "subtitle": "Stacked count by district", "figure": _household_stack(districts), "span": "side"},
        {"id": "yield", "title": "Maize yield by gender", "subtitle": "Gender filter applies to this panel", "figure": _yield_chart(districts, genders)},
        {"id": "assets", "title": "Asset ownership", "subtitle": "Household asset categories", "figure": _asset_chart()},
        {"id": "adoption-heatmap", "title": "Technology adoption intensity", "subtitle": "Household counts by technology and district", "figure": _adoption_heatmap(districts), "span": "wide"},
        {"id": "priority", "title": "Priority profile", "subtitle": "Average score across selected districts", "figure": _priority_chart(districts), "span": "side"},
        {"id": "food-security", "title": "Food security and shock exposure", "subtitle": "Food shortage and income shock with coping severity", "figure": _food_security_chart(districts), "span": "full"},
    ]
    context.update(charts=[{**chart, "figure": _figure_json(chart["figure"])} for chart in charts], table=_records(_overview_table(districts)), kpis=kpis)
    return render(request, "dashboard/page.html", context)


def demographics(request):
    ctx = _base_context(request, "demographics", "Demographics", "Household composition, head characteristics, and land holdings across selected districts.")
    districts = ctx["selected_districts"]
    return _render_dashboard(
        request, "demographics", ctx["title"], ctx["subtitle"],
        [
            {"id": "structure", "title": "Household composition", "subtitle": "Detailed structure by district", "figure": _structure_chart(districts), "span": "wide"},
            {"id": "age-education", "title": "Age, education, adults", "subtitle": "Average household characteristics", "figure": _age_education_chart(districts), "span": "side"},
            {"id": "land", "title": "Land holdings", "subtitle": "Average area per household", "figure": _land_chart(districts), "span": "full"},
        ],
        data.filter_by_district(data.hh_structure, districts),
    )


def production(request):
    ctx = _base_context(request, "production", "Production", "Crop production patterns by district and household head gender.")
    districts, genders = ctx["selected_districts"], ctx["selected_genders"]
    return _render_dashboard(
        request, "production", ctx["title"], ctx["subtitle"],
        [
            {"id": "yield", "title": "Maize yield", "subtitle": "kg/ha by gender", "figure": _yield_chart(districts, genders), "span": "full"},
            {"id": "crop-allocation", "title": "Crop allocation", "subtitle": "Share of cultivated area", "figure": _crop_alloc_chart(districts), "span": "wide"},
            {"id": "seasonal", "title": "Seasonal participation", "subtitle": "Summer vs winter", "figure": _seasonal_chart(districts), "span": "side"},
        ],
        data.filter_by_district(data.crop_allocation, districts),
    )


def adoption(request):
    ctx = _base_context(request, "adoption", "Adoption", "Technology adoption patterns and gender gaps.")
    districts = ctx["selected_districts"]
    return _render_dashboard(
        request, "adoption", ctx["title"], ctx["subtitle"],
        [
            {"id": "gaps", "title": "Gender gaps in adoption", "subtitle": "Male-headed minus female-headed adoption rate", "figure": _gaps_chart(districts), "span": "full"},
            {"id": "csa", "title": "CSA support by partner", "subtitle": "Share of supported households", "figure": _csa_chart(districts), "span": "side"},
            {"id": "tech-heatmap", "title": "Technology adoption counts", "subtitle": "Households practising each technology", "figure": _adoption_heatmap(districts), "span": "wide"},
        ],
        data.filter_by_district(data.csa_adoption, districts),
    )


def recommendations(request):
    ctx = _base_context(request, "recommendations", "Recommendations", "District-level priority scores and recommended technology bundles.")
    districts = ctx["selected_districts"]
    return _render_dashboard(
        request, "recommendations", ctx["title"], ctx["subtitle"],
        [
            {"id": "priority-radar", "title": "Priority profile by district", "subtitle": "Strengths and gaps across six dimensions", "figure": _priority_radar(districts), "span": "wide"},
            {"id": "food-security", "title": "Food security and shock exposure", "subtitle": "Food shortage, income shock, coping severity", "figure": _food_security_chart(districts), "span": "side"},
        ],
        data.filter_by_district(data.recommendations, districts),
    )
