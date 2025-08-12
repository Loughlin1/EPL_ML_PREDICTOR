"""
backend/app/services/models/predict.py
"""
import json
import logging

import pandas as pd
from sklearn.preprocessing import StandardScaler

from ...core.paths import (
    TEAM_ENCODER_FILEPATH,
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
    calculate_match_points,
)
from .config import FEATURES, LABELS
from .save_load import load_model
from ...db.queries import get_teams_names


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the data for model input
    Args:
        df (pd.DataFrame): Input data to be preprocessed
    Returns:
       X (pd.DataFrame): Preprocessed data
    """
    teams = get_teams_names()

    ###### Encoding ####################
    # Encode categorical features
    ## Encoding team name
    df = encode_team_name_features(df, encoder=load_encoder_file(TEAM_ENCODER_FILEPATH))
    df = encode_venue_name_feature(
        df, encoder=load_encoder_file(VENUE_ENCODER_FILEPATH)
    )
    # Feature engineering
    df = encode_day_of_week(df)
    df = encode_season_column(df)
    df = add_hour_feature(df)
    df = add_rolling_shooting_stats(df, teams)
    df = calculate_match_points(df)
    df = add_ppg_features(df, teams)

    X = df[FEATURES]

    assert not X.isnull().any().any(), "Data contains NaNs"
    assert len(X) > 0, "DataFrame is empty"

    # Scaling features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    return X


def predict(input_data: pd.DataFrame):
    """Generates predictions for matches based on the model and inputs"""
    # Load model
    model = load_model("random_forest_model.pkl", SAVED_MODELS_DIRECTORY)
    # Preprocess input data
    input_data = clean_data(input_data)
    X = preprocess_data(input_data)

    # Predictions
    predictions = model.predict(X)
    return predictions


def add_predictions_to_input_data(input_data: pd.DataFrame, predictions):
    future_scores = predictions.astype(int)
    input_data["PredScore"] = [f"{h}–{a}" for h, a in future_scores]
    input_data[["PredFTHG", "PredFTAG"]] = (
        input_data["PredScore"].str.split("–", expand=True).astype(int)
    )
    input_data["PredResult"] = [
        "H" if h > a else "D" if h == a else "A" for h, a in future_scores
    ]
    return input_data


def get_predictions(input_data: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """Returns the input DataFrame with the predictions in the columns."""
    logger.debug("Model Input:")
    logger.debug(input_data.head())
    predictions = predict(input_data)

    df = add_predictions_to_input_data(input_data, predictions)
    logger.debug("\n DataFrame after the model: \n")
    logger.debug(df.info())
    return df
