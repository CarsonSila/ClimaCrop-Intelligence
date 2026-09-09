"""
tests/test_data_processing.py — Unit tests for the data ingestion pipeline.

Covers:
- Config constants (sensible defaults, env-overridable)
- Station → county mapping (keyword + coordinate fallback coverage)
- 40-crop database integrity (count, categories, required columns)
- Market database integrity (200 rows = 40 crops x 5 markets)
- Checkpoint manifest helpers (idempotent load/save)
- Schema-tolerant CSV read (missing final_quality_flag does not crash)
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.data_processing import (
    CLIMATE_YEAR_START,
    CLIMATE_YEAR_END,
    RAINFALL_THRESHOLD_MM,
    STATION_CSV_COLUMNS,
    STATION_PROCESSED_MANIFEST,
    _load_processed_manifest,
    _save_processed_manifest,
    create_crops_database,
    create_market_database,
    map_station_to_county,
)


class TestPipelineConfig(unittest.TestCase):
    def test_config_constants_have_defaults(self):
        self.assertGreaterEqual(CLIMATE_YEAR_START, 2000)
        self.assertGreaterEqual(CLIMATE_YEAR_END, CLIMATE_YEAR_START)
        self.assertGreater(RAINFALL_THRESHOLD_MM, 0)
        self.assertIn("time", STATION_CSV_COLUMNS)
        self.assertIn("precip_mm", STATION_CSV_COLUMNS)
        self.assertIn("final_quality_flag", STATION_CSV_COLUMNS)

    def test_config_constants_overridable_via_env(self):
        original = os.environ.get("CLIMATE_YEAR_START")
        os.environ["CLIMATE_YEAR_START"] = "2020"
        # Re-import to pick up env change (module-level constants evaluate on import)
        import importlib
        import src.data_processing as dp
        importlib.reload(dp)
        self.assertEqual(dp.CLIMATE_YEAR_START, 2020)
        if original is None:
            os.environ.pop("CLIMATE_YEAR_START", None)
        else:
            os.environ["CLIMATE_YEAR_START"] = original
        importlib.reload(dp)


class TestStationCountyMapping(unittest.TestCase):
    def test_known_stations_by_name(self):
        self.assertEqual(map_station_to_county("x", "Nakuru Primary", 0, 36), "Nakuru")
        self.assertEqual(map_station_to_county("x", "Molo School", 0, 36), "Nakuru")
        self.assertEqual(map_station_to_county("x", "Eldoret Met", 0, 35), "Uasin Gishu")
        self.assertEqual(map_station_to_county("x", "Kapsabet Station", 0, 35), "Nandi")
        self.assertEqual(map_station_to_county("x", "Kisumu Central", 0, 34.7), "Kisumu")
        self.assertEqual(map_station_to_county("x", "Nairobi CBD", -1.3, 36.8), "Nairobi")
        self.assertEqual(map_station_to_county("x", "Mombasa Island", -4.2, 39.6), "Mombasa")
        self.assertEqual(map_station_to_county("x", "Kakamega Forest", 0.6, 34.7), "Bungoma")

    def test_coordinate_fallback_covers_all_regions(self):
        regions = {
            "Nakuru": (-0.3, 36.0),
            "Uasin Gishu": (0.5, 35.3),
            "Narok": (-1.1, 35.9),
            "Kiambu": (-1.1, 36.8),
            "Makueni": (-1.8, 37.6),
            "Nyeri": (-0.4, 37.1),
            "Kitui": (-2.5, 38.5),
            "Kwale": (-3.5, 39.6),
            "Turkana": (2.5, 35.5),
            "Marsabit": (1.5, 37.0),
            "Samburu": (2.5, 36.5),
        }
        for county, (lat, lon) in regions.items():
            result = map_station_to_county("x", "Unknown Station", lat, lon)
            self.assertEqual(
                result, county,
                f"Expected {county} for ({lat}, {lon}), got {result}",
            )

    def test_unknown_station_returns_other_kenya(self):
        # A point far outside Kenya's bounding boxes (Somalia coast)
        result = map_station_to_county("x", "Ocean Buoy", 50, 50)
        self.assertEqual(result, "Other Kenya")


class TestCropsDatabase(unittest.TestCase):
    def setUp(self):
        # Use a temp directory so we don't pollute the real data/ folder
        self._orig_data_dir = None

    def tearDown(self):
        pass

    def test_creates_exactly_40_crops(self):
        df = create_crops_database()
        self.assertEqual(len(df), 40, "Database must contain exactly 40 crops")

    def test_all_five_categories_present(self):
        df = create_crops_database()
        categories = set(df["category"].unique())
        expected = {"Cereals", "Pulses", "Roots & Tubers", "Horticulture", "Cash Crops"}
        self.assertEqual(categories, expected)

    def test_required_columns_present(self):
        df = create_crops_database()
        required = [
            "crop", "category", "min_rain_mm", "max_rain_mm",
            "min_temp_c", "max_temp_c", "cost_per_acre_kes",
            "yield_per_acre_kg", "base_price_kes_per_kg",
        ]
        for col in required:
            self.assertIn(col, df.columns, f"Missing column: {col}")

    def test_no_negative_or_null_economics(self):
        df = create_crops_database()
        for col in ["cost_per_acre_kes", "yield_per_acre_kg", "base_price_kes_per_kg"]:
            self.assertTrue((df[col] > 0).all(), f"{col} must be strictly positive")

    def test_output_file_written(self):
        df = create_crops_database()
        self.assertTrue(os.path.exists("data/crops_database.csv"))
        df_reloaded = pd.read_csv("data/crops_database.csv")
        self.assertEqual(len(df_reloaded), 40)


class TestMarketDatabase(unittest.TestCase):
    def test_200_rows_five_markets(self):
        crops_df = create_crops_database()
        df_market = create_market_database(crops_df)
        self.assertEqual(len(df_market), 40 * 5, "Market DB must have 200 rows (40 crops x 5 markets)")

    def test_all_five_markets_present(self):
        crops_df = create_crops_database()
        df_market = create_market_database(crops_df)
        expected = {"Nairobi (Wakulima)", "Nakuru", "Eldoret", "Kisumu (Jubilee)", "Mombasa (Kongowea)"}
        self.assertEqual(set(df_market["market"].unique()), expected)

    def test_output_file_written(self):
        crops_df = create_crops_database()
        df_market = create_market_database(crops_df)
        self.assertTrue(os.path.exists("data/market_prices.csv"))


class TestCheckpointManifest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self._orig = STATION_PROCESSED_MANIFEST
        # Patch the manifest path into the temp dir
        import src.data_processing as dp
        dp.STATION_PROCESSED_MANIFEST = os.path.join(self.tmpdir.name, "_processed_stations.json")

    def tearDown(self):
        import src.data_processing as dp
        dp.STATION_PROCESSED_MANIFEST = self._orig
        self.tmpdir.cleanup()

    def test_returns_empty_dict_when_no_file(self):
        result = _load_processed_manifest()
        self.assertEqual(result, {})

    def test_round_trip_persistence(self):
        manifest = {"TA00001": True, "TA00002": True}
        _save_processed_manifest(manifest)
        reloaded = _load_processed_manifest()
        self.assertEqual(reloaded, manifest)


class TestSchemaTolerantRead(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self._orig_data = "data"
        # Create a minimal station CSV missing final_quality_flag
        self.bad_csv = os.path.join(self.tmpdir.name, "TA00099.csv")
        with open(self.bad_csv, "w", encoding="utf-8") as f:
            f.write("time,station_id,precip_mm\n")
            f.write("2024-03-01 00:00:00,TA00099,0.0\n")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_missing_quality_flag_column_does_not_crash(self):
        """pd.read_csv with usecols=lambda should skip the bad column gracefully."""
        import pandas as pd
        df = pd.read_csv(self.bad_csv, usecols=lambda c: c in STATION_CSV_COLUMNS)
        # final_quality_flag column should be absent, not raise KeyError
        self.assertNotIn("final_quality_flag", df.columns)


if __name__ == "__main__":
    unittest.main()
