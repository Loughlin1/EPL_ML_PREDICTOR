import pandas as pd

from ..models.config import (
    LABELS,
    SHOOTING_STATS_COLS,
    SH_ROLLING_COLS,
    SH_ROLLING_HOME_COLS,
    SH_ROLLING_AWAY_COLS
)
from ...core.paths import data_dir
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
    df = df.copy()  # Avoid modifying input
    df.dropna(subset=["date"], inplace=True)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    # Assign home/away teams based on venue
    df.loc[df["venue"] == "Home", "home_team"] = team_name
    df.loc[df["venue"] == "Home", "away_team"] = df["opponent"]
    df.loc[df["venue"] == "Away", "home_team"] = df["opponent"]
    df.loc[df["venue"] == "Away", "away_team"] = team_name

    # Check venue column
    if not set(["Home", "Away"]).issubset(df["venue"].unique()):
        raise ValueError("Error: 'venue' column does not contain expected values.")

    # Extract week number
    if "round" in df.columns and df["round"].dtype == "object":
        df["week"] = df["round"].str.extract(r"(\d+)").astype(int)
    else:
        raise ValueError("Error: 'round' column is missing or not in the expected format.")

    # Calculate rolling averages (window=3, min_periods=1 for early weeks)
    new_cols = [f"{c}_rolling" for c in SHOOTING_STATS_COLS]
    rolling_stats = df[SHOOTING_STATS_COLS].rolling(window=3, min_periods=1, closed="left").mean()
    df[new_cols] = rolling_stats.fillna(0)  # Impute NA with 0 for initial matches

    df[SH_ROLLING_HOME_COLS] = 0.0
    df[SH_ROLLING_AWAY_COLS] = 0.0

    # Assign rolling stats based on venue (home team gets _rolling_h, away team gets _rolling_a)
    df.loc[df["venue"] == "Home", SH_ROLLING_HOME_COLS] = df.loc[df["venue"] == "Home", new_cols].values
    df.loc[df["venue"] == "Away", SH_ROLLING_AWAY_COLS] = df.loc[df["venue"] == "Away", new_cols].values

    # Impute 0 for early weeks or missing data
    df.loc[df["week"] <= 2, SH_ROLLING_HOME_COLS + SH_ROLLING_AWAY_COLS] = 0.0
    return df


def merge_team_stats(combined_df: pd.DataFrame) -> pd.DataFrame:
    """Merges home and away team rolling stats into a single DataFrame per match."""
    # Split into home and away DataFrames
    home_df = combined_df[combined_df["venue"] == "Home"].copy()
    away_df = combined_df[combined_df["venue"] == "Away"].copy()

    # Define columns to keep
    keep_cols = ["date", "home_team", "away_team", "week"]
    keep_cols = keep_cols + SH_ROLLING_HOME_COLS + SH_ROLLING_AWAY_COLS

    # Rename columns in away_df to avoid conflicts
    away_df = away_df[["date", "home_team", "away_team"] + SH_ROLLING_AWAY_COLS]

    # Merge home and away DataFrames
    merged_df = pd.merge(
        home_df[keep_cols],
        away_df[["date", "home_team", "away_team"] + SH_ROLLING_AWAY_COLS],
        how="left",
        on=["date", "home_team", "away_team"],
        suffixes=("", "_away")
    )

    # Update _rolling_a columns with values from away_df
    for col in SH_ROLLING_AWAY_COLS:
        merged_df[col] = merged_df[f"{col}_away"].fillna(merged_df[col])
        merged_df = merged_df.drop(f"{col}_away", axis=1)

    # Fill NaN with 0 for early weeks or missing data
    merged_df[SH_ROLLING_COLS] = merged_df[SH_ROLLING_COLS].fillna(0)
    return merged_df


def create_rolling_shooting_stats(teams: list[str]) -> pd.DataFrame:
    """Merges rolling statistics for all teams into a single dataframe."""
    rolling_dfs = []
    for team in teams:
        df = load_shooting_data(team)
        if df.empty:  # Skip teams with no previous seasons in premier league
            print(f"No shooting data for team {team}, imputing zeros")
            df = pd.DataFrame({
                "date": [], "home_team": [], "away_team": [], "week": [],
                **{col: [] for col in SH_ROLLING_HOME_COLS + SH_ROLLING_AWAY_COLS}
            })
        rolling_df = create_team_rolling_shooting_stats(df, team)
        rolling_dfs.append(rolling_df)

    # Concatenate and select relevant columns
    combined_df = pd.concat(rolling_dfs, ignore_index=False)
    merged_df = merge_team_stats(combined_df)
    return merged_df


