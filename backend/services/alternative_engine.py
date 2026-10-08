"""
Alternative Recommendation Engine for Prize2Plate.
Recommends 1-3 affordable, nutritious, and available alternatives when a food
experiences a price shock or when users look for a Better Plate option.

Weights (from config.py):
- Price: 40%
- Nutrition: 30%
- Availability: 20%
- Accessibility: 10%
"""

from typing import Any, Dict, List, Optional, Union

from config import (
    ALTERNATIVE_WEIGHTS,
    DEFAULT_ACCESSIBILITY_SCORE,
    MAX_ALTERNATIVES,
)
from services.price_engine import evaluate_food_price
from utils.helpers import normalize_food_name, safe_float


def format_num(value: float) -> Union[int, float]:
    """Return int if whole number, else rounded float."""
    rounded = round(float(value), 1)
    return int(rounded) if rounded.is_integer() else rounded


def calculate_price_affordability_score(
    candidate_price: float,
    reference_price: float,
) -> float:
    """
    Calculate an explainable 0-100 affordability score.
    A candidate at the same price as the reference food gets 50.
    Candidates cheaper than the reference food score higher (up to 100).
    """
    cand = safe_float(candidate_price, 0.0)
    ref = safe_float(reference_price, 0.0)
    if cand <= 0.0:
        return 0.0
    if ref <= 0.0:
        return max(0.0, min(100.0, 100.0 - cand))

    savings_ratio = (ref - cand) / ref
    raw_score = 50.0 + (savings_ratio * 100.0)
    return max(0.0, min(100.0, raw_score))


def build_alternative_reason(
    candidate_price: float,
    target_price: float,
    nutrition_score: float,
    availability_score: float,
) -> str:
    """Generate a human-readable explanation for why this alternative was recommended."""
    traits: List[str] = []
    if candidate_price < target_price:
        traits.append("Lower price")
    else:
        traits.append("Stable price")

    if nutrition_score >= 80:
        traits.append("strong nutrition")
    elif nutrition_score >= 70:
        traits.append("good nutritional profile")

    if availability_score >= 85:
        traits.append("good availability")
    elif availability_score >= 75:
        traits.append("steady market availability")

    if len(traits) >= 3:
        return f"{traits[0]} with {traits[1]} and {traits[2]}"
    if len(traits) == 2:
        return f"{traits[0]} with {traits[1]}"
    return traits[0] if traits else "Balanced affordability, nutrition, and availability"


def score_candidate_alternative(
    candidate: Dict[str, Any],
    target_food: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Score a single candidate food against the target food using weighted criteria:
    Price (40%), Nutrition (30%), Availability (20%), Accessibility (10%).
    """
    active_weights = weights or ALTERNATIVE_WEIGHTS

    target_price = safe_float(target_food.get("current_price"), 50.0)
    cand_price = safe_float(candidate.get("current_price"), 50.0)

    nutrition_data = candidate.get("nutrition") or {}
    nutrition_score = safe_float(nutrition_data.get("nutrition_score"), 70.0)
    availability_score = safe_float(candidate.get("availability_score"), 75.0)
    accessibility_score = safe_float(
        candidate.get("accessibility_score"), DEFAULT_ACCESSIBILITY_SCORE
    )

    price_score = calculate_price_affordability_score(cand_price, target_price)

    weighted_total = (
        price_score * active_weights.get("price", 0.40)
        + nutrition_score * active_weights.get("nutrition", 0.30)
        + availability_score * active_weights.get("availability", 0.20)
        + accessibility_score * active_weights.get("accessibility", 0.10)
    )

    final_score = int(round(weighted_total))
    reason = build_alternative_reason(
        cand_price, target_price, nutrition_score, availability_score
    )

    return {
        "name": candidate.get("name", "Unknown"),
        "score": final_score,
        "price": format_num(cand_price),
        "nutrition_score": format_num(nutrition_score),
        "availability_score": format_num(availability_score),
        "reason": reason,
    }


def recommend_alternatives(
    target_food: Dict[str, Any],
    all_foods: List[Dict[str, Any]],
    limit: int = MAX_ALTERNATIVES,
) -> List[Dict[str, Any]]:
    """
    Return the top 1-3 recommended alternatives for a target food.
    Prefers non-alert foods in the same or complementary staple category
    that balance affordability, nutrition, and market availability.
    """
    target_name = normalize_food_name(target_food.get("name"))
    target_category = target_food.get("category", "")
    target_price = safe_float(target_food.get("current_price"), 0.0)

    same_category_candidates: List[Dict[str, Any]] = []
    other_candidates: List[Dict[str, Any]] = []

    for food in all_foods:
        cand_name = normalize_food_name(food.get("name"))
        if not cand_name or cand_name == target_name:
            continue

        price_eval = evaluate_food_price(food)
        cand_price = safe_float(food.get("current_price"), 0.0)

        # Skip candidates currently experiencing a price shock if stable options exist
        is_shocked = price_eval.get("alert", False)
        if is_shocked:
            continue

        if food.get("category") == target_category and cand_price <= target_price * 1.15:
            same_category_candidates.append(food)
        elif cand_price <= target_price * 1.15:
            other_candidates.append(food)

    # Fallback if target food is already very cheap
    if not same_category_candidates and not other_candidates:
        for food in all_foods:
            if normalize_food_name(food.get("name")) != target_name:
                if not evaluate_food_price(food).get("alert", False):
                    other_candidates.append(food)

    scored_same = [
        score_candidate_alternative(cand, target_food)
        for cand in same_category_candidates
    ]
    scored_same.sort(key=lambda item: item["score"], reverse=True)

    scored_other = [
        score_candidate_alternative(cand, target_food) for cand in other_candidates
    ]
    scored_other.sort(key=lambda item: item["score"], reverse=True)

    combined = scored_same + scored_other
    max_items = max(1, min(int(limit), MAX_ALTERNATIVES))
    return combined[:max_items]
