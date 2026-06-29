import json
import logging
import os
import traceback
from datetime import datetime, timedelta

import pandas as pd
from fastapi import APIRouter, HTTPException

from ...core.paths import SUPERBRU_LEADERBOARD_CACHE as CACHE_PATH
from ...schemas import MatchInput
from ...services.utils.superbru_points_calculator import get_superbru_points
from ...services.web_scraping.superbru.leaderboard_scraper import get_top_points

router = APIRouter(
    prefix="/superbru",
    tags=["Superbru"],
)
logger = logging.getLogger(__name__)

CACHE_TTL = timedelta(days=90)  # timedelta(hours=1)


@router.post("/points")
def calculate_superbru_points(request: MatchInput):
    """
    Calculate the number of SuperBru points for predictions
    """
    try:
        df_input = pd.DataFrame(request.data)
        points = get_superbru_points(df_input)
        return {"points": points}
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Points calculation failed: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/points/top/global")
def get_leaderboard_points(season: str = None):
    """
    Get the top global points on SuperBru leaderboard, cached per season.
    """
    from ...core.config import settings

    target_season = season or settings.CURRENT_SEASON

    cache = {}
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            cache = json.load(f)

    entry = cache.get(target_season)
    if entry:
        is_finished_season = target_season != settings.CURRENT_SEASON
        ts = datetime.fromisoformat(entry["timestamp"])
        if is_finished_season or datetime.now() - ts < CACHE_TTL:
            return {
                "global_top": entry["global_top"],
                "global_top_250": entry["global_top_250"],
            }

    # Run scraper if cache is missing/expired for this season
    global_top, global_top_250 = get_top_points()

    cache[target_season] = {
        "timestamp": datetime.now().isoformat(),
        "global_top": global_top,
        "global_top_250": global_top_250,
    }
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

    return {"global_top": global_top, "global_top_250": global_top_250}