def add_previous_season_rank(df: pd.DataFrame, default_rank: int = 18) -> pd.DataFrame:
    """
    Adds previous season's ranking for home and away teams to the dataset.
    
    Args:
        df (pd.DataFrame): Input dataset with 'season', 'home_team', 'away_team' columns.
        standings_df (pd.DataFrame): Standings data with 'Season', 'Pos', 'Team' columns.
        default_rank (int): Rank for teams not in previous season (e.g., promoted teams).
    
    Returns:
        pd.DataFrame: Dataset with 'pos_last_season_h' and 'pos_last_season_a' columns.
    """
    df = df.copy()  # Avoid modifying input
    standings_df = pd.read_csv(f"{data_dir}/standings/2000-2025.csv")
    standings_df = standings_df[["Season", "Pos", "Team"]].copy()

    def reformat_season(season: str) -> str:
        year = int(season.split("-")[0])
        return f"{year}-{year+1}"

    # Function to get previous season
    def get_prev_season(season: str) -> str:
        year = int(season.split("-")[0])
        return f"{year-1}-{year}"
    
    # Add previous season column
    standings_df["Season"] = standings_df["Season"].apply(reformat_season)
    # print(df.head)
    df["prev_season"] = df["season"].apply(get_prev_season)
    
    # Merge for home team rank
    df = pd.merge(
        df,
        standings_df[["Season", "Team", "Pos"]].rename(columns={"Team": "home_team", "Pos": "pos_last_season_h"}),
        how="left",
        left_on=["prev_season", "home_team"],
        right_on=["Season", "home_team"]
    )
    
    # Merge for away team rank
    df = pd.merge(
        df,
        standings_df[["Season", "Team", "Pos"]].rename(columns={"Team": "away_team", "Pos": "pos_last_season_a"}),
        how="left",
        left_on=["prev_season", "away_team"],
        right_on=["Season", "away_team"]
    )
    
    # Fill missing ranks (e.g., promoted teams) with default
    df["pos_last_season_h"] = df["pos_last_season_h"].fillna(default_rank)
    df["pos_last_season_a"] = df["pos_last_season_a"].fillna(default_rank)
    
    # Drop temporary columns
    df = df.drop(columns=["prev_season", "Season_x", "home_team_y", "Season_y", "away_team_y"], errors="ignore")
    
    # # Debug: Check non-zero ranks
    # print("Sample with new features:")
    # print(df[["season", "home_team", "away_team", "pos_last_season_h", "pos_last_season_a"]].head())
    # print("Non-zero pos_last_season_h:", (df["pos_last_season_h"] != default_rank).sum())
    # print("Non-zero pos_last_season_a:", (df["pos_last_season_a"] != default_rank).sum())
    
    return df


def add_rolling_shooting_stats(df: pd.DataFrame, teams: list[str]) -> pd.DataFrame:
    rolling_df = create_rolling_shooting_stats(teams)
    merged_df = pd.merge(
        df,
        rolling_df,
        how="left",
        on=["date", "week", "home_team", "away_team"],
        suffixes=("", "_y"),
    )
    # Impute NA for rolling shooting stats
    merged_df[SH_ROLLING_COLS] = merged_df[SH_ROLLING_COLS].fillna(0)
    return merged_df


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



