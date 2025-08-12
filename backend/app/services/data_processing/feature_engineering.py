import pandas as pd

from ..models.config import LABELS, SHOOTING_STATS_COLS
from .data_loader import load_shooting_data


def calculate_match_points(df: pd.DataFrame) -> pd.DataFrame:
    """Function to calculate points for each team in each game"""
    df.loc[
        pd.isna(df["FTHG"]) | pd.isna(df["FTAG"]), ["home_points", "away_points"]
    ] = None
    df.loc[df["FTHG"] > df["FTAG"], ["home_points", "away_points"]] = [
        3,
        0,
    ]  # Home team wins
    df.loc[df["FTHG"] < df["FTAG"], ["home_points", "away_points"]] = [
        0,
        3,
    ]  # Away team wins
    df.loc[df["FTHG"] == df["FTAG"], ["home_points", "away_points"]] = [1, 1]  # Draw
    return df


# def calculate_result(df: pd.DataFrame) -> pd.DataFrame:
#     """Determines the result of matches based on the full-time goals."""
#     df["Result"] = None  # Initialize the column
#     df.loc[df["FTHG"] > df["FTAG"], "Result"] = "W"  # Win
#     df.loc[df["FTHG"] < df["FTAG"], "Result"] = "L"  # Loss
#     df.loc[df["FTHG"] == df["FTAG"], "Result"] = "D"  # Draw
#     return df


# def split_score_column(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Splits the 'Score' column into
#     'FTHG' (Full-Time Home Goals) and 'FTAG' (Full-Time Away Goals).

#     Args:
#         df (pd.DataFrame): DataFrame containing the 'Score' column.

#     Returns:
#         pd.DataFrame: DataFrame with 'FTHG' and 'FTAG' columns added.
#     """
#     df[LABELS] = df["Score"].str.split("–", expand=True).astype(int)
#     return df


# def add_season_column(df: pd.DataFrame, season_start_month: int = 8) -> pd.DataFrame:
#     """
#     Adds a 'Season' column to the DataFrame based on the date and season start month.

#     Args:
#         df (pd.DataFrame): The input DataFrame containing a 'date' column.
#         season_start_month (int): The starting month of season (e.g., 8 for August).

#     Returns:
#         pd.DataFrame: The DataFrame with the added 'season' column.
#     """
#     df["season"] = df["date"].apply(
#         lambda x: x.year if x.month >= season_start_month else x.year - 1
#     )
#     df["season"] = (
#         df["season"].astype(str) + "/" + (df["season"] + 1).astype(str).str[2:]
#     )
#     return df


def add_hour_feature(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts the hour from the 'time' column, handling non-string types safely."""
    df["hour"] = (
        df["time"]
        .fillna("00")
        .apply(lambda x: str(x)[:2] if pd.notnull(x) else "00")
        .astype(int)
    )
    return df


def create_team_rolling_shooting_stats(
    df: pd.DataFrame, team_name: str
) -> pd.DataFrame:
    """Creates rolling averages statistics for a given team's dataframe."""
    df.dropna(subset=["date"], inplace=True)
    # Getting rolling averages
    new_cols = [f"{c}_rolling" for c in SHOOTING_STATS_COLS]
    rolling_stats = df[SHOOTING_STATS_COLS].rolling(3, closed="left").mean()
    df[new_cols] = rolling_stats

    df.loc[df["venue"] == "Home", "home_team"] = team_name
    df.loc[df["venue"] == "Home", "away_team"] = df["opponent"]
    df.loc[df["venue"] == "Away", "home_team"] = df["opponent"]
    df.loc[df["venue"] == "Away", "away_team"] = team_name
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    # Check if 'venue' column has correct entries
    if "Home" not in df["venue"].unique() or "Away" not in df["venue"].unique():
        raise Exception("Error: 'venue' column does not contain expected values.")

    rolling_home_cols = [f"{c}_rolling_h" for c in SHOOTING_STATS_COLS]
    rolling_away_cols = [f"{c}_rolling_a" for c in SHOOTING_STATS_COLS]

    df.loc[df["venue"] == "Home", rolling_home_cols] = df.loc[
        df["venue"] == "Home", new_cols
    ].values
    df.loc[df["venue"] == "Away", rolling_away_cols] = df.loc[
        df["venue"] == "Away", new_cols
    ].values

    # Filling in missing rolling away stats with 0
    # so that they don't add an bias to the stats - form at start of season is unknown
    if "round" in df.columns and df["round"].dtype == "object":
        # Extract the numeric part from 'Round' and convert it to an integer
        df["week"] = df["round"].str.extract(r"(\d+)").astype(int)
    else:
        raise Exception(
            "Error: 'round' column is missing or not in the expected format."
        )

    # Week 1
    df.loc[(df["week"] == 1) & (df["venue"] == "Home"), rolling_home_cols] = 0
    df.loc[(df["week"] == 1) & (df["venue"] == "Away"), rolling_away_cols] = 0

    # Week 2 - set at the last week's stats
    df.loc[(df["week"] == 2) & (df["venue"] == "Home"), rolling_home_cols] = 0
    df.loc[(df["week"] == 2) & (df["venue"] == "Away"), rolling_away_cols] = 0

    # Week 3
    df.loc[(df["week"] == 3) & (df["venue"] == "Home"), rolling_home_cols] = 0
    df.loc[(df["week"] == 3) & (df["venue"] == "Away"), rolling_away_cols] = 0

    return df


def create_rolling_shooting_stats(teams: list[str]) -> pd.DataFrame:
    """Merges rolling statistics for all teams into a single dataframe."""
    rolling_dfs = []
    for team in teams:
        df = load_shooting_data(team)
        if df.empty:  # Skip teams with no previous seasons in premier league
            continue
        rolling_df = create_team_rolling_shooting_stats(df, team)
        rolling_dfs.append(rolling_df)

    combined_df = pd.concat(rolling_dfs, ignore_index=False)
    merged_df = combined_df.groupby(
        ["date", "home_team", "away_team"], as_index=False
    ).first()
    return merged_df


def add_rolling_shooting_stats(df: pd.DataFrame, teams: list[str]) -> pd.DataFrame:
    rolling_df = create_rolling_shooting_stats(teams)
    return pd.merge(
        df,
        rolling_df,
        how="left",
        on=["day", "date", "week", "home_team", "away_team"],
        suffixes=("", "_y"),
    )


def add_ppg_features(df: pd.DataFrame, teams: list[str]) -> pd.DataFrame:
    """Adds points per game (PPG) features to the dataframe for each team."""
    for team in teams:
        # Get all the matches of a team
        # Calculate the rolling points per game with a window of 3 games
        team_df = df[(df["home_team"] == team) | (df["away_team"] == team)].copy()
        team_df["Points"] = team_df["home_points"].where(
            team_df["home_team"] == team, team_df["away_points"]
        )
        team_df["ppg_rolling"] = (
            team_df["Points"].rolling(3, closed="left").mean().fillna(0)
        )

        team_df.loc[:, "Points"] = df["home_points"].where(
            df["home_team"] == team, df["away_points"]
        )
        df.loc[df["home_team"] == team, "ppg_rolling_h"] = team_df.loc[
            team_df["home_team"] == team, "ppg_rolling"
        ]
        df.loc[df["away_team"] == team, "ppg_rolling_a"] = team_df.loc[
            team_df["away_team"] == team, "ppg_rolling"
        ]

    return df
