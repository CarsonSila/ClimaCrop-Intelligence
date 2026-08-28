"""
Dedicated training and persistence script for ML models.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
import joblib
import pandas as pd

from src.ml_models import ClimatePatternEngine, CropSuitabilityEngine, MarketArbitrageEngine


def main():
    os.makedirs("models", exist_ok=True)
    
    climate_df = pd.read_csv("data/county_climate_historical.csv")
    crops_df = pd.read_csv("data/crops_database.csv")
    market_df = pd.read_csv("data/market_prices.csv")
    
    print("1. Training Climate Pattern Engine (K-Means)...")
    climate_engine = ClimatePatternEngine()
    climate_engine.fit(climate_df)
    joblib.dump(climate_engine, "models/climate_pattern_engine.joblib")
    
    print("2. Training 40-Crop Suitability Engine (Random Forest)...")
    crop_engine = CropSuitabilityEngine()
    crop_engine.fit(crops_df)
    joblib.dump(crop_engine, "models/crop_suitability_engine.joblib")
    
    print("3. Fitting Market Arbitrage Engine...")
    market_engine = MarketArbitrageEngine()
    market_engine.fit(market_df)
    joblib.dump(market_engine, "models/market_arbitrage_engine.joblib")
    
    print("All Models successfully trained and saved into models/ directory!")


if __name__ == "__main__":
    main()

