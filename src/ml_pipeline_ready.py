from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

from src.provenance import Provenance, SourcedValue


class NotEnoughRealData(RuntimeError):
    pass


REQUIRED_REAL_COLUMNS = {
    "county", "season", "year", "crop",
    "seasonal_rainfall_mm", "temp_mean_c",
    "actual_yield_kg_per_acre",
}


class YieldOutcomeModel:
    def __init__(self):
        self.model = GradientBoostingRegressor(random_state=42)
        self.feature_cols = ["seasonal_rainfall_mm", "temp_mean_c", "max_dry_spell_days",
                              "onset_week", "elevation_m", "rule_based_suitability_score"]
        self.is_fitted = False

    def fit(self, outcomes_df: pd.DataFrame, split_year: int):
        missing = REQUIRED_REAL_COLUMNS - set(outcomes_df.columns)
        if missing:
            raise NotEnoughRealData(
                f"outcomes_df is missing real observed columns: {missing}. "
                f"This model refuses to train on synthetic/estimated data — "
                f"it needs actual recorded yields per county/season/crop, e.g. "
                f"from KALRO trial records, an agricultural census, or farmer-reported "
                f"harvest data collected over at least 2-3 real seasons."
            )
        if outcomes_df["year"].nunique() < 3:
            raise NotEnoughRealData(
                f"Only {outcomes_df['year'].nunique()} distinct year(s) of real outcomes found. "
                f"A time-based train/test split needs at least a few real seasons to be "
                f"meaningful — with fewer than that, any reported accuracy is not trustworthy."
            )

        train = outcomes_df[outcomes_df["year"] < split_year]
        test = outcomes_df[outcomes_df["year"] >= split_year]
        if train.empty or test.empty:
            raise NotEnoughRealData(
                f"split_year={split_year} leaves an empty train or test set. "
                f"Choose a split_year that has real data on both sides of it."
            )

        X_train, y_train = train[self.feature_cols], train["actual_yield_kg_per_acre"]
        X_test, y_test = test[self.feature_cols], test["actual_yield_kg_per_acre"]

        self.model.fit(X_train, y_train)
        preds = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        self.is_fitted = True

        return SourcedValue(
            value=round(mae, 1),
            provenance=Provenance.MODELED,
            note=(f"Mean absolute error of {mae:.1f} kg/acre on a TIME-based holdout "
                  f"(trained on seasons before {split_year}, tested on {split_year} onward), "
                  f"trained on {len(train)} real observed outcomes. Report this metric "
                  f"alongside the rule-based score, don't hide it."),
        )

    def predict(self, features: dict) -> SourcedValue:
        if not self.is_fitted:
            raise RuntimeError("Model has not been fit on real data yet.")
        X = pd.DataFrame([features])[self.feature_cols]
        pred = float(self.model.predict(X)[0])
        return SourcedValue(
            value=round(pred, 0),
            provenance=Provenance.MODELED,
            note="Gradient-boosted prediction trained on real observed yield outcomes with a time-based holdout. See the model's reported MAE for how much to trust this.",
        )


if __name__ == "__main__":
    fake_df = pd.DataFrame({"county": ["Nakuru"], "season": ["Long Rains (MAM)"], "year": [2024]})
    try:
        YieldOutcomeModel().fit(fake_df, split_year=2023)
    except NotEnoughRealData as e:
        print(f"[Expected] {e}")
