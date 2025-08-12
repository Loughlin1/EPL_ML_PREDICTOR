"""
shooting_stats_scraper.py

    Module to scrape shooting stats data from the web
"""

import time
import pandas as pd

from ....core.config import settings
from ....core.paths import data_dir
from ....db.loaders.shooting_stats import add_shooting_stats
from ....db.queries import get_teams_by_season
from ...data_processing.data_loader import generate_seasons


FOOTBALL_DATA_BASE_URL = settings.FOOTBALL_DATA_BASE_URL
CURRENT_SEASON = settings.CURRENT_SEASON


def save_to_csv(df: pd.DataFrame, team_name: str):
    if " " in team_name:
        team_name = team_name.replace(" ", "-")
    csv_filepath = f"{data_dir}/shooting_stats/{team_name}.csv"
    df.to_csv(csv_filepath)
    print(f"Saved {team_name} to {csv_filepath}")


def scrape_season_stats(url: str):
    try:
        df = pd.read_html(url, attrs={"id": "matchlogs_for"})[0]
        return df if not df.empty else None
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None


def scrape_teams_stats(seasons, squad_id, team_name) -> pd.DataFrame:
    """
    Scrape shooting stats for a given team and seasons.

    Args:
        seasons: List of seasons to scrape.
        squad_id: ID of the team's squad from FBREF.
        team_name: Name of the team (e.g. "Arsenal").
    Returns:
        pd.DataFrame: DataFrame containing shooting stats.
    """
    if " " in team_name:
        team_name = team_name.replace(" ", "-")
    urls = [
        f"{FOOTBALL_DATA_BASE_URL}/en/squads/{squad_id}/{season}/matchlogs/c9/shooting/{team_name}-Match-Logs-Premier-League"
        for season in seasons
    ]

    dfs = []
    for url in urls:
        df = scrape_season_stats(url)
        time.sleep(10)
        if df is not None:
            dfs.append(df)
    if dfs:
        df = pd.concat(dfs, ignore_index=False)
        df = df.droplevel(level=0, axis=1)
        return df
    else:
        print(f"No valid data for team {team_name} in seasons {seasons}")


def scrape_shooting_stats(seasons: list[str]) -> None:
    """
    Scrapes shooting stats from the web and saves it to database
    """
    counter = 0
    for team in get_teams_by_season(seasons):
        df = scrape_teams_stats(seasons, team["fbref_team_id"], team["fullname"])
        add_shooting_stats(df, team["name"], seasons)

        if counter == 3:
            time.sleep(10)
        counter += 1
    print("Scraping completed")


if __name__ == "__main__":
    seasons = generate_seasons(2024, 2024)
    print(seasons)
    scrape_shooting_stats(seasons)
    print(f"Shooting stats scraped for seasons: {seasons}")
