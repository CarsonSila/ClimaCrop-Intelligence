from __future__ import annotations
import numpy as np
import pandas as pd

from src.provenance import Provenance, SourcedValue


class RuleBasedSuitabilityEngine:
    WEIGHTS = {
        "rain_fit": 0.40,
        "temp_fit": 0.25,
        "dry_spell_fit": 0.20,
        "onset_fit": 0.15,
    }

    def __init__(self, crops_df: pd.DataFrame):
        self.crops_df = crops_df.copy()

    @staticmethod
    def _band_fit(value: float, lo: float, hi: float, shortfall_penalty: float = 1.3) -> float:
        if hi <= lo:
            return 0.5
        center = (lo + hi) / 2.0
        half_width = (hi - lo) / 2.0
        if value < lo:
            deficit = (lo - value) / half_width
            return float(np.clip(1.0 - deficit * shortfall_penalty, 0.0, 1.0))
        elif value > hi:
            excess = (value - hi) / half_width
            return float(np.clip(1.0 - excess, 0.0, 1.0))
        else:
            dist = abs(value - center) / half_width
            return float(np.clip(1.0 - 0.3 * dist, 0.0, 1.0))

    def score_crop(self, climate_profile: dict, crop_row: pd.Series) -> dict:
        rain_fit = self._band_fit(
            climate_profile["seasonal_rainfall_mm"],
            crop_row["min_rain_mm"], crop_row["max_rain_mm"],
            shortfall_penalty=1.3,
        )
        temp_fit = self._band_fit(
            climate_profile["temp_mean_c"],
            crop_row["min_temp_c"], crop_row["max_temp_c"],
            shortfall_penalty=1.0,
        )

        drought_tol = crop_row["drought_tolerance"] / 10.0
        dry_spell_days = climate_profile.get("max_dry_spell_days", 10)
        tolerance_threshold = 5 + drought_tol * 35
        dry_spell_fit = float(np.clip(1.0 - max(0, dry_spell_days - tolerance_threshold) / 20.0, 0.0, 1.0))

        onset_week = climate_profile.get("onset_week", 3)
        growth_days = crop_row.get("growth_days", 100)
        onset_sensitivity = 1.0 if growth_days < 100 else (0.5 if growth_days < 250 else 0.2)
        onset_fit = float(np.clip(1.0 - max(0, onset_week - 3) * 0.08 * onset_sensitivity, 0.0, 1.0))

        composite = (
            rain_fit * self.WEIGHTS["rain_fit"]
            + temp_fit * self.WEIGHTS["temp_fit"]
            + dry_spell_fit * self.WEIGHTS["dry_spell_fit"]
            + onset_fit * self.WEIGHTS["onset_fit"]
        )
        suitability_score = float(np.clip(composite * 100, 5.0, 98.0))

        return {
            "suitability_score": round(suitability_score, 1),
            "rain_fit": round(rain_fit, 3),
            "temp_fit": round(temp_fit, 3),
            "dry_spell_fit": round(dry_spell_fit, 3),
            "onset_fit": round(onset_fit, 3),
        }

    def recommend(self, climate_profile: dict, top_n: int = 5, category_filter: str = "All") -> pd.DataFrame:
        results = []
        for _, crop_row in self.crops_df.iterrows():
            if category_filter != "All" and crop_row["category"] != category_filter:
                continue

            scores = self.score_crop(climate_profile, crop_row)
            suitability_score = scores["suitability_score"]

            base_yield = crop_row["yield_per_acre_kg"]
            expected_yield_kg = round(base_yield * (0.55 + 0.45 * (suitability_score / 100.0)), 0)

            cost_acre = crop_row["cost_per_acre_kes"]
            base_price = crop_row["base_price_kes_per_kg"]
            expected_revenue_acre = round(expected_yield_kg * base_price, 0)
            net_profit_acre = round(expected_revenue_acre - cost_acre, 0)
            bcr = round(expected_revenue_acre / cost_acre, 2) if cost_acre > 0 else 1.0

            if suitability_score >= 78:
                risk_level = "Low"
            elif suitability_score >= 58:
                risk_level = "Moderate"
            else:
                risk_level = "High"

            results.append({
                "crop": crop_row["crop"],
                "category": crop_row["category"],
                "suitability_score": suitability_score,
                "risk_level": risk_level,
                "expected_yield_kg_per_acre": int(expected_yield_kg),
                "cost_per_acre_kes": int(cost_acre),
                "expected_revenue_kes": int(expected_revenue_acre),
                "net_profit_kes_per_acre": int(net_profit_acre),
                "benefit_cost_ratio": bcr,
                "drought_tolerance": int(crop_row["drought_tolerance"]),
                "growth_days": int(crop_row["growth_days"]),
                
                "score_breakdown": (
                    f"rain fit {scores['rain_fit']:.0%}, temp fit {scores['temp_fit']:.0%}, "
                    f"dry-spell tolerance {scores['dry_spell_fit']:.0%}, onset timing {scores['onset_fit']:.0%}"
                ),
            })

        df_res = pd.DataFrame(results).sort_values(
            by=["suitability_score", "net_profit_kes_per_acre"], ascending=[False, False]
        )
        return df_res.head(top_n)
