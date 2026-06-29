"""
Hyperparameter search for RandomForestRegressor using time-series cross-validation.

Trains on data up to (but not including) TUNE_END_SEASON, runs
RandomizedSearchCV with TimeSeriesSplit, and prints the best parameters.
Copy the printed params into compare_models.py MODEL_CONFIGS to benchmark them.

Run from the backend directory:
    uv run python scripts/tune_random_forest.py
    uv run python scripts/tune_random_forest.py --n-iter 100 --cv-splits 5
"""

import argparse
import logging
import sys

import numpy as np
from scipy.stats import randint, uniform
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, ".")

from app.services.data_processing.data_loader import clean_data, load_training_data
from app.services.models.config import FEATURES, LABELS
from app.services.models.preprocess import check_data, preprocess_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Tune on data up to (not including) this season so 2023-2025 stays a clean hold-out
TUNE_END_YEAR = 2022  # uses 2014-2015 through 2022-2023

PARAM_DISTRIBUTIONS = {
    "estimator__n_estimators": randint(100, 600),
    "estimator__max_depth": [None, 5, 8, 10, 15, 20],
    "estimator__min_samples_split": randint(2, 20),
    "estimator__min_samples_leaf": randint(1, 10),
    "estimator__max_features": ["sqrt", "log2", 0.5, 0.7, 1.0],
    "estimator__max_samples": uniform(0.6, 0.4),  # bootstrap sample fraction 0.6–1.0
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-iter", type=int, default=60, help="Number of random search iterations")
    parser.add_argument("--cv-splits", type=int, default=4, help="Number of TimeSeriesSplit folds")
    args = parser.parse_args()

    logger.info(f"Loading training data up to {TUNE_END_YEAR}-{TUNE_END_YEAR + 1}...")
    df = load_training_data(end_season=TUNE_END_YEAR)
    df = clean_data(df)
    df = preprocess_data(df, test_data=False)
    df = df.sort_values("date").reset_index(drop=True)

    X = df[FEATURES]
    y = df[LABELS]
    check_data(X)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    logger.info(f"Running RandomizedSearchCV: {args.n_iter} iterations, {args.cv_splits} folds")
    logger.info(f"Training samples: {len(X_scaled)}, features: {X_scaled.shape[1]}")

    # MultiOutputRegressor wraps a single-output RF to predict both FTHG and FTAG
    # TimeSeriesSplit respects chronological order — no future data leaks into folds
    base = MultiOutputRegressor(RandomForestRegressor(random_state=42, n_jobs=-1))
    tscv = TimeSeriesSplit(n_splits=args.cv_splits)

    search = RandomizedSearchCV(
        estimator=base,
        param_distributions=PARAM_DISTRIBUTIONS,
        n_iter=args.n_iter,
        cv=tscv,
        scoring="neg_mean_absolute_error",
        random_state=42,
        n_jobs=-1,
        verbose=1,
        refit=True,
    )

    search.fit(X_scaled, y)

    best = search.best_params_
    # Strip "estimator__" prefix for readability
    clean_params = {k.replace("estimator__", ""): v for k, v in best.items()}

    logger.info(f"Best CV MAE: {-search.best_score_:.4f}")
    print("\n" + "=" * 60)
    print("BEST PARAMETERS")
    print("=" * 60)
    for k, v in sorted(clean_params.items()):
        print(f"  {k}: {v}")

    print("\nAdd to compare_models.py MODEL_CONFIGS:")
    params_str = ", ".join(
        f"{k}={repr(v)}" for k, v in sorted(clean_params.items())
    )
    print(f'  ("RandomForest (tuned)", GoalPredictor(')
    print(f'      RandomForestRegressor({params_str}, random_state=42)')
    print(f'  )),')

    # Show top 10 CV results
    import pandas as pd
    results = pd.DataFrame(search.cv_results_)
    results["mean_mae"] = -results["mean_test_score"]
    top = results.nsmallest(10, "mean_mae")[["mean_mae", "std_test_score", "params"]]
    print("\nTop 10 parameter combinations (by CV MAE):")
    for _, row in top.iterrows():
        clean = {k.replace("estimator__", ""): v for k, v in row["params"].items()}
        print(f"  MAE={row['mean_mae']:.4f} ± {abs(row['std_test_score']):.4f}  {clean}")


if __name__ == "__main__":
    main()
