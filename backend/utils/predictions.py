

import os
import json
import pickle

from .data_processing import merge_rolling_stats, calculate_result, add_ppg_features
from .feature_engineering import calculate_points

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

teams_2024 = json.load(open(f"{parent_dir}/Encoders/teams_2024.json"))
VENUE_ENCODER_FILEPATH = f'{parent_dir}/Encoders/venue_encoder.pkl'
TEAM_ENCODER_FILEPATH = f'{parent_dir}/Encoders/team_encoder.pkl'

def load_model(model_path: str):
    # Loads a machine learning model from a file
    with open(model_path, "rb") as file:
        model = pickle.load(file)
    return model


def make_prediction(model, input_data):
    # Generates predictions using the loaded model
    # ...existing code...
    ...


def get_predictions(future_matches: pd.DataFrame) -> pd.DataFrame:
    """Generates predictions for future matches based on the trained model and input features."""
    
    ## Cleaning matches to predict
    future_matches['Date'] = pd.to_datetime(future_matches['Date'], format="%Y-%m-%d")
    future_matches.dropna(subset=['Date'], inplace=True)
    future_matches.dropna(subset=['Date'], inplace=True) 

    future_matches['Wk'] = future_matches['Wk'].astype(int)

    ### Encoding features
    # Loading team encoder from file
    with open(TEAM_ENCODER_FILEPATH, 'rb') as file:
        loaded_encoder = pickle.load(file)
    
    # Transform using the loaded encoder
    future_matches['HomeTeam'] = future_matches['Home']
    future_matches['AwayTeam'] = future_matches['Away']
    future_matches['HomeTeamEncoded'] = loaded_encoder.transform(future_matches['Home'])
    future_matches['AwayTeamEncoded'] = loaded_encoder.transform(future_matches['Away'])

    # Loading venue encoder from file
    with open(VENUE_ENCODER_FILEPATH, 'rb') as file:
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
    data_base_filepath = f'{parent_dir}/data/shooting_data_2024'
    rolling_df = merge_rolling_stats(teams_2024)
    future_matches = pd.merge(future_matches, rolling_df, how="left", on=["Day","Date", "Time", "HomeTeam", "AwayTeam"], suffixes=('','_y') )
   
    future_matches['season'] = '2024/25'
    future_matches['season_encoded'] = 11

    # Extracting the scores
    future_matches[['FTHG', 'FTAG']] = future_matches['Score'].str.extract(r'(\d+)[^\d]+(\d+)').astype('Int64')
    # Compute Result
    future_matches['Result'] = future_matches.apply(calculate_result, axis=1)
    # Adding PPG (form) features
    future_matches.apply(calculate_points, axis=1) # Apply the points calculation to each row
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