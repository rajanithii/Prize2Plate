"""
Price Engine for Prize2Plate.
Calculates baseline (normal) prices, current prices, percentage increases,
and detects price shock alerts using thresholds from config.py.
"""

from typing import Any, Dict, List, Optional, Union

from config import PRICE_ALERT_THRESHOLD
from utils.calculations import average, percentage_change
from utils.helpers import safe_float

Number = Union[int, float]


def format_number(value: float) -> Union[int, float]:
    """Return int if the float has no fractional part (e.g., 53.0 -> 53), else float."""
    rounded = round(float(value), 2)
    return int(rounded) if rounded.is_integer() else rounded


def calculate_baseline_price(
    historical_prices: Optional[List[Number]],
    fallback_price: Number = 0.0,
) -> float:
    """
    Calculate baseline (normal) price from recent historical prices.
    Falls back safely if historical data is empty or invalid.
    """
    if historical_prices:
        avg_price = average(historical_prices, decimals=2)
        if avg_price > 0.0:
            return avg_price
    fallback = safe_float(fallback_price, 0.0)
    return round(fallback, 2) if fallback > 0.0 else 0.0


def get_current_price(price_value: Any) -> float:
    """Safely extract and validate a current price value."""
    val = safe_float(price_value, 0.0)
    return round(val, 2) if val > 0.0 else 0.0


def calculate_price_increase(
    current_price: Optional[Number],
    baseline_price: Optional[Number],
) -> float:
    """
    Calculate percentage price increase over baseline:
    ((current_price - baseline_price) / baseline_price) * 100
    """
    return percentage_change(current_price, baseline_price, decimals=1)


def detect_price_alert(
    increase_percent: Optional[Number],
    threshold: float = PRICE_ALERT_THRESHOLD,
) -> bool:
    """Return True if percentage price increase meets or exceeds the alert threshold."""
    inc = safe_float(increase_percent, 0.0)
    return bool(inc >= float(threshold))


def evaluate_food_price(food_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a food record and return structured price shock metrics.
    """
    current = get_current_price(food_record.get("current_price"))
    baseline = calculate_baseline_price(
        food_record.get("historical_prices"),
        fallback_price=food_record.get("normal_price", current),
    )
    increase_pct = calculate_price_increase(current, baseline)
    is_alert = detect_price_alert(increase_pct)

    return {
        "name": food_record.get("name", "Unknown"),
        "current_price": format_number(current),
        "normal_price": format_number(baseline),
        "increase_percent": format_number(increase_pct),
        "alert": is_alert,
    }
