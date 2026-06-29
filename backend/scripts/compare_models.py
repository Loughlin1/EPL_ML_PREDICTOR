"""
Compare multiple model types across all trainable seasons.

For each model config and each season, trains on all data before that season
and evaluates on the season's held-out data (last 20% chronologically).
Prints a summary table and optionally saves results to CSV.

Run from the backend directory:
    uv run python scripts/compare_models.py
    uv run python scripts/compare_models.py --output results.csv
"""

import argparse
import logging
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, PoissonRegressor
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, ".")

from app.services.data_processing.data_loader import clean_data, load_training_data
from app.services.models.config import FEATURES, LABELS
from app.services.models.evaluation import evaluate_model_performance
from app.services.models.preprocess import check_data, preprocess_data
from app.services.models.wrapper import GoalPredictor

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TRAINABLE_SEASONS = [
    "2015-2016",
    "2016-2017",
    "2017-2018",
    "2018-2019",
    "2019-2020",
    "2020-2021",
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025",
]

# Each entry is (display_name, GoalPredictor instance)
MODEL_CONFIGS = [
    ("LinearRegression", GoalPredictor(LinearRegression())),
    ("PoissonRegressor (home)", GoalPredictor(
        PoissonRegressor(max_iter=500), PoissonRegressor(max_iter=500)
    )),
    ("RandomForest", GoalPredictor(
        RandomForestRegressor(n_estimators=100, random_state=42)
    )),
    ("GradientBoosting (home)", GoalPredictor(
        GradientBoostingRegressor(n_estimators=100, random_state=42),
        GradientBoostingRegressor(n_estimators=100, random_state=42),
    )),
]

DISPLAY_METRICS = [
    "MAE_Total",
    "RMSE_Total",
    "Correct_Result_%",
    "Correct_Scores_%",
    "Goal_Difference_Accuracy",
]


def _train_and_evaluate(model_name: str, predictor: GoalPredictor, season: str) -> dict | None:
    """Train predictor on data before season, evaluate on season's held-out 20%."""
    end_year = int(season.split("-")[0]) - 1
    try:
        df = load_training_data(end_season=end_year)
        df = clean_data(df)
        df = preprocess_data(df, test_data=False)
        df = df.sort_values("date").reset_index(drop=True)

        X = df[FEATURES]
        y = df[LABELS]
        check_data(X)

        split_idx = int(len(df) * 0.8)
        X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)

        # Clone the predictor so configs stay reusable across seasons
        import copy
        p = copy.deepcopy(predictor)
        p.fit(X_train_scaled, y_train)

        raw_preds = p.predict(X_val_scaled)
        y_pred = pd.DataFrame(raw_preds, columns=LABELS)
        y_val = y_val.reset_index(drop=True)

        metrics = evaluate_model_performance(y_val, y_pred)
        return metrics

    except Exception as e:
        logger.warning(f"[{model_name}] season {season} failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Save results table to this CSV path", default=None)
    args = parser.parse_args()

    records = []
    for model_name, predictor in MODEL_CONFIGS:
        print(f"\nEvaluating: {model_name}")
        for season in TRAINABLE_SEASONS:
            print(f"  {season}...", end=" ", flush=True)
            metrics = _train_and_evaluate(model_name, predictor, season)
            if metrics:
                print(f"MAE={metrics['MAE_Total']:.3f}  Result%={metrics['Correct_Result_%']:.1f}%")
                records.append({"model": model_name, "season": season, **metrics})
            else:
                print("FAILED")

    if not records:
        print("No results to display.")
        return

    df = pd.DataFrame(records)

    # Per-model averages across seasons
    print("\n" + "=" * 80)
    print("AVERAGES ACROSS ALL SEASONS")
    print("=" * 80)
    avg = (
        df.groupby("model")[DISPLAY_METRICS]
        .mean()
        .round(3)
        .sort_values("Correct_Result_%", ascending=False)
    )
    print(avg.to_string())

    # Full per-season breakdown
    print("\n" + "=" * 80)
    print("PER-SEASON BREAKDOWN")
    print("=" * 80)
    for model_name in df["model"].unique():
        print(f"\n{model_name}")
        subset = df[df["model"] == model_name][["season"] + DISPLAY_METRICS].set_index("season")
        print(subset.to_string())

    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\nSaved full results to {args.output}")


if __name__ == "__main__":
    main()
