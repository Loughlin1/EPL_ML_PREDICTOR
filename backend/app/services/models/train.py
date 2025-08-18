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
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ...core.paths import (
    SAVED_MODELS_DIRECTORY,
)
from ..data_processing.data_loader import clean_data, load_training_data
from ..models.save_load import save_model, save_scaler
from ..models.config import FEATURES, LABELS, SH_ROLLING_HOME_COLS
from .preprocess import preprocess_data, check_data


def train_pipeline():
    # Load data
    df = load_training_data()
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
    save_scaler(scaler)

    # Train model
    model = LinearRegression()
    # model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Save model
    save_model(model, "best_model.joblib", SAVED_MODELS_DIRECTORY)


def train_model():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    logger.info("Starting training pipeline...")
    train_pipeline()
    logger.info("Training complete. Model saved.")
    return {"status": "success", "message": "Model trained and saved."}


if __name__ == "__main__":
    train_pipeline()
