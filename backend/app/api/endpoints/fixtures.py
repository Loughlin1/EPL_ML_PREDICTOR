from fastapi import APIRouter, Query
from app.services.utils.fixtures import get_fixtures_data
from app.services.web_scraping.fixtures.fixtures_scraper import scrape_fixtures

router = APIRouter()

@router.get("/fixtures")
def get_fixtures(matchweek: int = Query(None), refresh: bool = False):
    """
    Get EPL fixtures, optionally by matchweek, and optionally force refresh.
    """
    if refresh:
        scrape_fixtures()
    fixtures = get_fixtures_data()

    if matchweek is not None:
        fixtures = fixtures[fixtures["Matchweek"] == matchweek]

    # Handle NaN, inf, -inf for JSON serialization
    fixtures = fixtures.replace([float("inf"), float("-inf")], None)
    fixtures = fixtures.fillna("")  # Or fill with "N/A" or 0 depending on column
    return fixtures.to_dict(orient="records")
