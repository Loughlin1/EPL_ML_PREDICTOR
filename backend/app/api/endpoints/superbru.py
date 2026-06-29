import logging

from fastapi import APIRouter

from ...core.config import settings
from ...schemas import SuperbruLeaderboardResponse
from ...services import superbru_service

router = APIRouter(prefix="/superbru", tags=["Superbru"])
logger = logging.getLogger(__name__)


@router.get("/points/top/global", response_model=SuperbruLeaderboardResponse)
def get_leaderboard_points(season: str = None):
    """Return top global Superbru leaderboard points, cached per season."""
    target_season = season or settings.CURRENT_SEASON
    return superbru_service.get_leaderboard(target_season)
