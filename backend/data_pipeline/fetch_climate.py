"""
Climate / rainfall data fetcher for Prize2Plate.
Future real source: India Meteorological Department (IMD) rainfall dataset.
Currently provides DEMO/SAMPLE regional rainfall measurements (in mm).
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import CLIMATE_CSV_PATH
from utils.helpers import normalize_location, safe_float

# DEMO / SAMPLE DATA (Not real live IMD data)
# Chennai: 42 mm actual vs 65 mm normal (-35.4% deviation -> below_normal, medium signal)
# Bhopal & Pune: Normal rainfall (used by Wheat & Onion to demonstrate non-climate price shocks)
SAMPLE_CLIMATE_RECORDS: Dict[str, Dict[str, Any]] = {
    "Chennai": {
        "location": "Chennai",
        "rainfall": 42.0,
        "normal_rainfall": 65.0,
        "unit": "mm",
    },
    "Bhopal": {
        "location": "Bhopal",
        "rainfall": 62.0,
        "normal_rainfall": 64.0,
        "unit": "mm",
    },
    "Pune": {
        "location": "Pune",
        "rainfall": 76.0,
        "normal_rainfall": 74.0,
        "unit": "mm",
    },
    "Bengaluru": {
        "location": "Bengaluru",
        "rainfall": 95.0,
        "normal_rainfall": 65.0,
        "unit": "mm",
    },
    "Nagpur": {
        "location": "Nagpur",
        "rainfall": 46.0,
        "normal_rainfall": 80.0,
        "unit": "mm",
    },
    "Hyderabad": {
        "location": "Hyderabad",
        "rainfall": 51.0,
        "normal_rainfall": 68.0,
        "unit": "mm",
    },
    "Delhi": {
        "location": "Delhi",
        "rainfall": 48.0,
        "normal_rainfall": 50.0,
        "unit": "mm",
    },
    "Mumbai": {
        "location": "Mumbai",
        "rainfall": 112.0,
        "normal_rainfall": 105.0,
        "unit": "mm",
    },
    "Kolkata": {
        "location": "Kolkata",
        "rainfall": 98.0,
        "normal_rainfall": 92.0,
        "unit": "mm",
    },
    "Lucknow": {
        "location": "Lucknow",
        "rainfall": 58.0,
        "normal_rainfall": 60.0,
        "unit": "mm",
    },
}


def load_climate_from_csv(csv_path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """
    Hook for loading IMD regional rainfall CSV files.
    Falls back to SAMPLE_CLIMATE_RECORDS when no CSV file is present.
    """
    target_path = csv_path or CLIMATE_CSV_PATH
    if not target_path or not target_path.exists():
        return SAMPLE_CLIMATE_RECORDS

    records: Dict[str, Dict[str, Any]] = {}
    with target_path.open(mode="r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            loc = normalize_location(row.get("location"))
            if not loc:
                continue
            records[loc] = {
                "location": loc,
                "rainfall": safe_float(row.get("rainfall")),
                "normal_rainfall": safe_float(row.get("normal_rainfall")),
                "unit": row.get("unit", "mm"),
            }
    return records if records else SAMPLE_CLIMATE_RECORDS


def fetch_all_climate() -> List[Dict[str, Any]]:
    """Return climate records for all tracked locations."""
    source = load_climate_from_csv()
    return [dict(item) for item in source.values()]


def fetch_climate_by_location(location: str) -> Optional[Dict[str, Any]]:
    """Return climate record for a single location (case-insensitive)."""
    normalized = normalize_location(location)
    source = load_climate_from_csv()
    record = source.get(normalized)
    return dict(record) if record else None
