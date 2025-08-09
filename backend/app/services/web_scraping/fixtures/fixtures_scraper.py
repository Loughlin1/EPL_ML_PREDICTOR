"""
fixtures_scraper.py

    Module to scrape fixtures data from the web and return it in a structured format.
"""

import json
import os
import time

import pandas as pd
from dotenv import load_dotenv

from ....core.paths import (
    FIXTURES_TEST_DATA_FILEPATH,
    SHOOTING_TEST_DATA_DIR,
    TEAMS_IDS_2024_FILEPATH,
    TEAMS_IDS_TRAINING_FILEPATH
)

load_dotenv()

# GLOBAL VARIABLES
FOOTBALL_DATA_BASE_URL = os.environ["FOOTBALL_DATA_BASE_URL"]
CURRENT_SEASON = "2024-2025"


def scrape_season_stats(url):
    try:
        df = pd.read_html(url, attrs={"id": "matchlogs_for"})[0]
        return df if not df.empty else None
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None


def scrape_teams_stats(seasons, squad_id, team_name):
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
        csv_filepath = f"{SHOOTING_TEST_DATA_DIR}/{team_name}.csv"
        df.to_csv(csv_filepath)
        print(f"Exported {team_name} to {csv_filepath}")
    else:
        print(f"No valid data for team {team_name} in seasons {seasons}")


def scrape_all_teams_stats(seasons: list[str], team_ids):
    counter = 0
    for team, id in team_ids.items():
        scrape_teams_stats(seasons, id, team)
        if counter == 3:
            time.sleep(10)
        counter += 1


def scrape_fixtures(season: str = "2024-2025", teams: dict = None) -> None:
    """Function to scrape the fixtures data from the web and save it to a CSV file."""
    if season == CURRENT_SEASON:
        url = f"{FOOTBALL_DATA_BASE_URL}/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
    else:
        url = f"{FOOTBALL_DATA_BASE_URL}/en/comps/9/{season}/schedule/{season}-Premier-League-Scores-and-Fixtures"

    if not teams:
        teams = json.load(open(TEAMS_IDS_TRAINING_FILEPATH))

    df = pd.read_html(url, attrs={"id": f"sched_{season}_9_1"})[0]
    filepath = FIXTURES_TEST_DATA_FILEPATH
    df.to_csv(filepath)
    print(f"Fixtures data fetched and saved to {filepath}")
    # fetch shooting stats for each team
    scrape_all_teams_stats([season], teams)
