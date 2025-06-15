"""
train.py

This script performs data loading, cleaning, feature engineering, encoding, and model training for predicting 
full-time home and away goals in English Premier League matches using a RandomForestRegressor.

Functions:
    - rolling_stats(df, team_name): Calculates rolling averages for shooting statistics for a given team.
    - creates_rolling_stats(teams): Creates rolling statistics for all teams into a single DataFrame.
    - calculate_points(row): Calculates points for each team in each game based on the match result.
Workflow:
    1. Load match data from CSV files.
    2. Clean and preprocess the data.
    3. Add new features such as full-time goals, match result, season year, and encoded categorical variables.
    4. Calculate rolling averages for shooting statistics and points per game.
    5. Prepare features and labels for model training.
    6. Scale the features.
    7. Split the data into training and testing sets.
    8. Train a RandomForestRegressor model and make predictions on the test set.
"""
import json
import pandas as pd
import numpy as np

from sklearn.preprocessing import LabelEncoder

from backend.utils.feature_engineering import (
    fit_team_name_encoder,
    fit_venue_encoder,
    encode_team_name_features,
    encode_venue_name_feature,
    save_encoder_to_file,
    calculate_result,
    calculate_match_points,
    split_score_column,
    add_season_column,
    create_rolling_stats,
    add_rolling_stats,
    add_ppg_features,
    encode_season_column,
    add_hour_feature,
    encode_day_of_week
)
from backend.utils.data_processing import load_training_data, clean_data
from backend.utils.model_training import train_model
from backend.config import (
    TEAMS_TRAINING_FILEPATH,
    TEAM_ENCODER_FILEPATH,
    VENUE_ENCODER_FILEPATH,
    SHOOTING_TRAINING_DATA_DIR
)

########### Loading the Data #############
file_paths = ['2014-15.csv', '2015-16.csv', '2016-17.csv','2017-18.csv', '2018-19.csv', '2019-20.csv', '2020-21.csv', '2021-22.csv', '2022-23.csv', '2023-24.csv']
# headers = ['Day', 'Date', 'Time', 'HomeTeam', 'HomeOdds', 'Score', 'AwayOdds', 'AwayTeam', 'Attendance', 'Stadium', 'Referee', 'Report']

df = load_training_data(file_paths)

########### Data Cleaning #############
df = clean_data(df)

### Adding Features
df = split_score_column(df)  # Reuse the new function
df = calculate_result(df)
df = add_season_column(df)
df = add_hour_feature(df)

####################################


###### Encoding ####################
# Encode categorical features
team_encoder = fit_team_name_encoder(df)
df = encode_team_name_features(df, encoder=team_encoder)
save_encoder_to_file(team_encoder, filepath=TEAM_ENCODER_FILEPATH)

# Encoding Venue
venue_encoder = fit_venue_encoder(df)
df = encode_venue_name_feature(df, encoder=venue_encoder)
save_encoder_to_file(venue_encoder, filepath=VENUE_ENCODER_FILEPATH)

# Encoding day and hour
df = encode_day_of_week(df)
df = encode_season_column(df)
#######################################################

teams = json.load(open(TEAMS_TRAINING_FILEPATH)) # Doesn't contain Ipswich Town

rolling_df = create_rolling_stats(SHOOTING_TRAINING_DATA_DIR, teams=teams)
df = add_rolling_stats(df, rolling_df)
columns_with_nan = df.columns[df.isna().any()].tolist()

df = calculate_match_points(df)
df = add_ppg_features(df, teams)

##########################################################################################


####### Features and Labels ###########################
# Features and labels
cols = ["GF", "GA", "Sh", "SoT", "PK","PKatt"]
rolling_home_cols = [f"{c}_rolling_h" for c in cols]
rolling_away_cols = [f"{c}_rolling_a" for c in cols]

features = ['HomeTeamEncoded', 'AwayTeamEncoded', 'Wk', 'hour', 'day_code', 'venue_code', 'season_encoded', 'PPG_rolling_h', 'PPG_rolling_a']
features.extend(rolling_home_cols)
features.extend(rolling_away_cols)
print(f"Features are \n {features}")

labels = ['FTHG', 'FTAG']
X = df[features]
y = df[labels]  # Predicting home and away goals

X.loc[X.isna().any(axis=1),rolling_home_cols] = 0 # Luton Town had their third game in Week 4 of 2023-24 season

model, y_pred = train_model(X, y)
