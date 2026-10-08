"""
Supply Engine for Prize2Plate.
Evaluates crop production and mandi market arrivals to determine supply pressure
levels (low, medium, high) and combines signals into non-causal contributing factors.
"""

from typing import Any, Dict, List, Optional

from config import (
    ARRIVAL_DROP_HIGH,
    ARRIVAL_DROP_MODERATE,
    PRODUCTION_DROP_HIGH,
    PRODUCTION_DROP_MODERATE,
)
from utils.calculations import percentage_change
from utils.helpers import safe_float


def calculate_production_change(
    current_production: Optional[float],
    normal_production: Optional[float],
) -> float:
    """Calculate percentage change in crop production vs normal baseline."""
    return percentage_change(current_production, normal_production, decimals=1)


def calculate_arrival_change(
    current_arrivals: Optional[float],
    normal_arrivals: Optional[float],
) -> float:
    """Calculate percentage change in market (mandi) arrivals vs normal baseline."""
    return percentage_change(current_arrivals, normal_arrivals, decimals=1)


def classify_component_signal(
    change_percent: float,
    moderate_drop: float,
    high_drop: float,
) -> str:
    """Classify an individual supply metric into low, medium, or high pressure."""
    val = safe_float(change_percent, 0.0)
    if val <= high_drop:
        return "high"
    if val <= moderate_drop:
        return "medium"
    return "low"


def determine_supply_signal(
    production_change_percent: float,
    arrival_change_percent: float,
) -> str:
    """
    Combine production change and market arrival change into an overall
    supply pressure signal: 'low', 'medium', or 'high'.
    """
    prod_chg = safe_float(production_change_percent, 0.0)
    arr_chg = safe_float(arrival_change_percent, 0.0)

    if prod_chg <= PRODUCTION_DROP_HIGH and arr_chg <= ARRIVAL_DROP_MODERATE:
        return "high"
    if arr_chg <= ARRIVAL_DROP_HIGH and prod_chg <= PRODUCTION_DROP_MODERATE:
        return "high"
    if prod_chg <= PRODUCTION_DROP_HIGH or arr_chg <= ARRIVAL_DROP_HIGH:
        return "high"
    if prod_chg <= PRODUCTION_DROP_MODERATE or arr_chg <= ARRIVAL_DROP_MODERATE:
        return "medium"
    return "low"


def evaluate_food_supply(food_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate production and market arrival signals for a given food record.
    """
    curr_prod = safe_float(food_record.get("current_production"))
    norm_prod = safe_float(food_record.get("normal_production"))
    curr_arr = safe_float(food_record.get("current_arrivals"))
    norm_arr = safe_float(food_record.get("normal_arrivals"))

    prod_change = calculate_production_change(curr_prod, norm_prod)
    arr_change = calculate_arrival_change(curr_arr, norm_arr)

    prod_signal = classify_component_signal(
        prod_change, PRODUCTION_DROP_MODERATE, PRODUCTION_DROP_HIGH
    )
    arr_signal = classify_component_signal(
        arr_change, ARRIVAL_DROP_MODERATE, ARRIVAL_DROP_HIGH
    )
    overall_signal = determine_supply_signal(prod_change, arr_change)

    return {
        "current_production": curr_prod,
        "normal_production": norm_prod,
        "production_change_percent": prod_change,
        "production_signal": prod_signal,
        "current_arrivals": curr_arr,
        "normal_arrivals": norm_arr,
        "arrival_change_percent": arr_change,
        "market_arrival_signal": arr_signal,
        "supply_signal": overall_signal,
    }


def determine_possible_reasons(
    price_info: Dict[str, Any],
    supply_info: Dict[str, Any],
    climate_info: Dict[str, Any],
) -> List[str]:
    """
    Combine price, supply, and climate signals to generate responsible,
    non-causal possible contributing factors.
    Never claims that El Niño directly caused a specific price increase.
    """
    reasons: List[str] = []

    arr_change = safe_float(supply_info.get("arrival_change_percent"), 0.0)
    prod_change = safe_float(supply_info.get("production_change_percent"), 0.0)
    climate_status = climate_info.get("status", "normal")

    if arr_change <= ARRIVAL_DROP_MODERATE:
        reasons.append("Market arrivals are below the recent normal level")

    if prod_change <= PRODUCTION_DROP_MODERATE:
        reasons.append("Production pressure detected")

    if climate_status in ("below_normal", "above_normal"):
        reasons.append("Rainfall anomaly detected")

    if not reasons:
        if price_info.get("alert"):
            reasons.append(
                "No strong supply-side signal detected; other factors may be involved."
            )
        else:
            reasons.append(
                "Supply, market arrivals, and climate indicators are within normal ranges."
            )

    return reasons
