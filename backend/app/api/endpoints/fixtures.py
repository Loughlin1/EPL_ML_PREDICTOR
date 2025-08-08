from fastapi import APIRouter, Query
from app.services.data_processing.data_loader import get_this_seasons_fixtures_data
from app.services.web_scraping.fixtures.fixtures_scraper import scrape_fixtures
from app.core.config.paths import TEAMS_IDS_2024_FILEPATH

import json

router = APIRouter(
    prefix="/fixtures",
    tags=["Fixtures"],
)

@router.get("/")
def get_fixtures(matchweek: int = Query(None), refresh: bool = False):
    """
    Get EPL fixtures, optionally by matchweek, and optionally force refresh.
    """
    if refresh:
        teams_2024 = json.load(open(TEAMS_IDS_2024_FILEPATH))
        scrape_fixtures(season="2024-2025", teams=teams_2024)
    fixtures = get_this_seasons_fixtures_data()

    if matchweek is not None:
        fixtures = fixtures[fixtures["Matchweek"] == matchweek]

    # Handle NaN, inf, -inf for JSON serialization
    fixtures = fixtures.replace([float("inf"), float("-inf")], None)
    fixtures = fixtures.fillna("")  # Or fill with "N/A" or 0 depending on column
    return fixtures.to_dict(orient="records")
