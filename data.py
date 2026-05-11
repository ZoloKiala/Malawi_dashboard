"""Curated tables from the WASA Malawi baseline report.

All numbers are taken directly from the report tables. Districts are listed in
the same order across tables. Numeric values use floats so they survive pandas
filtering and Plotly serialization.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

DISTRICTS = ["Chikwawa", "Dowa", "Lilongwe", "Mangochi", "Mchinji", "Mulanje", "Salima"]
REGIONS = {
    "Chikwawa": "Southern",
    "Dowa": "Central",
    "Lilongwe": "Central",
    "Mangochi": "Southern",
    "Mchinji": "Central",
    "Mulanje": "Southern",
    "Salima": "Central",
}
GENDERS = ["Female-headed", "Male-headed"]


# -- Asset ownership (report chart 1) ------------------------------------------------
asset_ownership = pd.DataFrame(
    {
        "Category": [
            "Productive agricultural assets",
            "Water & irrigation assets",
            "Energy & technology assets",
            "Financial & market assets",
            "Livestock & animal power",
            "Housing & infrastructure",
        ],
        "Yes": [14.3, 2.2, 13.9, 28.4, 8.3, 14.1],
        "No": [85.7, 97.8, 86.1, 71.6, 91.7, 85.9],
    }
)


# -- Households by district and gender of head (Table 3) ----------------------------
hh_by_district_gender = pd.DataFrame(
    {
        "District": DISTRICTS,
        "Region": [REGIONS[d] for d in DISTRICTS],
        "Child-headed": [0, 0, 1, 1, 0, 0, 0],
        "Female-headed": [18, 12, 52, 66, 47, 32, 22],
        "Male-headed": [98, 79, 148, 116, 141, 74, 90],
        "Total": [116, 91, 201, 183, 188, 106, 112],
    }
)


# -- Household structure detail (Table 5) -------------------------------------------
hh_structure = pd.DataFrame(
    {
        "District": DISTRICTS,
        "Child headed": [0, 0, 1, 1, 0, 0, 0],
        "Female headed de facto": [2, 0, 1, 19, 2, 4, 2],
        "Female headed single": [16, 12, 51, 47, 45, 28, 20],
        "Male headed single": [0, 1, 5, 3, 2, 1, 3],
        "Male headed with wife": [91, 74, 134, 105, 135, 72, 86],
        "Male headed with wives": [7, 4, 9, 8, 4, 1, 1],
        "HH age (avg yrs)": [42.5, 41.9, 46.3, 51.0, 45.3, 46.4, 47.2],
        "Adults (avg)": [5.0, 4.2, 4.6, 6.9, 5.1, 5.6, 5.0],
        "Education (yrs)": [6.5, 6.8, 6.0, 4.4, 6.3, 6.3, 7.9],
    }
)


# -- Land holdings (Table 7) --------------------------------------------------------
land_holdings = pd.DataFrame(
    {
        "District": DISTRICTS,
        "Owned land (ha)": [0.80, 1.20, 0.92, 0.64, 1.27, 0.43, 1.66],
        "Rented land (ha)": [0.61, 0.27, 0.54, 0.33, 0.49, 0.18, 0.84],
        "Food crop area (ha)": [0.72, 0.93, 0.77, 0.56, 1.00, 0.38, 1.22],
        "Horticulture area (ha)": [0.06, 0.05, 0.09, 0.05, 0.11, 0.02, 0.01],
        "Aquaculture area (ha)": [0.03, 0.00, 0.02, 0.04, 0.03, 0.00, 0.00],
        "Fallow area (ha)": [0.05, 0.06, 0.02, 0.07, 0.04, 0.01, 0.38],
    }
)


# -- Maize yield by district x gender (Table 16 / report chart 2A) ------------------
maize_yield_long = pd.DataFrame(
    {
        "District": DISTRICTS * 2,
        "Gender": ["Female-headed"] * 7 + ["Male-headed"] * 7,
        "Yield_kg_ha": [
            411.7, 1927.2, 756.8, 1004.4, 906.1, 402.3, 1062.8,
            961.9, 2294.3, 986.8, 779.1, 1477.3, 406.8, 954.4,
        ],
    }
)


# -- Gender adoption gaps (report chart 2B): pp = male - female ---------------------
gender_gaps = pd.DataFrame(
    {
        "District": DISTRICTS,
        "Fertilizer": [-13.0, -13.3, 7.4, 8.1, 11.3, 26.8, 7.5],
        "Intercropping": [22.6, -9.7, -2.1, -25.5, 5.1, -12.5, -6.7],
        "Irrigation": [-4.3, -4.7, -2.4, 3.5, -1.1, -7.1, 4.2],
    }
)


# -- Crop allocation (Table 12) -----------------------------------------------------
crop_allocation = pd.DataFrame(
    {
        "District": DISTRICTS,
        "Maize": [32.0, 41.9, 41.2, 43.6, 36.8, 22.2, 30.9],
        "Groundnuts": [0.0, 8.9, 10.2, 10.2, 24.2, 6.1, 35.6],
        "Soybean": [0.0, 18.7, 12.9, 8.3, 24.8, 0.0, 11.2],
        "Sweet Potato": [0.6, 2.8, 3.8, 4.2, 1.4, 2.5, 1.2],
        "Cassava": [0.0, 0.0, 0.0, 6.0, 0.2, 36.3, 0.0],
        "Tobacco": [0.0, 21.0, 27.0, 0.0, 9.6, 0.0, 0.0],
        "Cowpea": [1.8, 0.6, 0.0, 0.0, 0.0, 0.0, 3.8],
    }
)


# -- Winter / summer participation (Table 13) ---------------------------------------
seasonal_participation = pd.DataFrame(
    {
        "District": DISTRICTS,
        "Region": [REGIONS[d] for d in DISTRICTS],
        "Summer (%)": [100.0] * 7,
        "Winter (%)": [21.6, 51.6, 58.2, 20.0, 41.5, 22.6, 17.1],
        "Main summer crops": [
            "Maize, Sorghum", "Maize, Groundnuts", "Maize, Groundnuts",
            "Maize, Rice", "Maize, Groundnuts", "Maize, Rice", "Maize, Beans",
        ],
        "Main winter crops": [
            "Green maize, Tomatoes", "Tomatoes, Green maize", "Green maize, Tomatoes",
            "Green maize, Tomatoes", "Green maize, Common beans",
            "Tomatoes, Green maize", "Tomatoes, Green maize",
        ],
    }
)


# -- CSA adoption by district (Table 2) ---------------------------------------------
csa_adoption = pd.DataFrame(
    {
        "District": DISTRICTS,
        "Region": [REGIONS[d] for d in DISTRICTS],
        "TLC (%)": [16.5, 53.8, 62.7, 19.0, 67.0, 8.5, 37.8],
        "CRS (%)": [3.5, 1.1, 0.0, 4.5, 1.1, 2.8, 3.6],
        "Other (%)": [7.8, 9.9, 2.5, 10.6, 1.6, 16.0, 0.9],
        "Main adopted CSA technologies": [
            "Agroforestry; Conservation agriculture; Manure management",
            "Manure management; Conservation agriculture; Agroforestry",
            "Manure management; Agroforestry; Conservation agriculture",
            "Agroforestry; Conservation agriculture; Manure management",
            "Manure management; Conservation agriculture; Agroforestry",
            "Manure management; Agroforestry; Conservation agriculture",
            "Conservation agriculture; Manure management; Agroforestry",
        ],
    }
)


# -- Technology adoption counts by district (Table 14) ------------------------------
tech_adoption_counts = pd.DataFrame(
    {
        "Technology": [
            "Agroforestry", "Cereal-legume rotation", "Contour ridges / bunds",
            "Manure application", "Mulching", "Residue retention", "Tied ridges",
        ],
        "Chikwawa": [4, 1, 22, 32, 15, 5, 21],
        "Dowa": [15, 11, 53, 79, 11, 23, 22],
        "Lilongwe": [39, 18, 38, 178, 17, 53, 41],
        "Mangochi": [21, 8, 54, 150, 30, 39, 38],
        "Mchinji": [32, 20, 41, 141, 24, 60, 13],
        "Mulanje": [8, 2, 38, 92, 11, 21, 33],
        "Salima": [13, 8, 57, 96, 19, 13, 42],
    }
)


# -- Food security indicators (Table 21) --------------------------------------------
food_security = pd.DataFrame(
    {
        "District": DISTRICTS,
        "Dietary diversity": [3.6, 4.1, 3.8, 4.2, 3.6, 3.5, 3.7],
        "Coping severity": [189.2, 22.8, 50.8, 49.9, 52.1, 128.0, 50.3],
        "Food shortage (%)": [92.0, 39.6, 56.7, 74.3, 51.9, 87.6, 56.0],
        "Income shock (%)": [95.9, 87.7, 88.2, 91.5, 89.9, 95.1, 92.1],
    }
)


# -- District priority scores (Table 31) - 1=weakest, 5=strongest -------------------
priority_scores = pd.DataFrame(
    {
        "District": ["Chikwawa", "Mulanje", "Mangochi", "Salima", "Dowa", "Lilongwe", "Mchinji"],
        "Productivity": [1, 1, 3, 3, 5, 3, 3],
        "Adoption": [3, 2, 4, 3, 5, 5, 4],
        "Food security": [1, 1, 2, 2, 2, 2, 2],
        "Water access": [2, 1, 2, 1, 3, 3, 3],
        "Market access": [2, 1, 2, 3, 5, 5, 3],
        "Inclusion": [1, 1, 5, 3, 3, 1, 3],
    }
)


# -- Recommended technology bundles by district (Table 32) --------------------------
recommendations = pd.DataFrame(
    {
        "District": ["Chikwawa", "Mulanje", "Mangochi", "Salima", "Dowa", "Lilongwe", "Mchinji"],
        "Lead partner": [
            "Catholic Relief Services", "Catholic Relief Services",
            "Catholic Relief Services", "Total LandCare",
            "Total LandCare", "Total LandCare", "Total LandCare",
        ],
        "Recommended technology bundle": [
            "Flood-resilient maize systems; drought-tolerant legumes; check dams; vetiver stabilization; rehabilitation of damaged irrigation/water systems; household soil moisture conservation",
            "Cassava-maize resilience systems; slope stabilization; erosion control; treadle irrigation; tree restoration; soil fertility restoration",
            "Maize-legume diversification; selective irrigation expansion; riverbank stabilization; savings-linked input access; horticulture expansion",
            "Legume intensification; irrigation expansion; climate information services; water harvesting; dry season production",
            "Maize-tobacco productivity systems; soil fertility restoration; efficient water use technologies; sustainable intensification",
            "Diversified maize-legume systems; input optimization; scale-appropriate mechanization; irrigation expansion; aggregation support",
            "Legume commercialization; soil fertility restoration; selective irrigation expansion; aggregation and storage systems",
        ],
        "Implementation considerations": [
            "Prioritise restoration of water control systems before productivity expansion. FGDs highlighted destroyed schemes, flooding, tool shortages, weak extension support.",
            "Focus first on land stabilization and household resilience before commercialization. FGDs highlighted annual flooding, poor roads, sedimentation, demand for irrigation equipment.",
            "Build on existing irrigation momentum and savings groups while protecting river systems and strengthening flood resilience.",
            "Strengthen integration of weather information, irrigation planning, and market-oriented production.",
            "Protect productivity gains while reducing soil degradation and strengthening long-term sustainability.",
            "Mechanization should remain appropriate to actual farm sizes and financing realities. Focus on scaling commercially viable systems.",
            "Focus on productivity stabilization, market aggregation, and reducing seasonal water-related risks.",
        ],
    }
)


_DASHBOARD_DIR = Path(__file__).resolve().parent
_GEOJSON_PATH = _DASHBOARD_DIR / "assets" / "malawi_districts.geojson"
_GADM_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_MWI_1.json"
_geojson_cache: dict | None = None


def _is_feature_collection(obj: object) -> bool:
    return isinstance(obj, dict) and obj.get("type") == "FeatureCollection"


def load_malawi_districts() -> dict | None:
    """Return Malawi district boundaries (GADM admin-1) as a GeoJSON FeatureCollection.

    Caches in-memory after the first successful load, and on disk under
    assets/malawi_districts.geojson. Downloads from GADM 4.1 if the cache file
    is missing or corrupt. Returns None on network failure.
    """
    global _geojson_cache
    if _geojson_cache is not None:
        return _geojson_cache

    if _GEOJSON_PATH.exists():
        try:
            parsed = json.loads(_GEOJSON_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            parsed = None
        if _is_feature_collection(parsed):
            _geojson_cache = parsed
            return parsed

    try:
        with urllib.request.urlopen(_GADM_URL, timeout=120) as resp:
            raw = resp.read()
        parsed = json.loads(raw.decode("utf-8"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not _is_feature_collection(parsed):
        return None

    try:
        _GEOJSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = _GEOJSON_PATH.with_suffix(_GEOJSON_PATH.suffix + ".tmp")
        tmp.write_bytes(raw)
        tmp.replace(_GEOJSON_PATH)
    except OSError:
        pass  # download succeeded; persisting the cache is best-effort

    _geojson_cache = parsed
    return parsed


def filter_by_district(df: pd.DataFrame, districts: list[str] | None) -> pd.DataFrame:
    if not districts:
        return df
    return df[df["District"].isin(districts)].reset_index(drop=True)


def filter_long_by(df: pd.DataFrame, districts: list[str] | None, genders: list[str] | None) -> pd.DataFrame:
    out = df
    if districts:
        out = out[out["District"].isin(districts)]
    if genders and "Gender" in out.columns:
        out = out[out["Gender"].isin(genders)]
    return out.reset_index(drop=True)
