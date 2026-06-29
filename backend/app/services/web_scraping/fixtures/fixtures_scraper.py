"""
fixtures_scraper.py

    Module to scrape fixtures data from the web and return it in a structured format.
"""

import io

import pandas as pd
import requests

from ....core.config import settings
from ....db.updaters.fixtures import upsert_fixtures

FOOTBALL_DATA_BASE_URL = settings.FOOTBALL_DATA_BASE_URL
CURRENT_SEASON = settings.CURRENT_SEASON

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}


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

    response = requests.get(url, headers=_HEADERS, timeout=30)
    response.raise_for_status()
    df = pd.read_html(io.StringIO(response.text), attrs={"id": f"sched_{season}_9_1"})[
        0
    ]
    upsert_fixtures(df, season=season)
    print("Fixtures data fetched and saved to database")


if __name__ == "__main__":
    scrape_and_save_fixtures()
