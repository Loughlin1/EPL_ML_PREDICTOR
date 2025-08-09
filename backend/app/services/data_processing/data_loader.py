import os
import pandas as pd

from ...core.paths import FIXTURES_TEST_DATA_FILEPATH
from ...db.database import get_session
from ...db.models import Match

def load_training_data(training_data_dir: str):
    if not os.path.exists(training_data_dir):
        raise FileExistsError(f"The path {training_data_dir} does NOT exist.")

    file_paths = [
        os.path.join(training_data_dir, f)
        for f in os.listdir(training_data_dir)
        if f.endswith(".csv") and os.path.isfile(os.path.join(training_data_dir, f))
    ]
    dfs = [
        pd.read_csv(file, index_col=0)
        for file in file_paths
    ]
    return pd.concat(dfs, ignore_index=False)


def clean_data(df):
    # ...existing code for cleaning...
    df.drop(columns=["Notes", "Match Report", "xG", "xG.1", "Attendance"], inplace=True)
    df.rename(columns={"Home": "HomeTeam", "Away": "AwayTeam"}, inplace=True)
    df.dropna(subset=["Day"], inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
    df["Wk"] = df["Wk"].astype(int)
    return df


def get_this_seasons_fixtures_data() -> pd.DataFrame:
    """
    Reads the fixtures data from a CSV file,
    drops rows with NaN values, and returns the DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing the fixtures data.
    """
    df = pd.read_csv(FIXTURES_TEST_DATA_FILEPATH, index_col=0)
    df.dropna(thresh=7, inplace=True)  # Dropping any NaN rows in the data
    return df    


def get_seasons_fixtures(season: str) -> pd.DataFrame:
    """
    Args:
        season: str season to get fixtures for e.g. "2014-2015"
    Returns:
       pd.DataFrame: DataFrame containing the fixtures data for the given season.
    """
    with get_session() as session:
        matches = session.query(Match).filter(Match.season == season).all()
        df = pd.DataFrame([{
            "season": m.season,
            "week": m.week,
            "day": m.day,
            "date": m.date,
            "time": m.time,
            "home_team_id": m.home_team_id,
            "away_team_id": m.away_team_id,
            "home_goals": m.home_goals,
            "away_goals": m.away_goals,
            "result": m.result,
            "attendance": m.attendance,
            "venue": m.venue,
            "referee": m.referee
        } for m in matches])
    return df


def generate_seasons(start_year: int, end_year: int):
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


if __name__ == "__main__":
    print(get_seasons_fixtures("2014-2015"))
