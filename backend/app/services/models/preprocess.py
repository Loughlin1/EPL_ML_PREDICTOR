from ..data_processing.feature_encoding import (
    encode_day_of_week,
    encode_season_column,
    encode_team_name_features,
    encode_venue_name_feature,
    fit_team_name_encoder,
    fit_venue_encoder,
    save_encoder_to_file,
    load_encoder_file,
)
from ..data_processing.feature_engineering import (
    add_hour_feature,
    add_ppg_features,
    add_rolling_shooting_stats,
    calculate_match_points,
    add_previous_season_rank,
    add_elo_ratings,
    add_h2h_features,
)
from ...core.paths import (
    TEAM_ENCODER_FILEPATH,
    VENUE_ENCODER_FILEPATH,
)
from ...db.queries import get_teams_names

import pandas as pd


def preprocess_data(df: pd.DataFrame, test_data: bool = True) -> pd.DataFrame:
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
    if test_data:
        # Load encoders
        team_encoder = load_encoder_file(TEAM_ENCODER_FILEPATH)
        venue_encoder = load_encoder_file(VENUE_ENCODER_FILEPATH)
    else:
        # Fit encoders
        team_encoder = fit_team_name_encoder(df)
        venue_encoder = fit_venue_encoder(df)
        save_encoder_to_file(team_encoder, filepath=TEAM_ENCODER_FILEPATH)
        save_encoder_to_file(venue_encoder, filepath=VENUE_ENCODER_FILEPATH)
    
    df = encode_team_name_features(df, encoder=team_encoder)
    df = encode_venue_name_feature(df, encoder=venue_encoder)

    # Feature engineering
    df = encode_day_of_week(df)
    df = encode_season_column(df)
    df = add_hour_feature(df)
    df = add_rolling_shooting_stats(df, teams)
    df = calculate_match_points(df)
    df = add_ppg_features(df, teams)
    df = add_previous_season_rank(df)
    df = add_elo_ratings(df)
    df = add_h2h_features(df)

    return df


def check_data(X: pd.DataFrame):
    if X.isnull().any().any():
        nan_cols = X.columns[X.isnull().any()]
        nan_rows = X.loc[:, nan_cols][X[nan_cols].isnull().any(axis=1)]
        raise AssertionError(
            f"Data contains NaNs in columns: {list(nan_cols)}\n"
            f"Rows with NaNs:\n{nan_rows}\n"
            f"Head:\n{X.head()}\n"
        )
    assert len(X) > 0, "DataFrame is empty"
