from fastapi import APIRouter, Query, HTTPException
from ...services.data_processing.data_loader import get_this_seasons_fixtures_data
from ...services.web_scraping.fixtures.fixtures_scraper import scrape_and_save_fixtures
from ...services.web_scraping.fixtures.shooting_stats_scraper import (
    scrape_and_save_shooting_stats,
)
from ...db.queries import get_teams, check_missing_results
from ...core.config import settings
import logging

router = APIRouter(
    tags=["Fixtures"],
)

logger = logging.getLogger(__name__)


@router.get("/fixtures")
def get_fixtures(matchweek: int = Query(None), refresh: bool = False):
    """
    Get EPL fixtures, optionally by matchweek, and optionally force refresh.
    """
    fixtures = get_this_seasons_fixtures_data()
    date_check_refresh = check_missing_results(logger=logger)
    if refresh or date_check_refresh:
        print("Refreshing data")
        scrape_and_save_fixtures(season=settings.CURRENT_SEASON)
        scrape_and_save_shooting_stats([settings.CURRENT_SEASON])

    if matchweek is not None:
        fixtures = fixtures[fixtures["week"] == matchweek]

    # Handle NaN, inf, -inf for JSON serialization
    fixtures = fixtures.replace([float("inf"), float("-inf")], None)
    fixtures = fixtures.fillna("")  # Or fill with "N/A" or 0 depending on column
    return fixtures.to_dict(orient="records")


@router.get("/teams")
def get_teams():
    try:
        teams = get_teams()
        return {"teams": teams}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load teams: {str(e)}")
