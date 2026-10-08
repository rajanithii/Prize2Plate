"""
Foods API routes for Prize2Plate.
Provides:
- GET /foods
- GET /foods/{food_name}
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from data_pipeline.clean_data import (
    get_clean_climate_record,
    get_clean_food_record,
    get_merged_food_dataset,
)
from services.climate_engine import evaluate_location_climate
from services.price_engine import evaluate_food_price
from services.supply_engine import determine_possible_reasons, evaluate_food_supply

router = APIRouter(prefix="/foods", tags=["Foods"])


@router.get("", response_model=List[Dict[str, Any]])
def get_all_foods() -> List[Dict[str, Any]]:
    """
    Return summary food cards for all tracked foods containing:
    name, current_price, normal_price, increase_percent, and alert.
    """
    dataset = get_merged_food_dataset()
    return [evaluate_food_price(record) for record in dataset]


@router.get("/{food_name}", response_model=Dict[str, Any])
def get_food_details(food_name: str) -> Dict[str, Any]:
    """
    Return detailed information for a specific food, including price metrics,
    nutrition profile, production signal, market-arrival signal, climate signal,
    and responsible possible contributing factors.
    """
    record = get_clean_food_record(food_name)
    if not record:
        raise HTTPException(status_code=404, detail="Food not found")

    price_info = evaluate_food_price(record)
    supply_info = evaluate_food_supply(record)

    location = record.get("primary_location", "Chennai")
    climate_record = get_clean_climate_record(location) or {
        "location": location,
        "rainfall": record.get("rainfall", 0.0),
        "normal_rainfall": record.get("normal_rainfall", 0.0),
    }
    climate_info = evaluate_location_climate(climate_record)
    possible_factors = determine_possible_reasons(price_info, supply_info, climate_info)

    return {
        "name": price_info["name"],
        "category": record.get("category", "general"),
        "unit": record.get("unit", "kg"),
        "primary_location": location,
        "current_price": price_info["current_price"],
        "normal_price": price_info["normal_price"],
        "increase_percent": price_info["increase_percent"],
        "alert": price_info["alert"],
        "nutrition": record.get("nutrition", {}),
        "production_signal": supply_info["production_signal"],
        "production_change_percent": supply_info["production_change_percent"],
        "market_arrival_signal": supply_info["market_arrival_signal"],
        "arrival_change_percent": supply_info["arrival_change_percent"],
        "supply_signal": supply_info["supply_signal"],
        "climate_signal": climate_info["signal"],
        "climate_status": climate_info["status"],
        "rainfall_deviation_percent": climate_info["deviation_percent"],
        "possible_contributing_factors": possible_factors,
    }
