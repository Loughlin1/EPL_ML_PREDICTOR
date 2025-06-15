from typing import Tuple, List
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder


def fit_team_name_encoder(df: pd.DataFrame) -> LabelEncoder:
    team_encoder = LabelEncoder()
    all_teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
    all_teams = np.append(all_teams, 'Ipswich Town') # Adding team since it was promoted
    team_encoder.fit(all_teams)
    return team_encoder


def encode_team_name_features(df: pd.DataFrame, encoder: LabelEncoder) -> pd.DataFrame:
    df['HomeTeamEncoded'] = encoder.transform(df['HomeTeam'])
    df['AwayTeamEncoded'] = encoder.transform(df['AwayTeam'])
    return df


def fit_venue_encoder(df: pd.DataFrame) -> LabelEncoder:
    venue_encoder = LabelEncoder()
    venues = df['Venue'].unique()
    venues = np.append(venues, 'Portman Road Stadium') # Adding new stadiums
    # print(f"The stadiums: \n {venues}")
    venue_encoder.fit(venues)
    return venue_encoder


def encode_venue_name_feature(df: pd.DataFrame, encoder: LabelEncoder) -> pd.DataFrame:
    # Cleaning up mismatches and changes in Stadium names before encoding
    venue_replacements = {
        'The American Express Stadium': 'The American Express Community Stadium',
        "St Mary's Stadium": "St. Mary's Stadium"
    }
    df['Venue'] = df['Venue'].replace(venue_replacements)
    df['venue_code'] = encoder.transform(df['Venue'])
    return df


def save_encoder_to_file(encoder: LabelEncoder, filepath: str) -> None:
    with open(filepath, 'wb') as file:
        pickle.dump(encoder, file)


def calculate_match_points(df: pd.DataFrame) -> pd.DataFrame:
    """Function to calculate points for each team in each game"""
    df.loc[pd.isna(df['FTHG']) | pd.isna(df['FTAG']), ['HomePoints', 'AwayPoints']] = None
    df.loc[df['FTHG'] > df['FTAG'], ['HomePoints', 'AwayPoints']] = [3, 0]  # Home team wins
    df.loc[df['FTHG'] < df['FTAG'], ['HomePoints', 'AwayPoints']] = [0, 3]  # Away team wins
    df.loc[df['FTHG'] == df['FTAG'], ['HomePoints', 'AwayPoints']] = [1, 1]  # Draw
    return df


def calculate_result(df: pd.DataFrame) -> pd.DataFrame:
    """Determines the result of matches based on the full-time goals."""
    df['Result'] = None  # Initialize the column
    df.loc[df['FTHG'] > df['FTAG'], 'Result'] = 'W'  # Win
    df.loc[df['FTHG'] < df['FTAG'], 'Result'] = 'L'  # Loss
    df.loc[df['FTHG'] == df['FTAG'], 'Result'] = 'D'  # Draw
    return df


def split_score_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Splits the 'Score' column into 'FTHG' (Full-Time Home Goals) and 'FTAG' (Full-Time Away Goals).
    
    Args:
        df (pd.DataFrame): DataFrame containing the 'Score' column.
    
    Returns:
        pd.DataFrame: DataFrame with 'FTHG' and 'FTAG' columns added.
    """
    df[['FTHG', 'FTAG']] = df['Score'].str.split('–', expand=True).astype(int)
    return df


def add_season_column(df: pd.DataFrame, season_start_month: int = 8) -> pd.DataFrame:
    """
    Adds a 'Season' column to the DataFrame based on the date and season start month.

    Args:
        df (pd.DataFrame): The input DataFrame containing a 'Date' column.
        season_start_month (int): The starting month of the season (e.g., 8 for August).

    Returns:
        pd.DataFrame: The DataFrame with the added 'Season' column.
    """
    df['Season'] = df['Date'].apply(lambda x: x.year if x.month >= season_start_month else x.year - 1)
    df['Season'] = df['Season'].astype(str) + '/' + (df['Season'] + 1).astype(str).str[2:]
    return df


def encode_season_column(df: pd.DataFrame) -> pd.DataFrame:
    df['season_encoded'] = df['Season'].rank(method='dense').astype(int)
    return df


def add_hour_feature(df: pd.DataFrame) -> pd.DataFrame:
    """Time that matches play may be a factor - regex to reformat from 'hh:mm' to 'hh' """
    # df["hour"] = df["Time"].str.replace(":+", "", regex=True).astype("int")
    df["hour"] = df["Time"].fillna('00').str[:2].astype("int")
    return df


def encode_day_of_week(df: pd.DataFrame) -> pd.DataFrame:
    df["day_code"] = df["Date"].dt.dayofweek # Gives each day of the week a code e.g. Mon = 0, Tues = 2, ....
    return df


def create_teams_rolling_stats(df: pd.DataFrame, team_name: str) -> pd.DataFrame:
    """Creates rolling averages statistics for a given team's dataframe."""
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


def create_rolling_stats(data_base_filepath: str, teams: List[str]) -> pd.DataFrame:
    """Merges rolling statistics for all teams into a single dataframe."""
    rolling_dfs = []
    for team in teams:
        df = pd.read_csv(f"{data_base_filepath}/{team}.csv")
        rolling_df = create_teams_rolling_stats(df, teams[team])
        rolling_dfs.append(rolling_df)

    combined_df = pd.concat(rolling_dfs, ignore_index=False)
    merged_df = combined_df.groupby(['Date', 'HomeTeam', 'AwayTeam'], as_index=False).first()
    # merged_df = merged_df.drop(['G-xG', 'npxG', 'npxG/Sh', 'np:G-xG', 'xG', 'Match Report', 'Match Report.1'], axis=1)
    return merged_df


def add_rolling_stats(df: pd.DataFrame, rolling_df: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(df, rolling_df, how="left", on=["Day","Date", "Time", "HomeTeam", "AwayTeam"], suffixes=('','_y') )


def add_ppg_features(df: pd.DataFrame, teams: dict) -> pd.DataFrame:
    """Adds points per game (PPG) features to the dataframe for each team."""
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
