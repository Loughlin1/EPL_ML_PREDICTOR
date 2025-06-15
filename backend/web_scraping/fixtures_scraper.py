"""
fixtures_scraper.py

    Module to scrape fixtures data from the web and return it in a structured format.
"""

import json
import os
import time

import pandas as pd
from dotenv import load_dotenv

from backend.config.paths import (
    FIXTURES_TEST_DATA_FILEPATH,
    SHOOTING_TEST_DATA_DIR,
    TEAMS_IDS_2024_FILEPATH,
)

load_dotenv()

# GLOBAL VARIABLES
FOOTBALL_DATA_URL = os.environ["FOOTBALL_DATA_URL"]
FOOTBALL_SHOOTING_DATA_BASE_URL = os.environ["FOOTBALL_SHOOTING_DATA_BASE_URL"]


def scrape_season_stats(url):
    try:
        df = pd.read_html(url, attrs={"id": "matchlogs_for"})[0]
        return df if not df.empty else None
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None


def scrape_teams_stats(seasons, squad_id, team_name):
    urls = [
        f"{FOOTBALL_SHOOTING_DATA_BASE_URL}/{squad_id}/{season}/matchlogs/c9/shooting/{team_name}-Match-Logs-Premier-League"
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


def scrape_all_teams_stats(seasons, team_ids):
    counter = 0
    for team, id in team_ids.items():
        scrape_teams_stats(seasons, id, team)
        if counter == 3:
            time.sleep(10)
        counter += 1


def scrape_fixtures() -> None:
    """Function to scrape the fixtures data from the web and save it to a CSV file."""
    df = pd.read_html(FOOTBALL_DATA_URL, attrs={"id": "sched_2024-2025_9_1"})[0]
    df.to_csv(FIXTURES_TEST_DATA_FILEPATH)
    print("Data fetched and processed")

    # fetch shooting stats for each team
    teams_2024 = json.load(open(TEAMS_IDS_2024_FILEPATH))
    scrape_all_teams_stats(["2024-2025"], teams_2024)
    time.sleep(10)
