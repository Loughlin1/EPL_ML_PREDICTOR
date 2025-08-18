import os
import pandas as pd
import json
import pytz
from datetime import datetime, timedelta

from ..models.config import TRAINING_DATA_START_SEASON, TRAINING_DATA_END_SEASON
from ...core.config import settings
from ...db.queries import get_seasons_fixtures, get_team_details, get_shooting_stats


def load_json_file(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def save_json_file(data, filepath):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def generate_seasons(start_year: int, end_year: int) -> list[str]:
    """
    Generate a list of seasons from start_year to end_year.
    Args:
        start_year: int (e.g. 2024)
        end_year: int (e.g. 2025)
    Returns:
        list of seasons (e.g. ["2024-2025", "2025-2026"])
    """
    seasons = []
    for year in range(start_year, end_year + 1):
        season_start = str(year)
        season_end = str(year + 1)
        season = f"{season_start}-{season_end}"
        seasons.append(season)
    return seasons


def load_training_data(start_season: int = None) -> pd.DataFrame:
    """
    Load training fixtures data from database
    Args:
        start_year: int (e.g. 2014 for "2014-2015")
    Returns:
        pd.DataFrame
    """
    dfs = []
    if not start_season:
        start_season = TRAINING_DATA_START_SEASON
    for season in generate_seasons(
        start_year=start_season, end_year=TRAINING_DATA_END_SEASON
    ):
        df = pd.DataFrame(get_seasons_fixtures(season=season))
        if not df.empty:
            dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()  # Return empty DataFrame if no data


def load_shooting_data(team: str) -> pd.DataFrame:
    """Load training shooting data for a team from database"""
    ...
    team_id = get_team_details(team)["team_id"]
    return pd.DataFrame(get_shooting_stats(team_id=team_id))


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # ...existing code for cleaning...
    df.drop(
        columns=["Notes", "Match Report", "xG", "xG.1", "Attendance"],
        inplace=True,
        errors="ignore",
    )
    df.dropna(subset=["date"], inplace=True)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df["week"] = df["week"].astype(int)
    return df


def get_this_seasons_fixtures_data() -> pd.DataFrame:
    """
    Reads this seasons fixtures data from database,
    drops rows with NaN values, and returns the DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing the fixtures data.
    """
    df = pd.DataFrame(get_seasons_fixtures(season=settings.CURRENT_SEASON))
    df.dropna(thresh=7, inplace=True)  # Dropping any NaN rows in the data
    return df
