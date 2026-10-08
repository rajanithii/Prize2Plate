"""
String normalization and safe type conversion helpers for Prize2Plate.
"""

import math
from typing import Any, Optional


def normalize_food_name(name: Optional[str]) -> str:
    """Normalize a food name string (e.g., '  tur dal ' -> 'Tur Dal')."""
    if not name or not isinstance(name, str):
        return ""
    cleaned = " ".join(name.strip().split())
    return cleaned.title()


def normalize_location(location: Optional[str]) -> str:
    """Normalize a location/city name string (e.g., ' chennai ' -> 'Chennai')."""
    if not location or not isinstance(location, str):
        return ""
    cleaned = " ".join(location.strip().split())
    return cleaned.title()


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert a value to float safely, handling None, strings, and NaN."""
    if value is None:
        return default
    try:
        result = float(value)
        if math.isnan(result) or math.isinf(result):
            return default
        return result
    except (ValueError, TypeError):
        return default
