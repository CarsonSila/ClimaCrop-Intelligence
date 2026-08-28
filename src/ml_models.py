"""
Machine Learning Layer for Climate-Smart Agricultural Advisory System.
Implements:
1. Climate Pattern Clustering (K-Means) & Seasonal Trend Forecaster
2. 40-Crop Suitability Classifier (Random Forest / Scikit-Learn)
3. Market Price Forecaster & Regional Arbitrage Engine
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# ---------------------------------------------------------
# 1. CLIMATE PATTERN CLUSTERING (K-Means, k=3)
# ---------------------------------------------------------
class ClimatePatternEngine:
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.scaler = StandardScaler()
        self.cluster_labels = {
            0: "Normal / Favourable Season",
            1: "High Rainfall / Waterlogging Risk",
            2: "Drought / Moisture Stress Risk"
        }
        self.features = ["seasonal_rainfall_mm", "max_dry_spell_days", "temp_mean_c", "onset_week", "drought_risk_index"]

    def fit(self, df_climate):
        X = df_climate[self.features].fillna(df_climate[self.features].mean())
        X_scaled = self.scaler.fit_transform(X)
        self.kmeans.fit(X_scaled)
        
        centers = self.scaler.inverse_transform(self.kmeans.cluster_centers_)
        rain_idx = self.features.index("seasonal_rainfall_mm")
        sorted_cluster_order = np.argsort(centers[:, rain_idx])
        
        self.cluster_relabel_map = {
            sorted_cluster_order[0]: 2,
            sorted_cluster_order[1]: 0,
            sorted_cluster_order[2]: 1
        }
        return self

    def predict(self, df_climate):
        X = df_climate[self.features].fillna(df_climate[self.features].mean())
        X_scaled = self.scaler.transform(X)
        raw_clusters = self.kmeans.predict(X_scaled)
        mapped_clusters = np.array([self.cluster_relabel_map.get(c, 0) for c in raw_clusters])
        return mapped_clusters, [self.cluster_labels[c] for c in mapped_clusters]


# ---------------------------------------------------------
# 2. 40-CROP SUITABILITY ENGINE (Multi-Class Random Forest)
# ---------------------------------------------------------
class CropSuitabilityEngine:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=75, max_depth=10, min_samples_leaf=2, random_state=42)
        self.crops_df = None
        self.feature_cols = [
            "seasonal_rainfall_mm", "temp_mean_c", "temp_max_c", 
            "temp_min_c", "max_dry_spell_days", "onset_week", 
            "elevation_m", "drought_risk_index"
        ]

    def _generate_synthetic_training_data(self, crops_df, n_samples_per_crop=150):
        """Generates well-calibrated training data across Kenya's agro-climatic zones."""
        rows = []
        np.random.seed(42)
        
        for _, crop in crops_df.iterrows():
            crop_name = crop["crop"]
            min_r, max_r = crop["min_rain_mm"], crop["max_rain_mm"]
            min_t, max_t = crop["min_temp_c"], crop["max_temp_c"]
            drought_tol = crop["drought_tolerance"]
            
            # Elevation profile based on crop type
            if crop_name in ["Tea", "Pyrethrum", "Irish Potatoes"]:
                elev_mean, elev_std = 2200, 180
            elif crop_name in ["Coffee (Arabica)", "Wheat", "Garden Peas", "Cabbage", "Carrots"]:
                elev_mean, elev_std = 1850, 150
            elif crop_name in ["Maize", "Common Beans", "Tomatoes", "Bananas", "Avocado (Hass)", "Macadamia"]:
                elev_mean, elev_std = 1600, 200
            elif crop_name in ["Rice", "Sugarcane", "Mangoes", "Cashew Nuts", "Cotton"]:
                elev_mean, elev_std = 600, 250
            elif crop_name in ["Sorghum", "Pearl Millet", "Cowpeas (Kunde)", "Green Grams (Ndengu)", "Cassava", "Watermelon"]:
                elev_mean, elev_std = 950, 250
            else:
                elev_mean, elev_std = 1400, 250
                
            for _ in range(n_samples_per_crop):
                rain = np.clip(np.random.normal((min_r + max_r)/2, (max_r - min_r)/4.5), min_r * 0.9, max_r * 1.1)
                temp_avg = np.clip(np.random.normal((min_t + max_t)/2, (max_t - min_t)/4.5), min_t * 0.95, max_t * 1.05)
                temp_max = temp_avg + np.random.uniform(5.0, 7.0)
                temp_min = temp_avg - np.random.uniform(5.0, 7.0)
                
                dry_spell_mean = (11 - drought_tol) * 2.0
                dry_spell = int(np.clip(np.random.normal(dry_spell_mean, 2.0), 2, 40))
                onset_w = int(np.clip(np.random.normal(3.0, 1.2), 1, 8))
                elev = np.clip(np.random.normal(elev_mean, elev_std), 10, 3200)
                drought_idx = max(0.0, min(1.0, (1.0 - (rain / 550.0)) * 0.6 + (dry_spell / 30.0) * 0.4))
                
                rows.append({
                    "seasonal_rainfall_mm": round(rain, 1),
                    "temp_mean_c": round(temp_avg, 1),
                    "temp_max_c": round(temp_max, 1),
                    "temp_min_c": round(temp_min, 1),
                    "max_dry_spell_days": dry_spell,
                    "onset_week": onset_w,
                    "elevation_m": round(elev, 0),
                    "drought_risk_index": round(drought_idx, 3),
                    "target_crop": crop_name
                })
                
        return pd.DataFrame(rows)

    def fit(self, crops_df):
        self.crops_df = crops_df.copy()
        df_train = self._generate_synthetic_training_data(crops_df)
        X = df_train[self.feature_cols]
        y = df_train["target_crop"]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        self.model.fit(X_train, y_train)
        
        acc = accuracy_score(y_test, self.model.predict(X_test))
        print(f"Crop Suitability Random Forest trained with Test Accuracy: {acc * 100:.2f}%")
        return self

    def recommend(self, climate_input_dict, top_n=5, category_filter="All"):
        input_df = pd.DataFrame([climate_input_dict])[self.feature_cols]
        probs = self.model.predict_proba(input_df)[0]
        classes = self.model.classes_
        
        results = []
        for crop_name, prob in zip(classes, probs):
            crop_meta = self.crops_df[self.crops_df["crop"] == crop_name]
            if crop_meta.empty:
                continue
            meta = crop_meta.iloc[0]
            
            if category_filter != "All" and meta["category"] != category_filter:
                continue
                
            rain_fit = 1.0 - min(1.0, abs(climate_input_dict["seasonal_rainfall_mm"] - (meta["min_rain_mm"] + meta["max_rain_mm"])/2) / (meta["max_rain_mm"] - meta["min_rain_mm"] + 1e-5))
            temp_fit = 1.0 - min(1.0, abs(climate_input_dict["temp_mean_c"] - (meta["min_temp_c"] + meta["max_temp_c"])/2) / (meta["max_temp_c"] - meta["min_temp_c"] + 1e-5))
            rule_fit = max(0.1, (rain_fit * 0.6 + temp_fit * 0.4))
            
            suitability_score = float(np.clip((prob * 4.0 * 0.4 + rule_fit * 0.6) * 100, 20.0, 96.0))
            
            base_yield = meta["yield_per_acre_kg"]
            expected_yield_kg = round(base_yield * (0.55 + 0.45 * (suitability_score / 100.0)), 0)
            
            cost_acre = meta["cost_per_acre_kes"]
            base_price = meta["base_price_kes_per_kg"]
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
                "crop": crop_name,
                "category": meta["category"],
                "suitability_score": round(suitability_score, 1),
                "risk_level": risk_level,
                "expected_yield_kg_per_acre": int(expected_yield_kg),
                "cost_per_acre_kes": int(cost_acre),
                "expected_revenue_kes": int(expected_revenue_acre),
                "net_profit_kes_per_acre": int(net_profit_acre),
                "benefit_cost_ratio": bcr,
                "drought_tolerance": int(meta["drought_tolerance"]),
                "growth_days": int(meta["growth_days"]),
            })
            
        df_res = pd.DataFrame(results).sort_values(by=["suitability_score", "net_profit_kes_per_acre"], ascending=[False, False])
        return df_res.head(top_n)


