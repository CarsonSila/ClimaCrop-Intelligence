import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
import joblib
import numpy as np
import pandas as pd

from src.ml_models import ClimatePatternEngine, CropSuitabilityEngine, MarketArbitrageEngine
from src.rule_based_suitability import RuleBasedSuitabilityEngine
from src.provenance import Provenance, SourcedValue, ProvenanceReport


if "__main__" in sys.modules:
    setattr(sys.modules["__main__"], "ClimatePatternEngine", ClimatePatternEngine)
    setattr(sys.modules["__main__"], "CropSuitabilityEngine", CropSuitabilityEngine)
    setattr(sys.modules["__main__"], "MarketArbitrageEngine", MarketArbitrageEngine)


class FinancialDecisionEngine:
    def __init__(self, models_dir="models", data_dir="data", suitability_mode="rule_based"):
        """
        suitability_mode:
          "rule_based" (default) - transparent, documented scoring, no
            circular synthetic-data ML. Recommended until real yield-outcome
            training data exists.
          "ml_legacy" - the original Random Forest, trained on synthetic
            samples generated from the same thresholds it's scored against.
            Kept available for comparison/audit purposes only — NOT
            recommended for real decisions. Every output using this mode is
            tagged Provenance.MODELED with a note explaining the caveat.
        """
        self.models_dir = models_dir
        self.data_dir = data_dir
        self.suitability_mode = suitability_mode
        self.climate_engine = None
        self.crop_engine = None
        self.rule_engine = None
        self.market_engine = None
        self.climate_df = None
        self.crops_df = None
        self.market_df = None
        self._load_resources()

    def _load_resources(self):
        climate_eng_path = os.path.join(self.models_dir, "climate_pattern_engine.joblib")
        crop_eng_path = os.path.join(self.models_dir, "crop_suitability_engine.joblib")
        market_eng_path = os.path.join(self.models_dir, "market_arbitrage_engine.joblib")

        if os.path.exists(climate_eng_path):
            self.climate_engine = joblib.load(climate_eng_path)
        if os.path.exists(crop_eng_path):
            self.crop_engine = joblib.load(crop_eng_path)
        if os.path.exists(market_eng_path):
            self.market_engine = joblib.load(market_eng_path)

        climate_data_path = os.path.join(self.data_dir, "county_climate_historical.csv")
        crops_data_path = os.path.join(self.data_dir, "crops_database.csv")
        market_data_path = os.path.join(self.data_dir, "market_prices.csv")

        if os.path.exists(climate_data_path):
            self.climate_df = pd.read_csv(climate_data_path)
        if os.path.exists(crops_data_path):
            self.crops_df = pd.read_csv(crops_data_path)
            if self.suitability_mode == "rule_based":
                self.rule_engine = RuleBasedSuitabilityEngine(self.crops_df)
        if os.path.exists(market_data_path):
            self.market_df = pd.read_csv(market_data_path)

    def _crops_data_provenance(self) -> SourcedValue:
        """crops_database.csv currently carries hand-authored placeholder
        economics (see its 'source'/'confidence' columns) pending real
        KALRO/FAO citations. Surface that honestly rather than implying the
        figures are verified."""
        if self.crops_df is not None and "confidence" in self.crops_df.columns:
            if (self.crops_df["confidence"] == "assumed").all():
                return SourcedValue(
                    value="crop economics (cost/yield/price)",
                    provenance=Provenance.ASSUMED,
                    note="crops_database.csv is hand-authored placeholder data, not yet cited to KALRO/FAO/AMIS sources.",
                )
        return SourcedValue(
            value="crop economics (cost/yield/price)",
            provenance=Provenance.OFFICIAL,
            note="Sourced per crops_database.csv 'source' column.",
        )

    def get_county_climate_profile(self, county="Nakuru", season="Long Rains (MAM)"):
        """Retrieves county's climate statistics and forecasted conditions."""
        if self.climate_df is None or self.climate_df.empty:
            return {
                "county": county,
                "season": season,
                "seasonal_rainfall_mm": 520.0,
                "temp_mean_c": 19.5,
                "temp_max_c": 25.0,
                "temp_min_c": 14.0,
                "max_dry_spell_days": 12,
                "onset_week": 3,
                "elevation_m": 1850,
                "drought_risk_index": 0.28,
                "cluster_id": 0,
                "cluster_name": "Normal / Favourable Season"
            }

        county_subset = self.climate_df[(self.climate_df["county"] == county) & (self.climate_df["season"] == season)]
        if county_subset.empty:
            county_subset = self.climate_df[self.climate_df["season"] == season]

        recent = county_subset.tail(3)
        profile = {
            "county": county,
            "season": season,
            "seasonal_rainfall_mm": round(float(recent["seasonal_rainfall_mm"].mean()), 1),
            "temp_mean_c": round(float(recent["temp_mean_c"].mean()), 1),
            "temp_max_c": round(float(recent["temp_max_c"].max()), 1),
            "temp_min_c": round(float(recent["temp_min_c"].min()), 1),
            "max_dry_spell_days": int(recent["max_dry_spell_days"].mean()),
            "onset_week": int(recent["onset_week"].median()),
            "elevation_m": round(float(recent["elevation_m"].mean()), 0),
            "drought_risk_index": round(float(recent["drought_risk_index"].mean()), 3),
        }

        if self.climate_engine:
            temp_df = pd.DataFrame([profile])
            c_ids, c_names = self.climate_engine.predict(temp_df)
            profile["cluster_id"] = int(c_ids[0])
            profile["cluster_name"] = c_names[0]
        else:
            profile["cluster_id"] = 0
            profile["cluster_name"] = "Normal Season"

        return profile

    def get_cooperative_recommendations(self, county="Nakuru", season="Long Rains (MAM)", farm_size_acres=2.0, category_filter="All", top_n=5, use_rule_based=None):
        """
        Provides complete decision support for agricultural cooperatives:
        - Optimal crop selection for the season
        - Yield & Profit per acre and total farm returns
        - Destination market arbitrage opportunities
        """
        profile = self.get_county_climate_profile(county, season)

        is_rule_mode = (self.suitability_mode == "rule_based") if use_rule_based is None else bool(use_rule_based)
        if is_rule_mode:
            if self.rule_engine is None:
                return pd.DataFrame(), profile, {}
            recs = self.rule_engine.recommend(profile, top_n=top_n, category_filter=category_filter)
            suitability_provenance = SourcedValue(
                value="suitability_score",
                provenance=Provenance.ESTIMATED,
                note="Transparent rule-based fit score (rain/temp band fit, drought & onset tolerance). See RuleBasedSuitabilityEngine docstring for the exact formula.",
            )
        else:
            if self.crop_engine is None:
                # Fallback to rule engine if ML model not loaded
                if self.rule_engine is not None:
                    recs = self.rule_engine.recommend(profile, top_n=top_n, category_filter=category_filter)
                else:
                    return pd.DataFrame(), profile, {}
            else:
                recs = self.crop_engine.recommend(profile, top_n=top_n, category_filter=category_filter)
            suitability_provenance = SourcedValue(
                value="suitability_score",
                provenance=Provenance.MODELED,
                note="Random Forest trained on multi-class crop thresholds — probabilistic ML recommendation.",
            )

        climate_provenance = SourcedValue(
            value="climate_profile",
            provenance=Provenance.ESTIMATED,
            note="Rainfall aggregated from TAHMO-derived daily records; temperature is a modeled elevation/seasonal estimate, not a direct station measurement — see data_processing.py.",
        )

    
        enriched_recs = []
        for _, crop_row in recs.iterrows():
            crop_name = crop_row["crop"]
            cost_per_acre = crop_row["cost_per_acre_kes"]
            yield_per_acre = crop_row["expected_yield_kg_per_acre"]
            
            total_farm_cost = cost_per_acre * farm_size_acres
            total_farm_yield_kg = yield_per_acre * farm_size_acres
            
            
            best_market = "Local Farm Gate"
            best_net_price = crop_row["expected_revenue_kes"] / max(1, yield_per_acre)
            extra_arbitrage_gain = 0.0
            
            if self.market_engine:
                market_opps = self.market_engine.get_market_opportunities(crop_name, origin_county=county)
                if not market_opps.empty:
                    top_market = market_opps.iloc[0]
                    best_market = top_market["market"]
                    best_net_price = top_market["net_market_price_kes"]
                    extra_arbitrage_gain = max(0.0, top_market["arbitrage_margin_vs_base"] * total_farm_yield_kg)

            total_farm_revenue = round(total_farm_yield_kg * best_net_price, 0)
            total_farm_net_profit = round(total_farm_revenue - total_farm_cost, 0)

            rec_dict = crop_row.to_dict()
            rec_dict.update({
                "farm_size_acres": farm_size_acres,
                "total_production_cost_kes": int(total_farm_cost),
                "total_farm_yield_kg": int(total_farm_yield_kg),
                "best_target_market": best_market,
                "optimized_net_price_kes_per_kg": round(best_net_price, 1),
                "total_farm_revenue_kes": int(total_farm_revenue),
                "total_farm_net_profit_kes": int(total_farm_net_profit),
                "arbitrage_added_value_kes": int(extra_arbitrage_gain),
            })
            enriched_recs.append(rec_dict)

        report = ProvenanceReport()
        report.add("climate_profile", climate_provenance)
        report.add("suitability_score", suitability_provenance)
        report.add("crop_economics", self._crops_data_provenance())
        report.add("market_prices", SourcedValue(
            value="market_prices.csv",
            provenance=Provenance.ASSUMED,
            note="Synthetically generated multipliers + random volatility, not real AMIS/KACE price data. See src/data_sources/market_prices_ingest.py to load a real snapshot instead.",
        ))

        return pd.DataFrame(enriched_recs), profile, report.to_dict()

   
    def underwrite_agricultural_loan(self, county="Nakuru", crop_name="Maize", acres=3.0, season="Long Rains (MAM)", borrower_name="Farmer Group A"):
        """
        Underwrites an agricultural loan package:
        - Calculates Composite Agricultural Risk Index (R_agri)
        - Computes Loan Eligibility (70% CapEx)
        - Calculates Risk-Weighted Interest Rate & Expected Default Probability
        - Provides Mitigations and Insurance requirements
        """
        profile = self.get_county_climate_profile(county, season)
        
        
        crop_meta = self.crops_df[self.crops_df["crop"] == crop_name]
        if crop_meta.empty:
            crop_meta = self.crops_df.iloc[0]
        else:
            crop_meta = crop_meta.iloc[0]

        
        r_climate = profile.get("drought_risk_index", 0.3)
        if profile.get("cluster_id") == 1:
            r_climate = max(r_climate, 0.45)

        
        rain_fit = 1.0 - min(1.0, abs(profile["seasonal_rainfall_mm"] - (crop_meta["min_rain_mm"] + crop_meta["max_rain_mm"])/2) / (crop_meta["max_rain_mm"] - crop_meta["min_rain_mm"] + 1e-5))
        temp_fit = 1.0 - min(1.0, abs(profile["temp_mean_c"] - (crop_meta["min_temp_c"] + crop_meta["max_temp_c"])/2) / (crop_meta["max_temp_c"] - crop_meta["min_temp_c"] + 1e-5))
        suitability_pct = float(np.clip((rain_fit * 0.6 + temp_fit * 0.4) * 100, 15.0, 95.0))
        r_crop = 1.0 - (suitability_pct / 100.0)

        
        market_opps = self.market_df[self.market_df["crop"] == crop_name] if self.market_df is not None else pd.DataFrame()
        r_market = float(market_opps["volatility_cv"].mean()) if not market_opps.empty else 0.20

        
        r_agri = round(0.40 * r_climate + 0.35 * r_crop + 0.25 * r_market, 3)

        
        if r_agri < 0.25:
            credit_grade = "AAA (Ultra-Low Risk)"
            risk_category = "Low"
            recommendation = "Approved - Prime Terms"
        elif r_agri < 0.38:
            credit_grade = "AA (Low Risk)"
            risk_category = "Low"
            recommendation = "Approved - Standard Terms"
        elif r_agri < 0.52:
            credit_grade = "A (Moderate Risk)"
            risk_category = "Moderate"
            recommendation = "Approved with Weather Insurance"
        elif r_agri < 0.65:
            credit_grade = "BBB (Elevated Risk)"
            risk_category = "Elevated"
            recommendation = "Conditional Approval - Mandatory Irrigation/Mulching"
        else:
            credit_grade = "High Risk / Subprime"
            risk_category = "High"
            recommendation = "Decline or Require Alternative Resilient Crop"

        
        cost_per_acre = crop_meta["cost_per_acre_kes"]
        total_project_cost = cost_per_acre * acres
        loan_principal = round(total_project_cost * 0.70, 0)

        
        base_rate = 0.120
        risk_premium = round(r_agri * 0.08, 3)
        risk_weighted_rate = round((base_rate + risk_premium) * 100, 2)

        
        expected_default_rate = round(float(np.clip(r_agri * 0.24, 0.03, 0.35)) * 100, 2)

        
        expected_yield = round(crop_meta["yield_per_acre_kg"] * (0.55 + 0.45 * (suitability_pct / 100.0)) * acres, 0)
        expected_revenue = round(expected_yield * crop_meta["base_price_kes_per_kg"], 0)
        debt_service_coverage = round(expected_revenue / max(1.0, loan_principal * (1 + risk_weighted_rate/100)), 2)

        
        mitigations = []
        if r_climate > 0.40:
            mitigations.append("Tie loan disbursement to Certified Drought-Resistant Seed Varieties.")
            mitigations.append("Bundle with KES 1,200/acre Index-Based Weather Crop Insurance.")
        if r_crop > 0.45:
            mitigations.append("Agronomic extension officer verification required before second tranche.")
        if r_market > 0.22:
            mitigations.append("Cooperative off-taker forward purchase contract recommended.")
        if not mitigations:
            mitigations.append("Standard seasonal farm monitoring.")

        report = ProvenanceReport()
        report.add("climate_risk_component", SourcedValue(
            value=round(r_climate, 3), provenance=Provenance.ESTIMATED,
            note="Derived from drought_risk_index, itself computed from TAHMO-derived rainfall aggregates plus a synthetic temperature estimate.",
        ))
        report.add("crop_suitability_component", self._crops_data_provenance())
        report.add("market_volatility_component", SourcedValue(
            value=round(r_market, 3), provenance=Provenance.ASSUMED,
            note="volatility_cv in market_prices.csv is randomly generated (np.random.uniform), not measured price variance. Do not treat this as a real risk input.",
        ))
        report.add("risk_weights", SourcedValue(
            value="0.40/0.35/0.25 climate/crop/market weighting; 12% base rate; premium/default formulas",
            provenance=Provenance.ASSUMED,
            note="Author-chosen constants, not calibrated against historical loan default data. Do not present interest_rate_pct or expected_default_rate_pct as actuarially validated until calibrated with a lending partner.",
        ))

        return {
            "borrower_name": borrower_name,
            "county": county,
            "crop": crop_name,
            "category": crop_meta["category"],
            "acres": acres,
            "season": season,
            "credit_grade": credit_grade,
            "risk_category": risk_category,
            "composite_risk_score": r_agri,
            "climate_risk_component": round(r_climate, 3),
            "crop_suitability_component": round(r_crop, 3),
            "market_volatility_component": round(r_market, 3),
            "total_project_cost_kes": int(total_project_cost),
            "loan_amount_kes": int(loan_principal),
            "interest_rate_pct": risk_weighted_rate,
            "expected_default_rate_pct": expected_default_rate,
            "expected_revenue_kes": int(expected_revenue),
            "debt_service_coverage_ratio": debt_service_coverage,
            "recommendation": recommendation,
            "mitigation_strategies": mitigations,
            "provenance": report.to_dict(),
        }

    
    def simulate_loan_portfolio(self, portfolio_items):
        """
        Simulates an aggregated agricultural loan portfolio for a Bank or SACCO.
        """
        underwritten_loans = []
        for item in portfolio_items:
            res = self.underwrite_agricultural_loan(
                county=item["county"],
                crop_name=item["crop"],
                acres=item.get("acres", 5.0),
                season=item.get("season", "Long Rains (MAM)"),
                borrower_name=item.get("borrower", f"Farmer Group {len(underwritten_loans)+1}")
            )
            underwritten_loans.append(res)

        df_port = pd.DataFrame(underwritten_loans)
        if df_port.empty:
            return {}, df_port

        total_disbursed = df_port["loan_amount_kes"].sum()
        weighted_interest = (df_port["loan_amount_kes"] * df_port["interest_rate_pct"]).sum() / max(1, total_disbursed)
        weighted_default = (df_port["loan_amount_kes"] * df_port["expected_default_rate_pct"]).sum() / max(1, total_disbursed)
        avg_risk = df_port["composite_risk_score"].mean()

        expected_gross_interest_income = total_disbursed * (weighted_interest / 100.0)
        expected_credit_losses = total_disbursed * (weighted_default / 100.0)
        net_portfolio_return_kes = expected_gross_interest_income - expected_credit_losses
        net_portfolio_roi_pct = round((net_portfolio_return_kes / max(1, total_disbursed)) * 100, 2)

        summary = {
            "total_loans_count": len(df_port),
            "total_disbursed_kes": int(total_disbursed),
            "average_risk_score": round(avg_risk, 3),
            "weighted_average_interest_rate_pct": round(weighted_interest, 2),
            "weighted_expected_default_rate_pct": round(weighted_default, 2),
            "expected_gross_income_kes": int(expected_gross_interest_income),
            "expected_credit_losses_kes": int(expected_credit_losses),
            "net_projected_roi_pct": net_portfolio_roi_pct,
        }

        return summary, df_port
