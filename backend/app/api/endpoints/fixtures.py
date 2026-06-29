import logging

from fastapi import APIRouter, Query

from ...core.config import settings
from ...db.queries import check_missing_results, get_available_seasons
from ...db.queries import get_teams as db_get_teams
from ...services.data_processing.data_loader import get_this_seasons_fixtures_data
from ...services.web_scraping.fixtures.fixtures_scraper import scrape_and_save_fixtures
from ...services.web_scraping.fixtures.shooting_stats_scraper import (
    scrape_and_save_shooting_stats,
)

router = APIRouter(tags=["Fixtures"])
logger = logging.getLogger(__name__)


@router.get("/seasons")
def list_seasons():
    """Return all seasons that have fixture data in the database."""
    return {"seasons": get_available_seasons()}


@router.get("/fixtures")
def get_fixtures(
    matchweek: int = Query(None),
    refresh: bool = False,
    season: str = Query(None),
):
    """
    Get EPL fixtures, optionally by matchweek and/or season.
    Only attempts a live scrape refresh for the current season.
    """
    target_season = season or settings.CURRENT_SEASON
    fixtures = get_this_seasons_fixtures_data(season=target_season)

    if target_season == settings.CURRENT_SEASON:
        date_check_refresh = check_missing_results(logger=logger)
        if refresh or date_check_refresh:
            try:
                scrape_and_save_fixtures(season=settings.CURRENT_SEASON)
                scrape_and_save_shooting_stats([settings.CURRENT_SEASON])
            except Exception as e:
                logger.warning("Scrape failed, serving cached DB data: %s", e)

    if matchweek is not None:
        fixtures = fixtures[fixtures["week"] == matchweek]

    fixtures = fixtures.replace([float("inf"), float("-inf")], None).fillna("")
    return fixtures.to_dict(orient="records")


@router.get("/teams")
def get_teams():
    """Return all teams in the database."""
    return {"teams": db_get_teams()}
