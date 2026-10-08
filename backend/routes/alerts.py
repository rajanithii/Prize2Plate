"""
Alerts API routes for Prize2Plate.
Provides:
- GET /alerts
- GET /alerts/{food_name}
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

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def build_alert_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    """Build structured alert evaluation payload for a single food record."""
    price_info = evaluate_food_price(record)
    supply_info = evaluate_food_supply(record)

    location = record.get("primary_location", "Chennai")
    climate_record = get_clean_climate_record(location) or {
        "location": location,
        "rainfall": record.get("rainfall", 0.0),
        "normal_rainfall": record.get("normal_rainfall", 0.0),
    }
    climate_info = evaluate_location_climate(climate_record)
    reasons = determine_possible_reasons(price_info, supply_info, climate_info)

    return {
        "food": price_info["name"],
        "current_price": price_info["current_price"],
        "normal_price": price_info["normal_price"],
        "increase_percent": price_info["increase_percent"],
        "alert": price_info["alert"],
        "supply_signal": supply_info["supply_signal"],
        "possible_reasons": reasons,
    }


@router.get("", response_model=List[Dict[str, Any]])
def get_active_alerts() -> List[Dict[str, Any]]:
    """Return only foods currently experiencing price alerts."""
    dataset = get_merged_food_dataset()
    active_alerts: List[Dict[str, Any]] = []
    for record in dataset:
        payload = build_alert_payload(record)
        if payload["alert"]:
            active_alerts.append(payload)
    return active_alerts


@router.get("/{food_name}", response_model=Dict[str, Any])
def get_food_alert(food_name: str) -> Dict[str, Any]:
    """Return detailed alert information and possible contributing reasons for a food."""
    record = get_clean_food_record(food_name)
    if not record:
        raise HTTPException(status_code=404, detail="Food not found")

    return build_alert_payload(record)
