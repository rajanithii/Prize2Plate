"""
Data cleaning and merging module for Prize2Plate.
Combines price, production, market arrival, and climate records into clean,
JSON-serializable Python dictionaries (avoiding raw Pandas objects in API responses).
"""

from typing import Any, Dict, List, Optional

from data_pipeline.fetch_availability import (
    fetch_all_availability,
    fetch_availability_by_food,
)
from data_pipeline.fetch_climate import fetch_all_climate, fetch_climate_by_location
from data_pipeline.fetch_prices import fetch_all_prices, fetch_price_by_food
from data_pipeline.fetch_production import (
    fetch_all_production,
    fetch_production_by_food,
)
from utils.helpers import normalize_food_name, normalize_location, safe_float

try:
    import pandas as pd  # type: ignore

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def clean_price_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure price record fields are clean, typed, and JSON-friendly."""
    raw_history = record.get("historical_prices") or []
    clean_history = [safe_float(p) for p in raw_history if safe_float(p) > 0]
    nutrition = dict(record.get("nutrition") or {})
    nutrition["nutrition_score"] = safe_float(nutrition.get("nutrition_score"), 70.0)

    return {
        "name": normalize_food_name(record.get("name")),
        "category": str(record.get("category", "general")),
        "unit": str(record.get("unit", "kg")),
        "current_price": safe_float(record.get("current_price")),
        "historical_prices": clean_history,
        "primary_location": normalize_location(
            record.get("primary_location", "Chennai")
        ),
        "accessibility_score": safe_float(record.get("accessibility_score"), 75.0),
        "nutrition": nutrition,
    }


def get_merged_food_dataset() -> List[Dict[str, Any]]:
    """
    Fetch and merge price, production, availability, and location climate data
    for all foods. Uses Pandas for tabular alignment when available, and always
    converts output to plain Python dicts/floats for JSON compatibility.
    """
    prices = [clean_price_record(item) for item in fetch_all_prices()]
    prod_map = {item["name"]: item for item in fetch_all_production()}
    avail_map = {item["name"]: item for item in fetch_all_availability()}
    climate_map = {item["location"]: item for item in fetch_all_climate()}

    merged: List[Dict[str, Any]] = []
    for item in prices:
        name = item["name"]
        prod = prod_map.get(name, {})
        avail = avail_map.get(name, {})
        loc = item.get("primary_location", "Chennai")
        climate = climate_map.get(loc, {})

        merged.append(
            {
                **item,
                "current_production": safe_float(prod.get("current_production")),
                "normal_production": safe_float(prod.get("normal_production")),
                "production_unit": str(prod.get("unit", "lakh tonnes")),
                "current_arrivals": safe_float(avail.get("current_arrivals")),
                "normal_arrivals": safe_float(avail.get("normal_arrivals")),
                "availability_score": safe_float(
                    avail.get("availability_score"), 75.0
                ),
                "arrivals_unit": str(avail.get("unit", "tonnes/day")),
                "rainfall": safe_float(climate.get("rainfall")),
                "normal_rainfall": safe_float(climate.get("normal_rainfall")),
            }
        )

    if HAS_PANDAS and merged:
        df = pd.DataFrame(merged)
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient="records")

    return merged


def get_clean_food_record(food_name: str) -> Optional[Dict[str, Any]]:
    """Return a single cleaned and merged food dictionary, or None if not found."""
    price_rec = fetch_price_by_food(food_name)
    if not price_rec:
        return None

    cleaned = clean_price_record(price_rec)
    name = cleaned["name"]
    prod = fetch_production_by_food(name) or {}
    avail = fetch_availability_by_food(name) or {}
    loc = cleaned.get("primary_location", "Chennai")
    climate = fetch_climate_by_location(loc) or {}

    return {
        **cleaned,
        "current_production": safe_float(prod.get("current_production")),
        "normal_production": safe_float(prod.get("normal_production")),
        "production_unit": str(prod.get("unit", "lakh tonnes")),
        "current_arrivals": safe_float(avail.get("current_arrivals")),
        "normal_arrivals": safe_float(avail.get("normal_arrivals")),
        "availability_score": safe_float(avail.get("availability_score"), 75.0),
        "arrivals_unit": str(avail.get("unit", "tonnes/day")),
        "rainfall": safe_float(climate.get("rainfall")),
        "normal_rainfall": safe_float(climate.get("normal_rainfall")),
    }


def get_clean_climate_record(location: str) -> Optional[Dict[str, Any]]:
    """Return a cleaned climate dictionary for a location, or None if not found."""
    raw = fetch_climate_by_location(location)
    if not raw:
        return None
    return {
        "location": normalize_location(raw.get("location")),
        "rainfall": safe_float(raw.get("rainfall")),
        "normal_rainfall": safe_float(raw.get("normal_rainfall")),
        "unit": str(raw.get("unit", "mm")),
    }
