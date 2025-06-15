"""
train.py

This script performs
    - data loading, cleaning, feature engineering, encoding, and model training

for predicting full-time home and away goals in English Premier League matches
using a RandomForestRegressor.

Workflow:
    1. Load match data from CSV files.
    2. Clean and preprocess the data.
    3. Add new features such as full-time goals, match result, season year, etc.
    4. Calculate rolling averages for shooting statistics and points per game.
    5. Prepare features and labels for model training.
    6. Scale the features.
    7. Split the data into training and testing sets.
    8. Train a RandomForestRegressor model and make predictions on the test set.
"""

import json

from backend.config import (
    SHOOTING_TRAINING_DATA_DIR,
    TEAM_ENCODER_FILEPATH,
    TEAMS_TRAINING_FILEPATH,
    VENUE_ENCODER_FILEPATH,
)
from backend.utils.data_processing import clean_data, load_training_data
from backend.utils.feature_encoding import (
    encode_day_of_week,
    encode_season_column,
    encode_team_name_features,
    encode_venue_name_feature,
    fit_team_name_encoder,
    fit_venue_encoder,
    save_encoder_to_file,
)
from backend.utils.feature_engineering import (
    add_hour_feature,
    add_ppg_features,
    add_rolling_stats,
    add_season_column,
    calculate_match_points,
    calculate_result,
    create_rolling_stats,
    split_score_column,
)
from backend.utils.model_training import train_model

########### Loading the Data #############
df = load_training_data()

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

teams = json.load(open(TEAMS_TRAINING_FILEPATH))  # Doesn't contain Ipswich Town

rolling_df = create_rolling_stats(SHOOTING_TRAINING_DATA_DIR, teams=teams)
df = add_rolling_stats(df, rolling_df)
columns_with_nan = df.columns[df.isna().any()].tolist()

df = calculate_match_points(df)
df = add_ppg_features(df, teams)

##########################################################################################


####### Features and Labels ###########################
# Features and labels
cols = ["GF", "GA", "Sh", "SoT", "PK", "PKatt"]
rolling_home_cols = [f"{c}_rolling_h" for c in cols]
rolling_away_cols = [f"{c}_rolling_a" for c in cols]

features = [
    "HomeTeamEncoded",
    "AwayTeamEncoded",
    "Wk",
    "hour",
    "day_code",
    "venue_code",
    "season_encoded",
    "PPG_rolling_h",
    "PPG_rolling_a",
]
features.extend(rolling_home_cols)
features.extend(rolling_away_cols)
print(f"Features are \n {features}")

labels = ["FTHG", "FTAG"]
X = df[features]
y = df[labels]  # Predicting home and away goals

X.loc[X.isna().any(axis=1), rolling_home_cols] = (
    0  # Luton Town had their third game in Week 4 of 2023-24 season
)

model, y_pred = train_model(X, y)
