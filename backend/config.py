"""
Configuration settings for the Prize2Plate backend.
Simple, beginner-friendly constants and thresholds used across services.
"""

from pathlib import Path

# Project metadata
PROJECT_NAME = "Prize2Plate"
PROJECT_STATUS = "running"

# Base paths for future CSV / government dataset files
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data_sources"

PRICES_CSV_PATH = DATA_DIR / "dca_prices.csv"
PRODUCTION_CSV_PATH = DATA_DIR / "des_production.csv"
AVAILABILITY_CSV_PATH = DATA_DIR / "agmarknet_arrivals.csv"
CLIMATE_CSV_PATH = DATA_DIR / "imd_rainfall.csv"

# Price Engine Configuration
# Percentage increase over baseline required to trigger a price alert
PRICE_ALERT_THRESHOLD = 10.0

# Supply Engine Thresholds (percentage change vs normal)
PRODUCTION_DROP_MODERATE = -5.0
PRODUCTION_DROP_HIGH = -12.0
ARRIVAL_DROP_MODERATE = -8.0
ARRIVAL_DROP_HIGH = -15.0

# Climate Engine Thresholds (percentage rainfall deviation from normal)
# IMD standard defines +/- 19% as normal rainfall
RAINFALL_NORMAL_THRESHOLD = 19.0
RAINFALL_HIGH_SIGNAL_THRESHOLD = 40.0

# Alternative Engine Scoring Weights (must sum to 1.0)
ALTERNATIVE_WEIGHTS = {
    "price": 0.40,
    "nutrition": 0.30,
    "availability": 0.20,
    "accessibility": 0.10,
}

DEFAULT_ACCESSIBILITY_SCORE = 75.0
MAX_ALTERNATIVES = 3

# CORS Allowed Origins for local React development
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*",
]
