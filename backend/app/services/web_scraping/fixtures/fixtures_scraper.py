"""
fixtures_scraper.py

    Module to scrape fixtures data from the web and return it in a structured format.
"""

import time
import pandas as pd

from ....db.updaters.fixtures import upsert_fixtures
from ....core.config import settings


FOOTBALL_DATA_BASE_URL = settings.FOOTBALL_DATA_BASE_URL
CURRENT_SEASON = settings.CURRENT_SEASON


def scrape_and_save_fixtures(season: str = None) -> None:
    """
    Function to scrape the fixtures data from the web and saves it to the database.
    Args:
        season (str): The season for which fixtures are being scraped.
                      E.g. ("2024-2025") (defaults to current season)
    """
    if season is None:
        season = CURRENT_SEASON
        url = f"{FOOTBALL_DATA_BASE_URL}/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
    else:
        url = f"{FOOTBALL_DATA_BASE_URL}/en/comps/9/{season}/schedule/{season}-Premier-League-Scores-and-Fixtures"

    df = pd.read_html(url, attrs={"id": f"sched_{season}_9_1"})[0]
    upsert_fixtures(df, season=season)
    print(f"Fixtures data fetched and saved to database")


if __name__ == "__main__":
    scrape_and_save_fixtures()
