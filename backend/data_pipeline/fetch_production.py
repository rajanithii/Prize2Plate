"""
Production data fetcher for Prize2Plate.
Future real source: Directorate of Economics and Statistics (DES) Agriculture Data Portal.
Currently provides DEMO/SAMPLE crop production indices/tonnage (in lakh tonnes).
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import PRODUCTION_CSV_PATH
from utils.helpers import normalize_food_name, safe_float

# DEMO / SAMPLE DATA (Not real live government data)
# Scenario A foods (Rice, Tomato, Tur Dal) show lower production vs normal.
# Scenario B foods (Wheat, Onion) show normal production despite higher prices.
SAMPLE_PRODUCTION_RECORDS: Dict[str, Dict[str, Any]] = {
    "Rice": {
        "name": "Rice",
        "current_production": 104.0,
        "normal_production": 122.0,
        "unit": "lakh tonnes",
    },
    "Wheat": {
        "name": "Wheat",
        "current_production": 111.6,
        "normal_production": 110.0,
        "unit": "lakh tonnes",
    },
    "Potato": {
        "name": "Potato",
        "current_production": 54.5,
        "normal_production": 53.5,
        "unit": "lakh tonnes",
    },
    "Onion": {
        "name": "Onion",
        "current_production": 31.2,
        "normal_production": 31.0,
        "unit": "lakh tonnes",
    },
    "Tomato": {
        "name": "Tomato",
        "current_production": 16.4,
        "normal_production": 20.0,
        "unit": "lakh tonnes",
    },
    "Tur Dal": {
        "name": "Tur Dal",
        "current_production": 34.0,
        "normal_production": 42.0,
        "unit": "lakh tonnes",
    },
    "Moong Dal": {
        "name": "Moong Dal",
        "current_production": 31.8,
        "normal_production": 31.0,
        "unit": "lakh tonnes",
    },
    "Ragi": {
        "name": "Ragi",
        "current_production": 19.8,
        "normal_production": 19.0,
        "unit": "lakh tonnes",
    },
    "Bajra": {
        "name": "Bajra",
        "current_production": 98.0,
        "normal_production": 96.0,
        "unit": "lakh tonnes",
    },
    "Jowar": {
        "name": "Jowar",
        "current_production": 48.5,
        "normal_production": 47.5,
        "unit": "lakh tonnes",
    },
    "Milk": {
        "name": "Milk",
        "current_production": 230.0,
        "normal_production": 226.0,
        "unit": "million tonnes",
    },
    "Banana": {
        "name": "Banana",
        "current_production": 35.8,
        "normal_production": 35.0,
        "unit": "lakh tonnes",
    },
}


def load_production_from_csv(csv_path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """
    Hook for loading DES Agriculture Data Portal production CSV files.
    Falls back to SAMPLE_PRODUCTION_RECORDS when no CSV file is present.
    """
    target_path = csv_path or PRODUCTION_CSV_PATH
    if not target_path or not target_path.exists():
        return SAMPLE_PRODUCTION_RECORDS

    records: Dict[str, Dict[str, Any]] = {}
    with target_path.open(mode="r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = normalize_food_name(row.get("name"))
            if not name:
                continue
            records[name] = {
                "name": name,
                "current_production": safe_float(row.get("current_production")),
                "normal_production": safe_float(row.get("normal_production")),
                "unit": row.get("unit", "lakh tonnes"),
            }
    return records if records else SAMPLE_PRODUCTION_RECORDS


def fetch_all_production() -> List[Dict[str, Any]]:
    """Return production records for all tracked foods."""
    source = load_production_from_csv()
    return [dict(item) for item in source.values()]


def fetch_production_by_food(food_name: str) -> Optional[Dict[str, Any]]:
    """Return production record for a single food (case-insensitive)."""
    normalized = normalize_food_name(food_name)
    source = load_production_from_csv()
    record = source.get(normalized)
    return dict(record) if record else None
