from fastapi import APIRouter, HTTPException
import pandas as pd
import logging
import json
import os
from datetime import datetime, timedelta
from app.schemas import MatchInput
from app.services.utils.superbru_points_calculator import get_superbru_points
from app.services.web_scraping.superbru.leaderboard_scraper import get_top_points

from app.core.config.paths import SUPERBRU_LEADERBOARD_CACHE as CACHE_PATH

router = APIRouter()
logger = logging.getLogger(__name__)

CACHE_TTL = timedelta(days=90) #timedelta(hours=1)

@router.post("/superbru/points")
def calculate_superbru_points(request: MatchInput):
    """
    Calculate the number of SuperBru points for predictions
    """
    try:
        df_input = pd.DataFrame(request.data)
        points = get_superbru_points(df_input)
        return {"points": points}
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/superbru/points/top/global")
def get_leaderboard_points():
    """
    Get the top global points on SuperBru leaderboard.
    """
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            cache = json.load(f)
            ts = datetime.fromisoformat(cache["timestamp"])
            if datetime.now() - ts < CACHE_TTL:
                return {
                    "global_top": cache["global_top"],
                    "global_top_250": cache["global_top_250"]
                }
    # Run scraper if cache is missing/expired
    global_top, global_top_250 = get_top_points()
    # Ensure directory exists
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

    with open(CACHE_PATH, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "global_top": global_top,
            "global_top_250": global_top_250
        }, f)
    return {
        "global_top": global_top,
        "global_top_250": global_top_250
    }
