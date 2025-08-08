from fastapi import APIRouter, Query, HTTPException
from app.services.data_processing.data_loader import get_this_seasons_fixtures_data
from app.services.web_scraping.fixtures.fixtures_scraper import scrape_fixtures
from app.core.config.paths import TEAMS_IDS_2024_FILEPATH, TEAMS_2024_FILEPATH

import json

router = APIRouter(
    tags=["Fixtures"],
)

@router.get("/fixtures")
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


@router.get("/teams")
def get_teams():
    try:
        with open(TEAMS_2024_FILEPATH, "r") as f:
            teams = json.load(f)
        return {"teams": teams}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load teams: {str(e)}")
