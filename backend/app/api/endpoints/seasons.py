import logging

from fastapi import APIRouter, Depends, HTTPException

from ...core.config import Settings, settings
from ...db.queries import get_available_seasons
from ...schemas import MatchweekResponse, SeasonsResponse
from ...services import seasons_service
from ...services.data_processing.data_loader import get_this_seasons_fixtures_data
from ...services.models.summary import get_or_compute_summary
from ...services.utils.matchweek import get_current_matchweek

router = APIRouter(prefix="/seasons", tags=["Seasons"])
logger = logging.getLogger(__name__)


def get_settings() -> Settings:
    return settings


@router.get("", response_model=SeasonsResponse)
def list_seasons():
    """Return all seasons available in the database."""
    return SeasonsResponse(seasons=get_available_seasons())


@router.get("/{season}/summary")
def get_season_summary(season: str, cfg: Settings = Depends(get_settings)):
    """
    Return pre-computed season summary (superbru points, model performance).
    Finished seasons are served from cache instantly. Current season is computed live.
    """
    summary = get_or_compute_summary(season, current_season=cfg.CURRENT_SEASON)
    if not summary:
        raise HTTPException(status_code=404, detail=f"No data found for season {season}")
    return summary


@router.get("/{season}/matchweek")
def get_season_current_matchweek(season: str):
    """Return the current/most recent matchweek number for a season."""
    fixtures = get_this_seasons_fixtures_data(season=season)
    week = get_current_matchweek(fixtures)
    return {"current_matchweek": week}


@router.get("/{season}/matchweek/{week}", response_model=MatchweekResponse)
def get_matchweek(season: str, week: int):
    """
    Return fixtures and predictions for a single matchweek.

    For finished seasons predictions are read directly from the DB cache.
    For the current season the prediction pipeline is triggered if needed.
    """
    result = seasons_service.get_matchweek(season=season, week=week)
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"No data for {season} matchweek {week}"
        )
    return result
