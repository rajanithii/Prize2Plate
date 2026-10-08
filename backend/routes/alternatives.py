"""
Alternatives API routes for Prize2Plate.
Provides:
- GET /alternatives/{food_name}
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from data_pipeline.clean_data import get_clean_food_record, get_merged_food_dataset
from services.alternative_engine import recommend_alternatives

router = APIRouter(prefix="/alternatives", tags=["Alternatives"])


@router.get("/{food_name}", response_model=Dict[str, Any])
def get_food_alternatives(food_name: str) -> Dict[str, Any]:
    """
    Return the top 1-3 affordable, nutritious, and available alternatives
    for a requested food.
    """
    target_record = get_clean_food_record(food_name)
    if not target_record:
        raise HTTPException(status_code=404, detail="Food not found")

    all_foods = get_merged_food_dataset()
    recommendations = recommend_alternatives(target_record, all_foods)

    return {
        "food": target_record["name"],
        "alternatives": recommendations,
    }
