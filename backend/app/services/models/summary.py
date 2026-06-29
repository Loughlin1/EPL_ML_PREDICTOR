"""
summary.py

Compute and cache season-level summary statistics (superbru points,
model performance) so they don't need to be recalculated on every request.
"""

import json
from datetime import datetime

import pandas as pd

from ...core.paths import SEASON_SUMMARIES_CACHE
from ...db.queries import get_season_with_predictions
from ..utils.superbru_points_calculator import get_superbru_points
from .evaluation import evaluate_model_performance
from .save_load import load_model_for_season


def _get_model_name(season: str) -> str:
    try:
        model = load_model_for_season(season)
        if hasattr(model, "home_model"):  # GoalPredictor wrapper
            return model.home_model.__class__.__name__
        if isinstance(model, dict):
            return next(iter(model.values())).__class__.__name__
        return model.__class__.__name__
    except Exception:
        return "Unknown"


def _load_cache() -> dict:
    if SEASON_SUMMARIES_CACHE.exists():
        with open(SEASON_SUMMARIES_CACHE) as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict) -> None:
    SEASON_SUMMARIES_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEASON_SUMMARIES_CACHE, "w") as f:
        json.dump(cache, f, indent=2)


def compute_season_summary(season: str) -> dict:
    """Compute superbru points and model performance for a full season."""
    rows = get_season_with_predictions(season)
    if not rows:
        return {}

    df = pd.DataFrame(rows)

    # Model performance — only on played matches
    played = df.dropna(subset=["FTHG", "FTAG", "PredFTHG", "PredFTAG"])
    if played.empty:
        model_performance = {}
        superbru_points = 0
    else:
        y_true = played[["FTHG", "FTAG"]].rename(columns={"FTHG": "FTHG", "FTAG": "FTAG"})
        y_pred = played[["PredFTHG", "PredFTAG"]].rename(
            columns={"PredFTHG": "FTHG", "PredFTAG": "FTAG"}
        )
        model_performance = evaluate_model_performance(y_true, y_pred)

        # Superbru points require Result + PredResult columns
        if "result" in df.columns and "PredResult" in df.columns:
            points_df = df.rename(columns={"result": "Result"})
            try:
                superbru_points = get_superbru_points(points_df)
            except Exception:
                superbru_points = 0
        else:
            superbru_points = 0

    return {
        "season": season,
        "superbru_points": superbru_points,
        "model_performance": model_performance,
        "model_name": _get_model_name(season),
        "matches_played": len(played),
        "matches_total": len(df),
        "computed_at": datetime.utcnow().isoformat(),
    }


def get_or_compute_summary(season: str, current_season: str, force: bool = False) -> dict:
    """
    Return cached summary for finished seasons (never expires).
    For the current season recomputes every time (live data).
    """
    is_finished = season != current_season

    if is_finished and not force:
        cache = _load_cache()
        if season in cache:
            return cache[season]

    summary = compute_season_summary(season)

    if is_finished and summary:
        cache = _load_cache()
        cache[season] = summary
        _save_cache(cache)

    return summary


def save_summary_for_season(season: str) -> dict:
    """Called from the training pipeline to pre-compute and persist the summary."""
    summary = compute_season_summary(season)
    if summary:
        cache = _load_cache()
        cache[season] = summary
        _save_cache(cache)
    return summary
