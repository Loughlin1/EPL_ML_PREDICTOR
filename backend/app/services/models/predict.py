"""
backend/app/services/models/predict.py
"""
import json
import logging

import pandas as pd
from sklearn.preprocessing import StandardScaler

from ...core.paths import (
    SHOOTING_TEST_DATA_DIR,
    TEAM_ENCODER_FILEPATH,
    TEAMS_2024_FILEPATH,
    VENUE_ENCODER_FILEPATH,
    SAVED_MODELS_DIRECTORY,
)
from ..data_processing.data_loader import clean_data
from ..data_processing.feature_encoding import (
    encode_day_of_week,
    encode_season_column,
    encode_team_name_features,
    encode_venue_name_feature,
    load_encoder_file,
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
from .config import FEATURES
from .save_load import load_model

with open(TEAMS_2024_FILEPATH, "r") as f:
    teams_2024 = json.load(f)


def predict(input_data: pd.DataFrame):
    """Generates predictions for matches based on the model and inputs"""
    # Load model
    model = load_model("random_forest_model.pkl", SAVED_MODELS_DIRECTORY)

    # Preprocess input data
    input_data = clean_data(input_data)
    input_data.dropna(subset=["Date"], inplace=True)
    input_data = encode_team_name_features(
        input_data, encoder=load_encoder_file(TEAM_ENCODER_FILEPATH)
    )
    input_data = encode_venue_name_feature(
        input_data, encoder=load_encoder_file(VENUE_ENCODER_FILEPATH)
    )

    # Feature engineering
    input_data = encode_day_of_week(input_data)
    input_data = split_score_column(input_data)
    input_data = calculate_result(input_data)
    input_data = add_season_column(input_data)
    input_data = encode_season_column(input_data)
    input_data = add_hour_feature(input_data)
    input_data = add_rolling_shooting_stats(
        input_data, SHOOTING_TEST_DATA_DIR, teams_2024
    )
    input_data = calculate_match_points(input_data)
    input_data = add_ppg_features(input_data, teams_2024)

    # Define features
    features = FEATURES # defined in config
    X = input_data[features]

    # Scale inputs
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Generate predictions
    predictions = model.predict(X)
    return predictions


def add_predictions_to_input_data(input_data: pd.DataFrame, predictions):
    future_scores = predictions.astype(int)
    input_data["PredScore"] = [f"{h}–{a}" for h, a in future_scores]
    input_data[["PredFTHG", "PredFTAG"]] = (
        input_data["PredScore"].str.split("–", expand=True).astype(int)
    )
    input_data["PredResult"] = [
        "W" if h > a else "D" if h == a else "L" for h, a in future_scores
    ]
    return input_data


def get_predictions(
    input_data: pd.DataFrame, logger: logging.Logger
) -> pd.DataFrame:
    """Returns the input DataFrame with the predictions in the columns."""
    logger.debug("Model Input:")
    logger.debug(input_data.head())
    predictions = predict(input_data)

    df = add_predictions_to_input_data(input_data, predictions)
    # print("\n DataFrame after the model: \n")
    # print(future_matches.info())
    return df
