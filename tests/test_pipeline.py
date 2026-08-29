import os
import unittest
import pandas as pd
import numpy as np

from src.financial_engine import FinancialDecisionEngine
from src.ml_models import ClimatePatternEngine, CropSuitabilityEngine, MarketArbitrageEngine


class TestKilimoSmartPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = FinancialDecisionEngine()

    def test_01_crops_database_integrity(self):
        """Verify the 40-crop benchmark database meets requirements."""
        self.assertTrue(os.path.exists("data/crops_database.csv"), "crops_database.csv should exist")
        df_crops = pd.read_csv("data/crops_database.csv")
        self.assertEqual(len(df_crops), 40, "Database must contain exactly 40 crops")
        
        required_cols = ["crop", "category", "min_rain_mm", "max_rain_mm", "min_temp_c", "max_temp_c", "cost_per_acre_kes", "yield_per_acre_kg", "base_price_kes_per_kg"]
        for col in required_cols:
            self.assertIn(col, df_crops.columns, f"Missing column: {col}")
            
        
        categories = set(df_crops["category"].unique())
        expected_cats = {"Cereals", "Pulses", "Roots & Tubers", "Horticulture", "Cash Crops"}
        self.assertEqual(categories, expected_cats, "All 5 crop categories must be present")

    def test_02_market_database_integrity(self):
        """Verify regional market pricing covers all 5 trading hubs."""
        self.assertTrue(os.path.exists("data/market_prices.csv"), "market_prices.csv should exist")
        df_market = pd.read_csv("data/market_prices.csv")
        self.assertEqual(len(df_market), 40 * 5, "Market database should have 200 rows (40 crops x 5 markets)")
        
        expected_markets = {"Nairobi (Wakulima)", "Nakuru", "Eldoret", "Kisumu (Jubilee)", "Mombasa (Kongowea)"}
        markets = set(df_market["market"].unique())
        self.assertEqual(markets, expected_markets, "All 5 trading hubs must exist")

    def test_03_cooperative_recommendations(self):
        """Test the cooperative crop recommendation logic."""
        recs, climate, provenance = self.engine.get_cooperative_recommendations(
            county="Nakuru",
            season="Long Rains (MAM)",
            farm_size_acres=3.0,
            category_filter="All",
            top_n=5
        )
        self.assertFalse(recs.empty, "Recommendations should not be empty")
        self.assertLessEqual(len(recs), 5, "Should return at most top_n crops")
        
        
        for _, row in recs.iterrows():
            self.assertGreater(row["suitability_score"], 0, "Suitability score must be positive")
            self.assertGreater(row["total_production_cost_kes"], 0, "Production cost must be positive")
            self.assertGreater(row["total_farm_yield_kg"], 0, "Yield must be positive")
            self.assertGreater(row["benefit_cost_ratio"], 0.5, "BCR must be reasonable")
            self.assertIn(row["risk_level"], ["Low", "Moderate", "High"], "Risk level must be valid")

    def test_03b_provenance_report_present(self):
        """Every recommendation batch must ship a provenance report, and it
        must not silently claim high confidence for placeholder data."""
        recs, climate, provenance = self.engine.get_cooperative_recommendations(
            county="Nakuru", season="Long Rains (MAM)", farm_size_acres=3.0
        )
        self.assertIn("overall_confidence", provenance)
        self.assertIn("weakest_link", provenance)
        self.assertLess(provenance["overall_confidence"], 0.85,
                         "Confidence should reflect that crop economics and market prices are still unverified placeholders.")

    def test_04_bank_loan_underwriting(self):
        """Test agricultural loan underwriting for banks and SACCOs."""
        loan = self.engine.underwrite_agricultural_loan(
            county="Nakuru",
            crop_name="Maize",
            acres=5.0,
            season="Long Rains (MAM)",
            borrower_name="Test Farmer Group"
        )
        
        
        expected_loan = round(loan["total_project_cost_kes"] * 0.70, 0)
        self.assertEqual(loan["loan_amount_kes"], int(expected_loan), "Loan facility should equal 70% of CapEx")
        
        
        self.assertGreaterEqual(loan["composite_risk_score"], 0.0)
        self.assertLessEqual(loan["composite_risk_score"], 1.0)
        
        
        self.assertGreaterEqual(loan["interest_rate_pct"], 12.0, "Interest rate must be >= Base 12%")
        self.assertLessEqual(loan["interest_rate_pct"], 22.0, "Interest rate should not exceed ceiling")
        
        
        self.assertIsInstance(loan["mitigation_strategies"], list)
        self.assertGreater(len(loan["mitigation_strategies"]), 0, "Must recommend mitigations")

        
        self.assertIn("provenance", loan)
        self.assertIn("risk_weights", loan["provenance"]["fields"])
        self.assertEqual(loan["provenance"]["fields"]["risk_weights"]["provenance"], "assumed",
                          "Risk-weighting constants must be flagged as unvalidated until calibrated against real default data.")

    def test_05_portfolio_simulation(self):
        """Test aggregate portfolio simulation."""
        portfolio = [
            {"county": "Nakuru", "crop": "Maize", "acres": 5.0},
            {"county": "Makueni", "crop": "Green Grams (Ndengu)", "acres": 10.0},
            {"county": "Kitui", "crop": "Sorghum", "acres": 8.0},
        ]
        summary, df_port = self.engine.simulate_loan_portfolio(portfolio)
        
        self.assertEqual(summary["total_loans_count"], 3)
        self.assertGreater(summary["total_disbursed_kes"], 0)
        self.assertGreater(summary["weighted_average_interest_rate_pct"], 12.0)
        self.assertGreater(summary["net_projected_roi_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
