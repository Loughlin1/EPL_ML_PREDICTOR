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
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ...core.paths import (
    TEAM_ENCODER_FILEPATH,
    VENUE_ENCODER_FILEPATH,
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
    calculate_match_points,
)
from ..models.save_load import save_model
from ..models.config import FEATURES, LABELS, rolling_home_cols
from ...db.queries import get_teams_names


def preprocess_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Preprocesses raw data for model input"""
    teams = get_teams_names()

    ###### Encoding ####################
    # Encode categorical features
    ## Encoding team name
    team_encoder = fit_team_name_encoder(df)
    save_encoder_to_file(team_encoder, filepath=TEAM_ENCODER_FILEPATH)
    df = encode_team_name_features(df, encoder=team_encoder)

    ## Encoding venue
    venue_encoder = fit_venue_encoder(df)
    save_encoder_to_file(venue_encoder, filepath=VENUE_ENCODER_FILEPATH)
    df = encode_venue_name_feature(df, encoder=venue_encoder)

    # Feature engineering
    df = encode_day_of_week(df)
    df = encode_season_column(df)
    df = add_hour_feature(df)
    df = add_rolling_shooting_stats(df, teams)
    df = calculate_match_points(df)
    df = add_ppg_features(df, teams)

    # Cleaning up Rolling Home Columns
    df.loc[
        df.isna().any(axis=1), rolling_home_cols
    ] = 0  # Luton Town had their third game in Week 4 of 2023-24 season

    # Define features and labels
    features = FEATURES
    labels = LABELS

    X = df[features]
    y = df[labels]

    assert not X.isnull().any().any(), "Data contains NaNs"
    assert len(X) > 0, "DataFrame is empty"

    return X, y


def train_pipeline():
    # Load data
    df = load_training_data()
    df = clean_data(df)
    X, y = preprocess_data(df)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    # Scaling features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

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
