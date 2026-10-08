"""
Climate API routes for Prize2Plate.
Provides:
- GET /climate/{location}
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from data_pipeline.clean_data import get_clean_climate_record
from services.climate_engine import evaluate_location_climate

router = APIRouter(prefix="/climate", tags=["Climate"])


@router.get("/{location}", response_model=Dict[str, Any])
def get_climate_by_location(location: str) -> Dict[str, Any]:
    """
    Return rainfall, normal_rainfall, deviation_percent, status, and signal
    for a given location.
    """
    record = get_clean_climate_record(location)
    if not record:
        raise HTTPException(status_code=404, detail="Location not found")

    evaluated = evaluate_location_climate(record)
    return {
        "location": evaluated["location"],
        "rainfall": evaluated["rainfall"],
        "normal_rainfall": evaluated["normal_rainfall"],
        "deviation_percent": evaluated["deviation_percent"],
        "status": evaluated["status"],
        "signal": evaluated["signal"],
    }