# ---------------------------------------------------------
# 3. REGIONAL MARKET FORECASTER & ARBITRAGE OPTIMIZER
# ---------------------------------------------------------
class MarketArbitrageEngine:
    def __init__(self):
        self.market_df = None

    def fit(self, market_df):
        self.market_df = market_df.copy()
        return self

    def get_market_opportunities(self, crop_name, origin_county="Nakuru"):
        crop_markets = self.market_df[self.market_df["crop"] == crop_name].copy()
        if crop_markets.empty:
            return pd.DataFrame()
            
        transport_matrix = {
            "Nakuru": {"Nairobi (Wakulima)": 6.0, "Nakuru": 1.5, "Eldoret": 4.5, "Kisumu (Jubilee)": 6.5, "Mombasa (Kongowea)": 14.0},
            "Uasin Gishu": {"Nairobi (Wakulima)": 9.0, "Nakuru": 4.5, "Eldoret": 1.5, "Kisumu (Jubilee)": 4.0, "Mombasa (Kongowea)": 17.0},
            "Kiambu": {"Nairobi (Wakulima)": 2.0, "Nakuru": 5.5, "Eldoret": 8.5, "Kisumu (Jubilee)": 10.0, "Mombasa (Kongowea)": 12.0},
            "Makueni": {"Nairobi (Wakulima)": 4.5, "Nakuru": 9.0, "Eldoret": 12.0, "Kisumu (Jubilee)": 13.5, "Mombasa (Kongowea)": 7.0},
            "Bungoma": {"Nairobi (Wakulima)": 11.0, "Nakuru": 6.5, "Eldoret": 3.0, "Kisumu (Jubilee)": 2.5, "Mombasa (Kongowea)": 19.0},
            "Kisumu": {"Nairobi (Wakulima)": 10.0, "Nakuru": 6.0, "Eldoret": 4.0, "Kisumu (Jubilee)": 1.5, "Mombasa (Kongowea)": 18.0},
            "Kwale": {"Nairobi (Wakulima)": 12.0, "Nakuru": 15.0, "Eldoret": 17.0, "Kisumu (Jubilee)": 18.0, "Mombasa (Kongowea)": 2.0},
        }
        
        county_trans = transport_matrix.get(origin_county, {"Nairobi (Wakulima)": 7.0, "Nakuru": 6.0, "Eldoret": 6.0, "Kisumu (Jubilee)": 6.0, "Mombasa (Kongowea)": 13.0})
        
        crop_markets["est_transport_kes_per_kg"] = crop_markets["market"].map(county_trans).fillna(6.0)
        crop_markets["net_market_price_kes"] = np.round(crop_markets["market_price"] - crop_markets["est_transport_kes_per_kg"], 1)
        crop_markets["arbitrage_margin_vs_base"] = np.round(crop_markets["net_market_price_kes"] - crop_markets["base_price"], 1)
        
        crop_markets = crop_markets.sort_values(by="net_market_price_kes", ascending=False)
        return crop_markets[["market", "base_price", "market_price", "est_transport_kes_per_kg", "net_market_price_kes", "arbitrage_margin_vs_base", "volatility_cv"]]

