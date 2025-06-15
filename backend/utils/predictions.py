import json
import logging
import pickle

import pandas as pd

from ..config import (
    SHOOTING_TEST_DATA_DIR,
    TEAM_ENCODER_FILEPATH,
    TEAMS_2024_FILEPATH,
    VENUE_ENCODER_FILEPATH,
)
from .data_processing import clean_data
from .feature_encoding import (
    encode_day_of_week,
    encode_season_column,
    encode_team_name_features,
    encode_venue_name_feature,
)
from .feature_engineering import (
    add_hour_feature,
    add_ppg_features,
    add_rolling_shooting_stats,
    add_season_column,
    calculate_match_points,
    calculate_result,
    create_rolling_shooting_stats,
    split_score_column,
)
from .train import features, model

teams_2024 = json.load(open(TEAMS_2024_FILEPATH))


def load_model(model_path: str):
    # Loads a machine learning model from a file
    with open(model_path, "rb") as file:
        model = pickle.load(file)
    return model


def make_prediction(model, input_data):
    # Generates predictions using the loaded model
    # ...existing code...
    ...


def get_predictions(
    future_matches: pd.DataFrame, logger: logging.Logger
) -> pd.DataFrame:
    """
    Generates predictions for matches based on the model and input features.
    """

    ## Cleaning matches to predict
    logger.debug("future_matches:")
    logger.debug(future_matches.head())
    future_matches = clean_data(future_matches)
    future_matches.dropna(subset=["Date"], inplace=True)

    ### Encoding features
    team_encoder = pickle.load(open(TEAM_ENCODER_FILEPATH, "rb"))
    future_matches = encode_team_name_features(future_matches, encoder=team_encoder)
    venue_encoder = pickle.load(open(VENUE_ENCODER_FILEPATH, "rb"))
    future_matches = encode_venue_name_feature(future_matches, encoder=venue_encoder)

    # Merge with rolling stats
    rolling_df = create_rolling_shooting_stats(SHOOTING_TEST_DATA_DIR, teams_2024)
    future_matches = add_rolling_shooting_stats(future_matches, rolling_df)

    # Adding features
    future_matches = split_score_column(future_matches)
    future_matches = calculate_result(future_matches)
    future_matches = calculate_match_points(future_matches)
    future_matches = add_ppg_features(future_matches, teams_2024)
    future_matches = add_hour_feature(future_matches)
    future_matches = add_season_column(future_matches)
    future_matches = encode_season_column(future_matches)
    future_matches = encode_day_of_week(future_matches)
    # Features
    X = future_matches[features]
    logger.info("\n Features going into the model are: \n")
    logger.info(X.info())
    # y = future_matches[labels]  # Predicting home and away goals

    future_scores = model.predict(X)
    future_scores = future_scores.astype(int)
    future_matches["PredScore"] = [f"{h}–{a}" for h, a in future_scores]
    future_matches[["PredFTHG", "PredFTAG"]] = (
        future_matches["PredScore"].str.split("–", expand=True).astype(int)
    )

    future_matches["PredResult"] = [
        "W" if h > a else "D" if h == a else "L" for h, a in future_scores
    ]
    # print("\n DataFrame after the model: \n")
    # print(future_matches.info())
    return future_matches
