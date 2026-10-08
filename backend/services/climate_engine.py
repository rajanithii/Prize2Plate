"""
Climate Engine for Prize2Plate.
Calculates regional rainfall deviation from normal, classifies status
(normal, below_normal, above_normal) and signal intensity (low, medium, high),
and provides non-causal explanatory text.
"""

from typing import Any, Dict, Optional, Union

from config import RAINFALL_HIGH_SIGNAL_THRESHOLD, RAINFALL_NORMAL_THRESHOLD
from utils.calculations import percentage_change
from utils.helpers import safe_float

Number = Union[int, float]


def format_metric(value: float) -> Union[int, float]:
    """Return int if the float has no fractional part, else float."""
    rounded = round(float(value), 1)
    return int(rounded) if rounded.is_integer() else rounded


def calculate_rainfall_deviation(
    actual_rainfall: Optional[Number],
    normal_rainfall: Optional[Number],
) -> float:
    """
    Calculate percentage deviation of actual rainfall from normal:
    ((actual - normal) / normal) * 100
    Safely handles zero or missing normal rainfall.
    """
    return percentage_change(actual_rainfall, normal_rainfall, decimals=1)


def classify_rainfall_status(deviation_percent: Optional[Number]) -> str:
    """
    Classify rainfall status into 'normal', 'below_normal', or 'above_normal'.
    """
    dev = safe_float(deviation_percent, 0.0)
    if dev < -RAINFALL_NORMAL_THRESHOLD:
        return "below_normal"
    if dev > RAINFALL_NORMAL_THRESHOLD:
        return "above_normal"
    return "normal"


def classify_climate_signal(deviation_percent: Optional[Number]) -> str:
    """
    Produce a climate risk signal ('low', 'medium', 'high') based on
    absolute rainfall deviation.
    """
    abs_dev = abs(safe_float(deviation_percent, 0.0))
    if abs_dev <= RAINFALL_NORMAL_THRESHOLD:
        return "low"
    if abs_dev <= RAINFALL_HIGH_SIGNAL_THRESHOLD:
        return "medium"
    return "high"


def generate_climate_explanation(status: str, signal: str) -> str:
    """
    Generate responsible explanation of climate conditions without claiming direct causality.
    """
    if status == "below_normal":
        if signal == "high":
            return "Rainfall was significantly below normal, which may contribute to supply pressure."
        return "Rainfall was below normal, which may be a possible contributing factor to local supply pressure."
    if status == "above_normal":
        if signal == "high":
            return "Rainfall was significantly above normal, which may contribute to crop or transport disruption."
        return "Rainfall was above normal, which may affect harvesting or market movement."
    return "Rainfall was near normal levels; no strong climate anomaly detected."


def evaluate_location_climate(climate_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a climate record and return structured JSON-ready climate metrics.
    """
    actual = safe_float(climate_record.get("rainfall"), 0.0)
    normal = safe_float(climate_record.get("normal_rainfall"), 0.0)
    deviation = calculate_rainfall_deviation(actual, normal)
    status = classify_rainfall_status(deviation)
    signal = classify_climate_signal(deviation)
    explanation = generate_climate_explanation(status, signal)

    return {
        "location": climate_record.get("location", "Unknown"),
        "rainfall": format_metric(actual),
        "normal_rainfall": format_metric(normal),
        "deviation_percent": format_metric(deviation),
        "status": status,
        "signal": signal,
        "explanation": explanation,
    }
