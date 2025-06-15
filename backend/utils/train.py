"""
train.py

This script performs data loading, cleaning, feature engineering, encoding, and model training for predicting 
full-time home and away goals in English Premier League matches using a RandomForestRegressor.

Functions:
    - rolling_stats(df, team_name): Calculates rolling averages for shooting statistics for a given team.
    - merge_rolling_stats(teams): Merges rolling statistics for all teams into a single DataFrame.
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
    encode_team_name_features,
    encode_venue_name_feature,
    save_encoder_to_file,
    calculate_rolling_stats,
    calculate_match_points
)
from backend.utils.data_processing import load_data, clean_data, merge_rolling_stats
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

df = load_data(file_paths)

########### Data Cleaning #############
df = clean_data(df)


### Adding Features
df[['FTHG', 'FTAG']] = df['Score'].str.split('–', expand=True).astype(int)  # Full-Time Home Goals and Full-Time Away Goals
conditions = [df['FTHG'] > df['FTAG'], df['FTHG'] < df['FTAG']]
df['Result'] = np.select(conditions, choicelist=['W', 'L'], default='D')

# Calculate the season year based on the start month
season_start_month = 8  # # Define the start month of the season: August
df['Season'] = df['Date'].apply(lambda x: x.year if x.month >= season_start_month else x.year - 1)

# Convert the season year to a format like '2023/24'
df['Season'] = df['Season'].astype(str) + '/' + (df['Season'] + 1).astype(str).str[2:]

####################################


###### Encoding ####################
# Encode categorical features
team_encoder = LabelEncoder()
df, encoder = encode_team_name_features(df, team_encoder)
save_encoder_to_file(team_encoder, filepath=TEAM_ENCODER_FILEPATH)

# Encoding Venue
venue_encoder = LabelEncoder()
df, venue_encoder = encode_venue_name_feature(df, venue_encoder)
save_encoder_to_file(venue_encoder, filepath=VENUE_ENCODER_FILEPATH)

# Encoding day and hour
df["hour"] = df["Time"].str.replace(":+", "", regex=True).astype("int")  # Time that matches play may be a factor - regex to reformat from "hh:mm" to "hh"
df["day_code"] = df["Date"].dt.dayofweek # Gives each day of the week a code e.g. Mon = 0, Tues = 2, ....
df['season_encoded'] = df['Season'].rank(method='dense').astype(int)

#######################################################

####### Rolling Avg Shooting Stats ####################

teams = json.load(open(TEAMS_TRAINING_FILEPATH)) # Doesn't contain Ipswich Town

def rolling_stats(df, team_name):
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


rolling_df = merge_rolling_stats(
    data_base_filepath=SHOOTING_TRAINING_DATA_DIR, teams=teams
)
result = pd.merge(df, rolling_df, how="left", on=["Day","Date", "Time", "HomeTeam", "AwayTeam"], suffixes=('','_y') )

df = result
columns_with_nan = df.columns[df.isna().any()].tolist()

#######################################################


df = calculate_match_points(df)

for team in teams.values():
    # Get all the matches of a team
    # Calculate the rolling points per game with a window of 3 games
    team_df = df[(df['HomeTeam'] == team)|(df['AwayTeam'] == team)].copy()
    team_df['Points'] = team_df['HomePoints'].where(team_df['HomeTeam'] == team, team_df['AwayPoints'])
    team_df['PPG_rolling'] = team_df['Points'].rolling(3, closed='left').mean().fillna(0)
    
    team_df.loc[:, 'Points'] = df['HomePoints'].where(df['HomeTeam'] == team, df['AwayPoints'])
    df.loc[df['HomeTeam'] == team, 'PPG_rolling_h'] = team_df.loc[team_df['HomeTeam'] == team, 'PPG_rolling']
    df.loc[df['AwayTeam'] == team, 'PPG_rolling_a'] = team_df.loc[team_df['AwayTeam'] == team, 'PPG_rolling']

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
