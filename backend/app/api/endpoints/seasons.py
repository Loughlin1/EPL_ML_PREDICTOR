import logging
import traceback

import pandas as pd
from fastapi import APIRouter, HTTPException

from ...core.config import settings
from ...db.database import get_session
from ...db.queries import get_matchweek_with_predictions, get_season_match_ids
from ...services.data_processing.data_loader import get_this_seasons_fixtures_data
from ...services.models.predict import check_cache, predict_pipeline
from ...services.models.summary import get_or_compute_summary
from ...services.utils.matchweek import get_current_matchweek
from ...services.utils.superbru_points_calculator import get_superbru_points

router = APIRouter(prefix="/seasons", tags=["Seasons"])
logger = logging.getLogger(__name__)

COLUMN_MAPPING = {
    "day": "Day",
    "date": "Date",
    "time": "Time",
    "home_team": "Home",
    "away_team": "Away",
    "Score": "Score",
    "result": "Result",
    "PredScore": "PredScore",
    "PredResult": "PredResult",
    "venue": "Venue",
    "week": "week",
    "FTHG": "FTHG",
    "FTAG": "FTAG",
    "PredFTHG": "PredFTHG",
    "PredFTAG": "PredFTAG",
}


def _sanitise(records: list) -> list:
    df = pd.DataFrame(records)
    df = df.replace([float("inf"), float("-inf")], None)
    df = df.fillna("")
    return df.to_dict(orient="records")


def _ensure_predictions_cached(season: str) -> None:
    """For current season: run full predict pipeline if predictions aren't cached yet."""
    match_ids = get_season_match_ids(season)
    if not match_ids:
        return
    with get_session() as db:
        if not check_cache(match_ids, cache_duration_hours=24, db=db):
            fixtures_df = get_this_seasons_fixtures_data(season=season)
            predict_pipeline(fixtures_df, cache_duration_hours=24, logger=logger, season=season)


@router.get("/{season}/summary")
def get_season_summary(season: str):
    """
    Return pre-computed season summary (superbru points, model performance).
    Finished seasons are served from cache instantly. Current season is computed live.
    """
    try:
        summary = get_or_compute_summary(season, current_season=settings.CURRENT_SEASON)
        if not summary:
            raise HTTPException(status_code=404, detail=f"No data found for season {season}")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{season}/matchweek")
def get_season_current_matchweek(season: str):
    """Return the current/most recent matchweek for a season."""
    try:
        fixtures = get_this_seasons_fixtures_data(season=season)
        week = get_current_matchweek(fixtures)
        return {"current_matchweek": week}
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{season}/matchweek/{week}")
def get_matchweek(season: str, week: int):
    """
    Return fixtures and predictions for a single matchweek.

    For finished seasons predictions are read directly from the DB cache.
    For the current season the prediction pipeline is triggered if needed.
    """
    try:
        if season == settings.CURRENT_SEASON:
            _ensure_predictions_cached(season)

        rows = get_matchweek_with_predictions(season=season, week=week)
        if not rows:
            raise HTTPException(
                status_code=404, detail=f"No data for {season} matchweek {week}"
            )

        df = pd.DataFrame(rows)

        # Compute superbru points for this week server-side
        try:
            points_df = df.rename(columns={"result": "Result"})
            week_points = get_superbru_points(points_df)
        except Exception:
            week_points = 0

        # Keep only columns that exist in both the data and COLUMN_MAPPING
        cols = [k for k in COLUMN_MAPPING if k in df.columns]
        df = df[cols].rename(columns=COLUMN_MAPPING)
        df["Score"] = df["Score"].replace("None-None", "")
        df["Venue"] = df["Venue"].replace("The American Express Community Stadium", "The AMEX")

        return {"matches": _sanitise(df.to_dict(orient="records")), "week_points": week_points}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
