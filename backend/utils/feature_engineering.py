
from typing import Tuple
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder


def encode_team_name_features(df: pd.DataFrame, encoder: LabelEncoder) -> Tuple[pd.DataFrame, LabelEncoder]:
    # ...existing code for encoding...
    all_teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
    all_teams = np.append(all_teams, 'Ipswich Town') # Adding team since it was promoted

    encoder.fit(all_teams)
    df['HomeTeamEncoded'] = encoder.transform(df['HomeTeam'])
    df['AwayTeamEncoded'] = encoder.transform(df['AwayTeam'])
    return df, encoder


def encode_venue_name_feature(df: pd.DataFrame, encoder: LabelEncoder) -> Tuple[pd.DataFrame, LabelEncoder]:
    venues = df['Venue'].unique()
    venues = np.append(venues, 'Portman Road Stadium') # Adding new stadiums
    # print(f"The stadiums: \n {venues}")
    encoder.fit(venues)
    df['venue_code'] = encoder.transform(df['Venue'])
    return df, encoder


def save_encoder_to_file(encoder: LabelEncoder, filepath: str):
    with open(filepath, 'wb') as file:
        pickle.dump(encoder, file)


def calculate_rolling_stats(df, teams):
    # ...existing code for rolling stats...
    return df


def calculate_points(row):
    """Function to calculate points for each team in each game"""
    if row['FTHG'] > row['FTAG']:  # Home team wins
        row['HomePoints'] = 3
        row['AwayPoints'] = 0
    elif row['FTHG'] < row['FTAG']:  # Away team wins
        row['HomePoints'] = 0
        row['AwayPoints'] = 3
    else:  # Draw
        row['HomePoints'] = 1
        row['AwayPoints'] = 1
    return row
