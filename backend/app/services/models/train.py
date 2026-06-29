"""
train.py

This script performs
    - data loading, cleaning, feature engineering, encoding, and model training

for predicting full-time home and away goals in English Premier League matches
using a RandomForestRegressor.

Workflow:
    1. Load match data from database.
    2. Clean and preprocess the data.
    3. Add new features such as full-time goals, match result, season year, etc.
    4. Calculate rolling averages for shooting statistics and points per game.
    5. Prepare features and labels for model training.
    6. Scale the features.
    7. Split the data into training and testing sets.
    8. Train a RandomForestRegressor model and make predictions on the test set.
"""

import logging

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ...core.config import settings
from ...core.paths import (
    SAVED_MODELS_DIRECTORY,
)
from ..data_processing.data_loader import clean_data, load_training_data
from ..models.config import FEATURES, LABELS
from ..models.save_load import save_model, save_model_for_season, save_scaler, save_scaler_for_season
from .preprocess import check_data, preprocess_data


def train_pipeline(season: str = None):
    """
    Train a model for the given season.

    If season is provided, trains on all data *before* that season and saves
    season-scoped artifacts (model_{season}.joblib, scaler_{season}.pkl).
    If no season is given, trains on all available data and saves the default
    best_model.joblib used for the current season.

    Args:
        season: Target season string e.g. "2024-2025". Trains on data up to
                but not including this season.
    """
    if season:
        # e.g. "2024-2025" → train on 2014-2023
        end_year = int(season.split("-")[0]) - 1
    else:
        end_year = None  # use config default

    # Load data
    df = load_training_data(end_season=end_year)
    df = clean_data(df)
    df = preprocess_data(df, test_data=False)
    X = df[FEATURES]
    y = df[LABELS]
    check_data(X)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    # Scaling features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # Train model
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)

    # Save artifacts — season-scoped if a season was given, otherwise default
    if season:
        save_model_for_season(model, season)
        save_scaler_for_season(scaler, season)
    else:
        save_model(model, "best_model.joblib", SAVED_MODELS_DIRECTORY)
        save_scaler(scaler)


def train_model(season: str = None):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    label = season or settings.CURRENT_SEASON
    logger.info(f"Starting training pipeline for season {label}...")
    train_pipeline(season=season)
    logger.info("Training complete. Model saved.")
    return {"status": "success", "message": f"Model trained and saved for season {label}."}


if __name__ == "__main__":
    train_pipeline()
