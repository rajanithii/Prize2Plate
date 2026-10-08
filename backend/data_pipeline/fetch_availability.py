"""
Market availability / arrivals data fetcher for Prize2Plate.
Future real source: AGMARKNET (Agricultural Marketing Information Network) mandi arrivals.
Currently provides DEMO/SAMPLE mandi arrival volumes (tonnes/day) and availability scores.
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import AVAILABILITY_CSV_PATH
from utils.helpers import normalize_food_name, safe_float

# DEMO / SAMPLE DATA (Not real live government data)
# Scenario A foods (Rice, Tomato, Tur Dal) show reduced mandi arrivals.
# Scenario B foods (Wheat, Onion) show normal mandi arrivals.
SAMPLE_AVAILABILITY_RECORDS: Dict[str, Dict[str, Any]] = {
    "Rice": {
        "name": "Rice",
        "current_arrivals": 780.0,
        "normal_arrivals": 980.0,
        "availability_score": 58.0,
        "unit": "tonnes/day",
    },
    "Wheat": {
        "name": "Wheat",
        "current_arrivals": 910.0,
        "normal_arrivals": 900.0,
        "availability_score": 85.0,
        "unit": "tonnes/day",
    },
    "Potato": {
        "name": "Potato",
        "current_arrivals": 1150.0,
        "normal_arrivals": 1120.0,
        "availability_score": 89.0,
        "unit": "tonnes/day",
    },
    "Onion": {
        "name": "Onion",
        "current_arrivals": 850.0,
        "normal_arrivals": 840.0,
        "availability_score": 84.0,
        "unit": "tonnes/day",
    },
    "Tomato": {
        "name": "Tomato",
        "current_arrivals": 540.0,
        "normal_arrivals": 820.0,
        "availability_score": 48.0,
        "unit": "tonnes/day",
    },
    "Tur Dal": {
        "name": "Tur Dal",
        "current_arrivals": 410.0,
        "normal_arrivals": 530.0,
        "availability_score": 55.0,
        "unit": "tonnes/day",
    },
    "Moong Dal": {
        "name": "Moong Dal",
        "current_arrivals": 640.0,
        "normal_arrivals": 620.0,
        "availability_score": 88.0,
        "unit": "tonnes/day",
    },
    "Ragi": {
        "name": "Ragi",
        "current_arrivals": 520.0,
        "normal_arrivals": 500.0,
        "availability_score": 90.0,
        "unit": "tonnes/day",
    },
    "Bajra": {
        "name": "Bajra",
        "current_arrivals": 610.0,
        "normal_arrivals": 595.0,
        "availability_score": 86.0,
        "unit": "tonnes/day",
    },
    "Jowar": {
        "name": "Jowar",
        "current_arrivals": 560.0,
        "normal_arrivals": 550.0,
        "availability_score": 85.0,
        "unit": "tonnes/day",
    },
    "Milk": {
        "name": "Milk",
        "current_arrivals": 1450.0,
        "normal_arrivals": 1420.0,
        "availability_score": 92.0,
        "unit": "kiloliters/day",
    },
    "Banana": {
        "name": "Banana",
        "current_arrivals": 920.0,
        "normal_arrivals": 900.0,
        "availability_score": 91.0,
        "unit": "tonnes/day",
    },
}


def load_availability_from_csv(
    csv_path: Optional[Path] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Hook for loading AGMARKNET mandi arrival CSV files.
    Falls back to SAMPLE_AVAILABILITY_RECORDS when no CSV file is present.
    """
    target_path = csv_path or AVAILABILITY_CSV_PATH
    if not target_path or not target_path.exists():
        return SAMPLE_AVAILABILITY_RECORDS

    records: Dict[str, Dict[str, Any]] = {}
    with target_path.open(mode="r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = normalize_food_name(row.get("name"))
            if not name:
                continue
            records[name] = {
                "name": name,
                "current_arrivals": safe_float(row.get("current_arrivals")),
                "normal_arrivals": safe_float(row.get("normal_arrivals")),
                "availability_score": safe_float(row.get("availability_score"), 75.0),
                "unit": row.get("unit", "tonnes/day"),
            }
    return records if records else SAMPLE_AVAILABILITY_RECORDS


def fetch_all_availability() -> List[Dict[str, Any]]:
    """Return market arrival and availability records for all tracked foods."""
    source = load_availability_from_csv()
    return [dict(item) for item in source.values()]


def fetch_availability_by_food(food_name: str) -> Optional[Dict[str, Any]]:
    """Return market arrival record for a single food (case-insensitive)."""
    normalized = normalize_food_name(food_name)
    source = load_availability_from_csv()
    record = source.get(normalized)
    return dict(record) if record else None
