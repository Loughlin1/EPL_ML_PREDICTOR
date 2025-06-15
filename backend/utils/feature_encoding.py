import pickle

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def fit_team_name_encoder(df: pd.DataFrame) -> LabelEncoder:
    team_encoder = LabelEncoder()
    all_teams = pd.concat([df["HomeTeam"], df["AwayTeam"]]).unique()
    all_teams = np.append(
        all_teams, "Ipswich Town"
    )  # Adding team since it was promoted
    team_encoder.fit(all_teams)
    return team_encoder


def encode_team_name_features(df: pd.DataFrame, encoder: LabelEncoder) -> pd.DataFrame:
    df["HomeTeamEncoded"] = encoder.transform(df["HomeTeam"])
    df["AwayTeamEncoded"] = encoder.transform(df["AwayTeam"])
    return df


def fit_venue_encoder(df: pd.DataFrame) -> LabelEncoder:
    venue_encoder = LabelEncoder()
    venues = df["Venue"].unique()
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
    df["Venue"] = df["Venue"].replace(venue_replacements)
    df["venue_code"] = encoder.transform(df["Venue"])
    return df


def save_encoder_to_file(encoder: LabelEncoder, filepath: str) -> None:
    with open(filepath, "wb") as file:
        pickle.dump(encoder, file)


def encode_season_column(df: pd.DataFrame) -> pd.DataFrame:
    df["season_encoded"] = df["Season"].rank(method="dense").astype(int)
    return df


def encode_day_of_week(df: pd.DataFrame) -> pd.DataFrame:
    df["day_code"] = df[
        "Date"
    ].dt.dayofweek  # Gives each day of the week a code e.g. Mon = 0, Tues = 2, ....
    return df
