"""
train.py

This script performs
    - data loading, cleaning, feature engineering, encoding, and model training

for predicting full-time home and away goals in English Premier League matches
using a RandomForestRegressor.

Workflow:
    1. Load match data from CSV files.
    2. Clean and preprocess the data.
    3. Add new features such as full-time goals, match result, season year, etc.
    4. Calculate rolling averages for shooting statistics and points per game.
    5. Prepare features and labels for model training.
    6. Scale the features.
    7. Split the data into training and testing sets.
    8. Train a RandomForestRegressor model and make predictions on the test set.
"""

import json
import logging
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ...core.paths import (
    SHOOTING_TRAINING_DATA_DIR,
    TEAM_ENCODER_FILEPATH,
    TEAMS_TRAINING_FILEPATH,
    VENUE_ENCODER_FILEPATH,
    FIXTURES_TRAINING_DATA_DIR,
    SAVED_MODELS_DIRECTORY,
)
from ..data_processing.data_loader import clean_data, load_training_data
from ..data_processing.feature_encoding import (
    encode_day_of_week,
    encode_season_column,
    encode_team_name_features,
    encode_venue_name_feature,
    fit_team_name_encoder,
    fit_venue_encoder,
    save_encoder_to_file,
)
from ..data_processing.feature_engineering import (
    add_hour_feature,
    add_ppg_features,
    add_rolling_shooting_stats,
    add_season_column,
    calculate_match_points,
    calculate_result,
    split_score_column,
)
from ..models.save_load import save_model
from ..models.config import FEATURES, rolling_home_cols

with open(TEAMS_TRAINING_FILEPATH, "r") as f:
    teams = json.load(f) # Doesn't contain Ipswich Town


def preprocess_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Preprocesses raw data for model input"""
    ###### Encoding ####################
    # Encode categorical features
    team_encoder = fit_team_name_encoder(df)
    save_encoder_to_file(team_encoder, filepath=TEAM_ENCODER_FILEPATH)
    df = encode_team_name_features(df, encoder=team_encoder)

    # Encoding Venue
    venue_encoder = fit_venue_encoder(df)
    save_encoder_to_file(venue_encoder, filepath=VENUE_ENCODER_FILEPATH)
    df = encode_venue_name_feature(df, encoder=venue_encoder)

    # Feature engineering
    df = encode_day_of_week(df)
    df = split_score_column(df)
    df = calculate_result(df)
    df = add_season_column(df)
    df = encode_season_column(df)
    df = add_hour_feature(df)
    df = add_rolling_shooting_stats(df, SHOOTING_TRAINING_DATA_DIR, teams)
    df = calculate_match_points(df)
    df = add_ppg_features(df, teams)

    # Cleaning up Rolling Home Columns
    df.loc[df.isna().any(axis=1), rolling_home_cols] = (
        0  # Luton Town had their third game in Week 4 of 2023-24 season
    )

    # Define features and labels    
    features = FEATURES
    labels = ["FTHG", "FTAG"]

    X = df[features]
    y = df[labels]  # Predicting home and away goals

    # Scaling features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    return X, y


def train_pipeline():
    # Load data
    df = load_training_data(FIXTURES_TRAINING_DATA_DIR)
    df = clean_data(df)
    X, y = preprocess_data(df)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Save model
    save_model(model, "random_forest_model.pkl", SAVED_MODELS_DIRECTORY)


def train_model():
    logger = logging.getLogger(__name__)
    logger.info("Starting training pipeline...")
    train_pipeline()
    logger.info("Training complete. Model saved.")
    return {"status": "success", "message": "Model trained and saved."}


if __name__ == "__main__":
    train_pipeline()
