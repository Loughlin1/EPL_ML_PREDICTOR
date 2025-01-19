"""
Predictor Module
This module provides functions to generate predictions for football matches based on historical data and machine learning models.
Functions:
    rolling_stats(df, team_name):
        Creates rolling averages statistics for a given team's dataframe.
    merge_rolling_stats(teams):
        Merges rolling statistics for all teams into a single dataframe.
    calculate_points(row):
        Calculates points for each team in each game based on the match result.
    add_ppg_features(df, teams):
        Adds points per game (PPG) features to the dataframe for each team.
    get_predictions(future_matches):
        Generates predictions for future matches based on the trained model and input features.
"""
import os
import sys
import pandas as pd
import numpy as np
import pickle
import json
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

from utils.Train import model, features, labels

##### Prediction #####################################

def rolling_stats(df, team_name):
    """Creates rolling averages statistics"""
    df.dropna(subset=['Date'], inplace=True) 

    # Getting rolling averages
    cols = ["GF", "GA", "Sh", "SoT", "PK","PKatt"]
    new_cols = [f"{c}_rolling" for c in cols]
    rolling_stats = df[cols].rolling(3, closed='left').mean()
    df[new_cols] = rolling_stats
    # df = df.dropna(subset=new_cols)

    df.loc[df['Venue'] == 'Home', 'HomeTeam'] = team_name
    df.loc[df['Venue'] == 'Home', 'AwayTeam'] = df['Opponent']
    df.loc[df['Venue'] == 'Away', 'HomeTeam'] = df['Opponent']
    df.loc[df['Venue'] == 'Away', 'AwayTeam'] = team_name
    df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")
    
    # Check if 'Venue' column has correct entries
    if 'Home' not in df['Venue'].unique() or 'Away' not in df['Venue'].unique():
        print("Error: 'Venue' column does not contain expected values.")
        return df
    
    rolling_home_cols = [f"{c}_rolling_h" for c in cols]
    rolling_away_cols = [f"{c}_rolling_a" for c in cols]

    df.loc[df['Venue'] == 'Home', rolling_home_cols] = df.loc[df['Venue'] == 'Home', new_cols].values
    df.loc[df['Venue'] == 'Away', rolling_away_cols] = df.loc[df['Venue'] == 'Away', new_cols].values

    # Filling in missing rolling away stats with 0 so that they don't add an bias to the stats - form at start of season is unknown
    # First week rolling shooting stats are set at 0 so so that they don't add an bias to the stats - form at start of season is unknown
    if 'Round' in df.columns and df['Round'].dtype == 'object':
        # Extract the numeric part from 'Round' and convert it to an integer
        df['Wk'] = df['Round'].str.extract(r'(\d+)').astype(int)
    else:
        print("Error: 'Round' column is missing or not in the expected format.")

    # Week 1
    df.loc[(df['Wk']==1) & (df['Venue'] == 'Home'), rolling_home_cols] = 0
    df.loc[(df['Wk']==1) & (df['Venue'] == 'Away'), rolling_away_cols] = 0

    # Week 2 - set at the last week's stats
    df.loc[(df['Wk']==2) & (df['Venue'] == 'Home'), rolling_home_cols] = 0
    df.loc[(df['Wk']==2) & (df['Venue'] == 'Away'), rolling_away_cols] = 0
   
    # Week 3
    df.loc[(df['Wk']==3) & (df['Venue'] == 'Home'), rolling_home_cols] = 0
    df.loc[(df['Wk']==3) & (df['Venue'] == 'Away'), rolling_away_cols] = 0

    return df

def merge_rolling_stats(teams):
    rolling_dfs = []
    for team in teams:
        df = pd.read_csv(f'{parent_dir}/data/shooting_data_2024/'+ team + '.csv')
        rolling_df = rolling_stats(df, teams[team])
        rolling_dfs.append(rolling_df)

    combined_df = pd.concat(rolling_dfs, ignore_index=False)
    merged_df = combined_df.groupby(['Date', 'HomeTeam', 'AwayTeam'], as_index=False).first()
    # merged_df = merged_df.drop(['G-xG', 'npxG', 'npxG/Sh', 'np:G-xG', 'xG', 'Match Report', 'Match Report.1'], axis=1)

    return merged_df

teams_2024 = json.load(open(f"{parent_dir}/Encoders/teams_2024.json"))
rolling_df = merge_rolling_stats(teams_2024)
rolling_df.head()

def calculate_points(df):
    """Function to calculate points for each team in each game"""
    df.loc[pd.isna(df['FTHG']) | pd.isna(df['FTAG']), ['HomePoints', 'AwayPoints']] = None
    df.loc[df['FTHG'] > df['FTAG'], ['HomePoints', 'AwayPoints']] = [3, 0]  # Home team wins
    df.loc[df['FTHG'] < df['FTAG'], ['HomePoints', 'AwayPoints']] = [0, 3]  # Away team wins
    df.loc[df['FTHG'] == df['FTAG'], ['HomePoints', 'AwayPoints']] = [1, 1]  # Draw
    return df