def add_elo_ratings(df: pd.DataFrame, k: int = 30, home_advantage: int = 100, base_rating: int = 1500, season_reset: float = 0.2) -> pd.DataFrame:
    """
    Adds Elo ratings for home and away teams as features to the dataset.
    
    Args:
        df (pd.DataFrame): Dataset with 'date', 'season', 'home_team', 'away_team', 'FTHG', 'FTAG'.
        k (int): Elo update factor (higher = faster rating changes).
        home_advantage (int): Rating boost for home team.
        base_rating (int): Initial Elo rating for new teams.
        season_reset (float): Fraction to regress ratings toward base at season start (0 to 1).
    
    Returns:
        pd.DataFrame: Dataset with 'elo_h' and 'elo_a' columns.
    """
    df = df.copy().sort_values("date")  # Ensure chronological order
    df["elo_h"] = 0.0
    df["elo_a"] = 0.0
    
    # Initialize Elo ratings for all teams
    teams = set(df["home_team"]).union(df["away_team"])
    elo_ratings = {team: base_rating for team in teams}
    current_season = None
    
    for idx, row in df.iterrows():
        home_team = row["home_team"]
        away_team = row["away_team"]
        season = row["season"]
        
        # Season reset: Regress ratings toward base at new season
        if current_season != season and current_season is not None:
            for team in elo_ratings:
                elo_ratings[team] = base_rating * season_reset + elo_ratings[team] * (1 - season_reset)
        current_season = season
        
        # Get current ratings
        home_elo = elo_ratings[home_team] + home_advantage
        away_elo = elo_ratings[away_team]

        # Update Elo ratings only if FTHG and FTAG are not None
        if pd.notna(row["FTHG"]) and pd.notna(row["FTAG"]):
            # Calculate expected scores
            expected_home = 1 / (1 + 10 ** ((away_elo - home_elo) / 400))
            expected_away = 1 - expected_home
            
            # Determine actual scores (1 = win, 0.5 = draw, 0 = loss)
            if row["FTHG"] > row["FTAG"]:
                home_score, away_score = 1, 0
            elif row["FTHG"] < row["FTAG"]:
                home_score, away_score = 0, 1
            else:
                home_score, away_score = 0.5, 0.5
            
            # Update Elo ratings
            elo_ratings[home_team] += k * (home_score - expected_home)
            elo_ratings[away_team] += k * (away_score - expected_away)
    
    # Debug: Check Elo ranges
    # print("Elo ratings sample:")
    # print(df[["date", "season", "home_team", "away_team", "elo_h", "elo_a"]].head())
    # print(f"Elo_h range: {df['elo_h'].min():.1f} - {df['elo_h'].max():.1f}")
    # print(f"Elo_a range: {df['elo_a'].min():.1f} - {df['elo_a'].max():.1f}")
    
    return df



def add_h2h_features(df: pd.DataFrame, window: int = 5, default_goals: float = 1.5) -> pd.DataFrame:
    """
    Adds head-to-head average goals features for home and away teams.
    
    Args:
        df (pd.DataFrame): Dataset with 'date', 'season', 'home_team', 'away_team', 'FTHG', 'FTAG'.
        window (int): Number of previous H2H matches to consider (default: 5).
        default_goals (float): Default goals for teams with no H2H history (e.g., league avg).
    
    Returns:
        pd.DataFrame: Dataset with 'h2h_home_goals' and 'h2h_away_goals' columns.
    """
    df = df.copy().sort_values("date")  # Ensure chronological order
    df["h2h_avg_goals_a"] = 0.0
    df["h2h_avg_goals_h"] = 0.0
    
    for idx, row in df.iterrows():
        home_team = row["home_team"]
        away_team = row["away_team"]
        match_date = row["date"]
        
        # Filter past matches between these teams (both directions)
        past_matches = df[
            (df["date"] < match_date) &
            (
                ((df["home_team"] == home_team) & (df["away_team"] == away_team)) |
                ((df["home_team"] == away_team) & (df["away_team"] == home_team))
            )
        ].tail(window)  # Last `window` matches
        
        if not past_matches.empty:
            # Compute average goals
            home_goals = []
            away_goals = []
            for _, match in past_matches.iterrows():
                if match["home_team"] == home_team:
                    home_goals.append(match["FTHG"])
                    away_goals.append(match["FTAG"])
                else:
                    home_goals.append(match["FTAG"])  # Home team was away
                    away_goals.append(match["FTHG"])  # Away team was home
            
            df.at[idx, "h2h_avg_goals_h"] = sum(home_goals) / len(home_goals) if home_goals else default_goals
            df.at[idx, "h2h_avg_goals_a"] = sum(away_goals) / len(away_goals) if away_goals else default_goals
        else:
            # No H2H history
            df.at[idx, "h2h_avg_goals_h"] = default_goals
            df.at[idx, "h2h_avg_goals_a"] = default_goals
    
    # Debug: Check feature values
    # print("H2H features sample:")
    # print(df[["date", "season", "home_team", "away_team", "h2h_avg_goals_h", "h2h_avg_goals_a"]].head())
    # print(f"H2H_home_goals range: {df['h2h_avg_goals_h'].min():.2f} - {df['h2h_avg_goals_h'].max():.2f}")
    # print(f"H2H_away_goals range: {df['h2h_avg_goals_a'].min():.2f} - {df['h2h_avg_goals_a'].max():.2f}")

    df[["h2h_avg_goals_h", "h2h_avg_goals_a"]] = df[["h2h_avg_goals_h", "h2h_avg_goals_a"]].fillna(default_goals)
    return df



