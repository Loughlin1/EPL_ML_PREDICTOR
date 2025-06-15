from typing import List

import pandas as pd


def calculate_match_points(df: pd.DataFrame) -> pd.DataFrame:
    """Function to calculate points for each team in each game"""
    df.loc[pd.isna(df["FTHG"]) | pd.isna(df["FTAG"]), ["HomePoints", "AwayPoints"]] = (
        None
    )
    df.loc[df["FTHG"] > df["FTAG"], ["HomePoints", "AwayPoints"]] = [
        3,
        0,
    ]  # Home team wins
    df.loc[df["FTHG"] < df["FTAG"], ["HomePoints", "AwayPoints"]] = [
        0,
        3,
    ]  # Away team wins
    df.loc[df["FTHG"] == df["FTAG"], ["HomePoints", "AwayPoints"]] = [1, 1]  # Draw
    return df


def calculate_result(df: pd.DataFrame) -> pd.DataFrame:
    """Determines the result of matches based on the full-time goals."""
    df["Result"] = None  # Initialize the column
    df.loc[df["FTHG"] > df["FTAG"], "Result"] = "W"  # Win
    df.loc[df["FTHG"] < df["FTAG"], "Result"] = "L"  # Loss
    df.loc[df["FTHG"] == df["FTAG"], "Result"] = "D"  # Draw
    return df


def split_score_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Splits the 'Score' column into
    'FTHG' (Full-Time Home Goals) and 'FTAG' (Full-Time Away Goals).

    Args:
        df (pd.DataFrame): DataFrame containing the 'Score' column.

    Returns:
        pd.DataFrame: DataFrame with 'FTHG' and 'FTAG' columns added.
    """
    df[["FTHG", "FTAG"]] = df["Score"].str.split("–", expand=True).astype(int)
    return df


def add_season_column(df: pd.DataFrame, season_start_month: int = 8) -> pd.DataFrame:
    """
    Adds a 'Season' column to the DataFrame based on the date and season start month.

    Args:
        df (pd.DataFrame): The input DataFrame containing a 'Date' column.
        season_start_month (int): The starting month of season (e.g., 8 for August).

    Returns:
        pd.DataFrame: The DataFrame with the added 'Season' column.
    """
    df["Season"] = df["Date"].apply(
        lambda x: x.year if x.month >= season_start_month else x.year - 1
    )
    df["Season"] = (
        df["Season"].astype(str) + "/" + (df["Season"] + 1).astype(str).str[2:]
    )
    return df


def add_hour_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Time that matches play as a factor - regex to reformat from 'hh:mm' to 'hh
    '"""
    # df["hour"] = df["Time"].str.replace(":+", "", regex=True).astype("int")
    df["hour"] = df["Time"].fillna("00").str[:2].astype("int")
    return df


def create_teams_rolling_stats(df: pd.DataFrame, team_name: str) -> pd.DataFrame:
    """Creates rolling averages statistics for a given team's dataframe."""
    df.dropna(subset=["Date"], inplace=True)

    # Getting rolling averages
    cols = ["GF", "GA", "Sh", "SoT", "PK", "PKatt"]
    new_cols = [f"{c}_rolling" for c in cols]
    rolling_stats = df[cols].rolling(3, closed="left").mean()
    df[new_cols] = rolling_stats
    # df = df.dropna(subset=new_cols)

    df.loc[df["Venue"] == "Home", "HomeTeam"] = team_name
    df.loc[df["Venue"] == "Home", "AwayTeam"] = df["Opponent"]
    df.loc[df["Venue"] == "Away", "HomeTeam"] = df["Opponent"]
    df.loc[df["Venue"] == "Away", "AwayTeam"] = team_name
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")

    # Check if 'Venue' column has correct entries
    if "Home" not in df["Venue"].unique() or "Away" not in df["Venue"].unique():
        print("Error: 'Venue' column does not contain expected values.")
        return df

    rolling_home_cols = [f"{c}_rolling_h" for c in cols]
    rolling_away_cols = [f"{c}_rolling_a" for c in cols]

    df.loc[df["Venue"] == "Home", rolling_home_cols] = df.loc[
        df["Venue"] == "Home", new_cols
    ].values
    df.loc[df["Venue"] == "Away", rolling_away_cols] = df.loc[
        df["Venue"] == "Away", new_cols
    ].values

    # Filling in missing rolling away stats with 0
    # so that they don't add an bias to the stats - form at start of season is unknown
    if "Round" in df.columns and df["Round"].dtype == "object":
        # Extract the numeric part from 'Round' and convert it to an integer
        df["Wk"] = df["Round"].str.extract(r"(\d+)").astype(int)
    else:
        print("Error: 'Round' column is missing or not in the expected format.")

    # Week 1
    df.loc[(df["Wk"] == 1) & (df["Venue"] == "Home"), rolling_home_cols] = 0
    df.loc[(df["Wk"] == 1) & (df["Venue"] == "Away"), rolling_away_cols] = 0

    # Week 2 - set at the last week's stats
    df.loc[(df["Wk"] == 2) & (df["Venue"] == "Home"), rolling_home_cols] = 0
    df.loc[(df["Wk"] == 2) & (df["Venue"] == "Away"), rolling_away_cols] = 0

    # Week 3
    df.loc[(df["Wk"] == 3) & (df["Venue"] == "Home"), rolling_home_cols] = 0
    df.loc[(df["Wk"] == 3) & (df["Venue"] == "Away"), rolling_away_cols] = 0

    return df


def create_rolling_stats(data_base_filepath: str, teams: List[str]) -> pd.DataFrame:
    """Merges rolling statistics for all teams into a single dataframe."""
    rolling_dfs = []
    for team in teams:
        df = pd.read_csv(f"{data_base_filepath}/{team}.csv")
        rolling_df = create_teams_rolling_stats(df, teams[team])
        rolling_dfs.append(rolling_df)

    combined_df = pd.concat(rolling_dfs, ignore_index=False)
    merged_df = combined_df.groupby(
        ["Date", "HomeTeam", "AwayTeam"], as_index=False
    ).first()
    return merged_df


def add_rolling_stats(df: pd.DataFrame, rolling_df: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(
        df,
        rolling_df,
        how="left",
        on=["Day", "Date", "Time", "HomeTeam", "AwayTeam"],
        suffixes=("", "_y"),
    )


def add_ppg_features(df: pd.DataFrame, teams: dict) -> pd.DataFrame:
    """Adds points per game (PPG) features to the dataframe for each team."""
    for team in teams.values():
        # Get all the matches of a team
        # Calculate the rolling points per game with a window of 3 games
        team_df = df[(df["HomeTeam"] == team) | (df["AwayTeam"] == team)].copy()
        team_df["Points"] = team_df["HomePoints"].where(
            team_df["HomeTeam"] == team, team_df["AwayPoints"]
        )
        team_df["PPG_rolling"] = (
            team_df["Points"].rolling(3, closed="left").mean().fillna(0)
        )

        team_df.loc[:, "Points"] = df["HomePoints"].where(
            df["HomeTeam"] == team, df["AwayPoints"]
        )
        df.loc[df["HomeTeam"] == team, "PPG_rolling_h"] = team_df.loc[
            team_df["HomeTeam"] == team, "PPG_rolling"
        ]
        df.loc[df["AwayTeam"] == team, "PPG_rolling_a"] = team_df.loc[
            team_df["AwayTeam"] == team, "PPG_rolling"
        ]

    return df
