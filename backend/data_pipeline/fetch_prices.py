"""
Price data fetcher for Prize2Plate.
Future real source: Department of Consumer Affairs (DCA) Price Monitoring System.
Currently returns clearly labeled DEMO/SAMPLE retail price data (INR/kg or INR/liter)
and nutrition profiles so the backend runs reliably offline.
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import PRICES_CSV_PATH
from utils.helpers import normalize_food_name, safe_float

# DEMO / SAMPLE DATA (Not real live government data)
# Includes Scenario A (Rice, Tomato, Tur Dal: price shock + supply/climate stress)
# and Scenario B (Wheat, Onion: price shock with normal supply and normal climate)
SAMPLE_PRICE_RECORDS: Dict[str, Dict[str, Any]] = {
    "Rice": {
        "name": "Rice",
        "category": "cereal",
        "unit": "kg",
        "current_price": 53.0,
        "historical_prices": [44.0, 44.5, 45.0, 44.5],
        "primary_location": "Chennai",
        "accessibility_score": 88.0,
        "nutrition": {
            "calories_kcal": 345,
            "protein_g": 6.8,
            "fiber_g": 1.2,
            "iron_mg": 0.8,
            "calcium_mg": 10,
            "nutrition_score": 68.0,
            "highlights": "Primary energy staple; moderate protein and low fiber",
        },
    },
    "Wheat": {
        "name": "Wheat",
        "category": "cereal",
        "unit": "kg",
        "current_price": 38.0,
        "historical_prices": [32.5, 33.0, 33.5, 33.0],
        "primary_location": "Bhopal",
        "accessibility_score": 86.0,
        "nutrition": {
            "calories_kcal": 341,
            "protein_g": 11.8,
            "fiber_g": 12.5,
            "iron_mg": 3.5,
            "calcium_mg": 41,
            "nutrition_score": 76.0,
            "highlights": "Whole grain staple with good dietary fiber and protein",
        },
    },
    "Potato": {
        "name": "Potato",
        "category": "vegetable",
        "unit": "kg",
        "current_price": 28.0,
        "historical_prices": [26.5, 27.0, 27.5, 27.0],
        "primary_location": "Lucknow",
        "accessibility_score": 92.0,
        "nutrition": {
            "calories_kcal": 97,
            "protein_g": 1.6,
            "fiber_g": 1.8,
            "iron_mg": 0.5,
            "calcium_mg": 10,
            "nutrition_score": 72.0,
            "highlights": "Energy-dense vegetable rich in potassium and vitamin C",
        },
    },
    "Onion": {
        "name": "Onion",
        "category": "vegetable",
        "unit": "kg",
        "current_price": 48.0,
        "historical_prices": [39.5, 40.0, 40.5, 40.0],
        "primary_location": "Pune",
        "accessibility_score": 90.0,
        "nutrition": {
            "calories_kcal": 50,
            "protein_g": 1.2,
            "fiber_g": 1.7,
            "iron_mg": 0.6,
            "calcium_mg": 47,
            "nutrition_score": 70.0,
            "highlights": "Essential culinary bulb with antioxidants and micronutrients",
        },
    },
    "Tomato": {
        "name": "Tomato",
        "category": "vegetable",
        "unit": "kg",
        "current_price": 64.0,
        "historical_prices": [41.0, 42.0, 43.0, 42.0],
        "primary_location": "Bengaluru",
        "accessibility_score": 85.0,
        "nutrition": {
            "calories_kcal": 20,
            "protein_g": 0.9,
            "fiber_g": 1.2,
            "iron_mg": 0.6,
            "calcium_mg": 12,
            "nutrition_score": 74.0,
            "highlights": "Rich in lycopene, vitamin C, and folate",
        },
    },
    "Tur Dal": {
        "name": "Tur Dal",
        "category": "pulse",
        "unit": "kg",
        "current_price": 148.0,
        "historical_prices": [118.0, 120.0, 122.0, 120.0],
        "primary_location": "Nagpur",
        "accessibility_score": 84.0,
        "nutrition": {
            "calories_kcal": 335,
            "protein_g": 22.3,
            "fiber_g": 15.0,
            "iron_mg": 2.7,
            "calcium_mg": 73,
            "nutrition_score": 85.0,
            "highlights": "High-protein pulse rich in folate and dietary fiber",
        },
    },
    "Moong Dal": {
        "name": "Moong Dal",
        "category": "pulse",
        "unit": "kg",
        "current_price": 96.0,
        "historical_prices": [93.0, 94.0, 95.0, 94.0],
        "primary_location": "Hyderabad",
        "accessibility_score": 86.0,
        "nutrition": {
            "calories_kcal": 348,
            "protein_g": 24.0,
            "fiber_g": 16.3,
            "iron_mg": 4.4,
            "calcium_mg": 124,
            "nutrition_score": 88.0,
            "highlights": "Easily digestible high-protein legume with strong iron content",
        },
    },
    "Ragi": {
        "name": "Ragi",
        "category": "cereal",
        "unit": "kg",
        "current_price": 32.0,
        "historical_prices": [31.0, 31.5, 32.0, 31.5],
        "primary_location": "Chennai",
        "accessibility_score": 85.0,
        "nutrition": {
            "calories_kcal": 328,
            "protein_g": 7.3,
            "fiber_g": 11.5,
            "iron_mg": 3.9,
            "calcium_mg": 344,
            "nutrition_score": 82.0,
            "highlights": "Climate-resilient finger millet rich in calcium, iron, and fiber",
        },
    },
    "Bajra": {
        "name": "Bajra",
        "category": "cereal",
        "unit": "kg",
        "current_price": 34.0,
        "historical_prices": [33.0, 33.5, 34.0, 33.5],
        "primary_location": "Delhi",
        "accessibility_score": 82.0,
        "nutrition": {
            "calories_kcal": 361,
            "protein_g": 11.6,
            "fiber_g": 11.4,
            "iron_mg": 8.0,
            "calcium_mg": 42,
            "nutrition_score": 80.0,
            "highlights": "Drought-tolerant pearl millet high in iron, zinc, and protein",
        },
    },
    "Jowar": {
        "name": "Jowar",
        "category": "cereal",
        "unit": "kg",
        "current_price": 36.0,
        "historical_prices": [34.5, 35.0, 35.5, 35.0],
        "primary_location": "Pune",
        "accessibility_score": 80.0,
        "nutrition": {
            "calories_kcal": 349,
            "protein_g": 10.4,
            "fiber_g": 9.7,
            "iron_mg": 4.1,
            "calcium_mg": 25,
            "nutrition_score": 79.0,
            "highlights": "Sorghum grain with rich complex carbohydrates and B-vitamins",
        },
    },
    "Milk": {
        "name": "Milk",
        "category": "dairy",
        "unit": "liter",
        "current_price": 56.0,
        "historical_prices": [53.5, 54.0, 54.5, 54.0],
        "primary_location": "Mumbai",
        "accessibility_score": 94.0,
        "nutrition": {
            "calories_kcal": 67,
            "protein_g": 3.2,
            "fiber_g": 0.0,
            "iron_mg": 0.2,
            "calcium_mg": 120,
            "nutrition_score": 84.0,
            "highlights": "Complete protein source rich in bioavailable calcium and B12",
        },
    },
    "Banana": {
        "name": "Banana",
        "category": "fruit",
        "unit": "kg",
        "current_price": 42.0,
        "historical_prices": [40.5, 41.0, 41.5, 41.0],
        "primary_location": "Kolkata",
        "accessibility_score": 91.0,
        "nutrition": {
            "calories_kcal": 89,
            "protein_g": 1.1,
            "fiber_g": 2.6,
            "iron_mg": 0.3,
            "calcium_mg": 17,
            "nutrition_score": 78.0,
            "highlights": "Year-round affordable fruit providing potassium and vitamin B6",
        },
    },
}


def load_prices_from_csv(csv_path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """
    Hook for loading Department of Consumer Affairs (DCA) retail price CSV files.
    Falls back to SAMPLE_PRICE_RECORDS when no CSV file is present.
    """
    target_path = csv_path or PRICES_CSV_PATH
    if not target_path or not target_path.exists():
        return SAMPLE_PRICE_RECORDS

    records: Dict[str, Dict[str, Any]] = {}
    with target_path.open(mode="r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = normalize_food_name(row.get("name"))
            if not name:
                continue
            base = SAMPLE_PRICE_RECORDS.get(name, {}).copy()
            base["name"] = name
            base["current_price"] = safe_float(
                row.get("current_price"), base.get("current_price", 0.0)
            )
            records[name] = base
    return records if records else SAMPLE_PRICE_RECORDS


def fetch_all_prices() -> List[Dict[str, Any]]:
    """Return price and nutrition records for all tracked foods."""
    source = load_prices_from_csv()
    return [dict(item) for item in source.values()]


def fetch_price_by_food(food_name: str) -> Optional[Dict[str, Any]]:
    """Return price and nutrition record for a single food (case-insensitive)."""
    normalized = normalize_food_name(food_name)
    source = load_prices_from_csv()
    record = source.get(normalized)
    return dict(record) if record else None
