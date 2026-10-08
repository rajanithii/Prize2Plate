"""
Reusable mathematical calculations for Prize2Plate.
Handles zero, None, and invalid inputs safely without raising ZeroDivisionError.
"""

from typing import Iterable, Optional, Union

Number = Union[int, float]


def safe_divide(
    numerator: Optional[Number],
    denominator: Optional[Number],
    default: float = 0.0,
) -> float:
    """Safely divide two numbers, returning default if denominator is zero or invalid."""
    try:
        if numerator is None or denominator is None:
            return default
        num = float(numerator)
        den = float(denominator)
        if den == 0.0:
            return default
        return num / den
    except (ValueError, TypeError, ZeroDivisionError):
        return default


def percentage_change(
    current: Optional[Number],
    baseline: Optional[Number],
    decimals: int = 1,
) -> float:
    """
    Calculate percentage change: ((current - baseline) / baseline) * 100.
    Returns 0.0 if baseline is zero, negative, or missing.
    """
    try:
        if current is None or baseline is None:
            return 0.0
        curr_val = float(current)
        base_val = float(baseline)
        if base_val <= 0.0:
            return 0.0
        change = ((curr_val - base_val) / base_val) * 100.0
        return round(change, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def average(values: Optional[Iterable[Optional[Number]]], decimals: int = 2) -> float:
    """Calculate the arithmetic mean of valid numeric values in an iterable."""
    if not values:
        return 0.0
    valid_numbers = []
    for item in values:
        if item is None:
            continue
        try:
            valid_numbers.append(float(item))
        except (ValueError, TypeError):
            continue
    if not valid_numbers:
        return 0.0
    return round(sum(valid_numbers) / len(valid_numbers), decimals)


def normalize_score(
    value: Optional[Number],
    min_val: float = 0.0,
    max_val: float = 100.0,
    invert: bool = False,
    decimals: int = 1,
) -> float:
    """
    Normalize a numeric value to a 0-100 scale and clamp within [0, 100].
    If invert is True, lower raw values yield higher normalized scores.
    """
    try:
        if value is None:
            return 0.0
        val = float(value)
        if max_val <= min_val:
            return 0.0
        clamped = max(min_val, min(max_val, val))
        ratio = (clamped - min_val) / (max_val - min_val)
        if invert:
            ratio = 1.0 - ratio
        return round(ratio * 100.0, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0
