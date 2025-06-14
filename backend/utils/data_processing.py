"""
backend/utils/data_processing.py

"""
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

import pandas as pd


def load_data(file_paths):
    dfs = [pd.read_csv('./data/' + file, index_col=0) for file in file_paths]
    return pd.concat(dfs, ignore_index=False)


def clean_data(df):
    # ...existing code for cleaning...
    df.drop(columns=['Notes', 'Match Report', 'xG', 'xG.1', 'Attendance'], inplace=True)
    df.rename(columns={'Home': 'HomeTeam', 'Away': 'AwayTeam'}, inplace=True)
    df.dropna(subset=['Day'], inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")
    df['Wk'] = df['Wk'].astype(int)
    return df



def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    # Preprocesses raw data for model input
    # ...existing code...
    ...


def create_rolling_stats(df: pd.DataFrame, team_name: str):
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


def merge_rolling_stats(data_base_filepath: str, teams: list) -> pd.DataFrame:
    """Merges rolling statistics for all teams into a single dataframe."""
    rolling_dfs = []
    for team in teams:
        df = pd.read_csv(f"{data_base_filepath}/{team}.csv")
        rolling_df = create_rolling_stats(df, teams[team])
        rolling_dfs.append(rolling_df)

    combined_df = pd.concat(rolling_dfs, ignore_index=False)
    merged_df = combined_df.groupby(['Date', 'HomeTeam', 'AwayTeam'], as_index=False).first()
    # merged_df = merged_df.drop(['G-xG', 'npxG', 'npxG/Sh', 'np:G-xG', 'xG', 'Match Report', 'Match Report.1'], axis=1)

    return merged_df



def add_ppg_features(df, teams):
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