def add_ppg_features(df, teams):
    for team in teams.values():
        # Get all the matches of a team
        # Calculate the rolling points per game with a window of 3 games
        team_df = df[(df['HomeTeam'] == team)|(df['AwayTeam'] == team)].copy()
        team_df['Points'] = team_df['HomePoints'].where(team_df['HomeTeam'] == team, team_df['AwayPoints'])
        team_df['PPG_rolling'] = team_df['Points'].rolling(3, closed='left').mean().fillna(0)
        
        team_df.loc[:, 'Points'] = df['HomePoints'].where(df['HomeTeam'] == team, df['AwayPoints'])
        df.loc[df['HomeTeam'] == team, 'PPG_rolling_h'] = team_df.loc[team_df['HomeTeam'] == team, 'PPG_rolling']
        df.loc[df['AwayTeam'] == team, 'PPG_rolling_a'] = team_df.loc[team_df['AwayTeam'] == team, 'PPG_rolling']
        
    return df


def calculate_result(row):
    """Determines the result of a match based on the full-time goals."""
    if pd.isna(row['FTHG']) or pd.isna(row['FTAG']):
        return None  # Return NaN if either column is NaN
    elif row['FTHG'] > row['FTAG']:
        return 'W'  # Win
    elif row['FTHG'] < row['FTAG']:
        return 'L'  # Loss
    else:
        return 'D'  # Draw


def get_predictions(future_matches: pd.DataFrame) -> pd.DataFrame:
    ''' Function to get predictions from a dataframe'''
    
    ## Cleaning matches to predict
    future_matches['Date'] = pd.to_datetime(future_matches['Date'], format="%Y-%m-%d")
    future_matches.dropna(subset=['Date'], inplace=True)
    future_matches.dropna(subset=['Date'], inplace=True) 

    future_matches['Wk'] = future_matches['Wk'].astype(int)

    ### Encoding features
    # Loading team encoder from file
    with open(f'{parent_dir}/Encoders/team_encoder.pkl', 'rb') as file:
        loaded_encoder = pickle.load(file)
    
    # Transform using the loaded encoder
    future_matches['HomeTeam'] = future_matches['Home']
    future_matches['AwayTeam'] = future_matches['Away']
    future_matches['HomeTeamEncoded'] = loaded_encoder.transform(future_matches['Home'])
    future_matches['AwayTeamEncoded'] = loaded_encoder.transform(future_matches['Away'])

    # Loading venue encoder from file
    with open(f'{parent_dir}/Encoders/venue_encoder.pkl', 'rb') as file:
        venue_encoder = pickle.load(file)

    # Cleaning up mismatches and changes in Stadium names before encoding
    venue_replacements = {
        'The American Express Stadium': 'The American Express Community Stadium',
        "St Mary's Stadium": "St. Mary's Stadium"
    }
    future_matches['Venue'] = future_matches['Venue'].replace(venue_replacements)
    future_matches['venue_code'] = venue_encoder.transform(future_matches['Venue']) # Transform using the loaded encoder

    # Encoding day and hour
    future_matches["hour"] = future_matches["Time"].fillna('00').str[:2].astype(float)
    future_matches["day_code"] = future_matches["Date"].dt.dayofweek # Gives each day of the week a code e.g. Mon = 0, Tues = 2, ....

    # Merge with rolling stats
    rolling_df = merge_rolling_stats(teams_2024)
    future_matches = pd.merge(future_matches, rolling_df, how="left", on=["Day","Date", "Time", "HomeTeam", "AwayTeam"], suffixes=('','_y') )
   
    future_matches['season'] = '2024/25'
    future_matches['season_encoded'] = 11

    # Extracting the scores
    future_matches[['FTHG', 'FTAG']] = future_matches['Score'].str.extract(r'(\d+)[^\d]+(\d+)').astype('Int64')
    # Compute Result
    future_matches['Result'] = future_matches.apply(calculate_result, axis=1)
    # Adding PPG (form) features
    future_matches = calculate_points(future_matches)  # Apply the points calculation to the dataframe
    future_matches = add_ppg_features(future_matches, teams_2024)

    # Features
    X = future_matches[features]
    print("\n Features going into the model are: \n")
    print(X.info())
    # y = future_matches[labels]  # Predicting home and away goals

    future_scores = model.predict(X)
    future_scores = future_scores.astype(int)
    future_matches['PredScore'] = [f"{h}–{a}" for h,a in future_scores]
    future_matches[['PredFTHG', 'PredFTAG']] = future_matches['PredScore'].str.split('–', expand=True).astype(int)

    future_matches['PredResult'] = [
        "W" if h > a else "D" if h == a else "L"
            for h, a in future_scores
    ]
    # print("\n DataFrame after the model: \n")
    # print(future_matches.info())
    return future_matches