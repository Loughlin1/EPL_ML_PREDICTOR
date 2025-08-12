import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def fit_team_name_encoder(df: pd.DataFrame) -> LabelEncoder:
    team_encoder = LabelEncoder()
    all_teams = pd.concat([df["home_team"], df["away_team"]]).unique()
    all_teams = np.append(
        all_teams, "Ipswich Town"
    )  # Adding team since it was promoted
    team_encoder.fit(all_teams)
    return team_encoder


def encode_team_name_features(df: pd.DataFrame, encoder: LabelEncoder) -> pd.DataFrame:
    df["home_team_encoded"] = encoder.transform(df["home_team"])
    df["away_team_encoded"] = encoder.transform(df["away_team"])
    return df


def fit_venue_encoder(df: pd.DataFrame) -> LabelEncoder:
    venue_encoder = LabelEncoder()
    venues = df["venue"].unique()
    venues = np.append(venues, "Portman Road Stadium")  # Adding new stadiums
    # print(f"The stadiums: \n {venues}")
    venue_encoder.fit(venues)
    return venue_encoder


def encode_venue_name_feature(df: pd.DataFrame, encoder: LabelEncoder) -> pd.DataFrame:
    # Cleaning up mismatches and changes in Stadium names before encoding
    venue_replacements = {
        "The American Express Stadium": "The American Express Community Stadium",
        "St Mary's Stadium": "St. Mary's Stadium",
    }
    df["venue"] = df["venue"].replace(venue_replacements)
    df["venue_code"] = encoder.transform(df["venue"])
    return df


def load_encoder_file(filepath: str):
    with open(filepath, "rb") as file:
        return pickle.load(file)


def save_encoder_to_file(encoder: LabelEncoder, filepath: str) -> None:
    with open(filepath, "wb") as file:
        pickle.dump(encoder, file)


def encode_season_column(df: pd.DataFrame) -> pd.DataFrame:
    df["season_encoded"] = df["season"].rank(method="dense").astype(int)
    return df


def encode_day_of_week(df: pd.DataFrame) -> pd.DataFrame:
    df["day_code"] = df["date"].dt.dayofweek  # code e.g. Mon = 0, Tues = 2, ...
    return df
