"""
seasons_service.py

Business logic for season and matchweek data retrieval, isolated from the endpoint layer.
"""

import logging

import pandas as pd

from ..core.config import settings
from ..db.database import get_session
from ..db.queries import get_matchweek_with_predictions, get_season_match_ids
from ..services.data_processing.data_loader import get_this_seasons_fixtures_data
from ..services.models.predict import check_cache, predict_pipeline
from ..services.utils.superbru_points_calculator import get_superbru_points

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

VENUE_ALIASES = {
    "The American Express Community Stadium": "The AMEX",
}


def ensure_predictions_cached(season: str) -> None:
    """Run the full predict pipeline for the current season if predictions aren't cached yet."""
    match_ids = get_season_match_ids(season)
    if not match_ids:
        return
    with get_session() as db:
        if not check_cache(match_ids, cache_duration_hours=24, db=db):
            logger.info("Prediction cache stale for %s — running pipeline", season)
            fixtures_df = get_this_seasons_fixtures_data(season=season)
            predict_pipeline(
                fixtures_df, cache_duration_hours=24, logger=logger, season=season
            )


def get_matchweek(season: str, week: int) -> dict:
    """
    Return sanitised match rows and superbru points for a single matchweek.

    For finished seasons predictions are read directly from the DB.
    For the current season the prediction pipeline is triggered if needed.
    """
    if season == settings.CURRENT_SEASON:
        ensure_predictions_cached(season)

    rows = get_matchweek_with_predictions(season=season, week=week)
    if not rows:
        return None

    df = pd.DataFrame(rows)

    try:
        points_df = df.rename(columns={"result": "Result"})
        week_points = get_superbru_points(points_df)
    except Exception:
        week_points = 0

    cols = [k for k in COLUMN_MAPPING if k in df.columns]
    df = df[cols].rename(columns=COLUMN_MAPPING)
    df["Score"] = df["Score"].replace("None-None", "")
    for long, short in VENUE_ALIASES.items():
        df["Venue"] = df["Venue"].replace(long, short)

    df = df.replace([float("inf"), float("-inf")], None)
    df = df.fillna("")

    return {"matches": df.to_dict(orient="records"), "week_points": week_points}
