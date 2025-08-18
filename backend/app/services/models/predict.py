"""
backend/app/services/models/predict.py
"""
import json
import logging
import numpy as np
import pandas as pd
import hashlib
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler

from ...core.paths import (
    SAVED_MODELS_DIRECTORY,
)
from ..data_processing.data_loader import (
    clean_data, load_training_data, get_this_seasons_fixtures_data
)
from .config import FEATURES, LABELS
from .save_load import load_model, load_scaler
from .preprocess import preprocess_data, check_data
from ...db.database import get_session
from sqlalchemy.orm import Session
from ...db.models import Match, PredictionsCache


def assign_predictions(input_data: pd.DataFrame, future_scores) -> pd.DataFrame:
    input_data["PredScore"] = [f"{h}-{a}" for h, a in future_scores]
    input_data[["PredFTHG", "PredFTAG"]] = [(h, a) for h, a in future_scores]
    input_data["PredResult"] = [
        "H" if h > a else "D" if h == a else "A" for h, a in future_scores
    ]
    return input_data


def check_cache(match_ids: list, cache_duration_hours: float, db: Session) -> bool:
    """
    Check if all match_ids have valid cache entries.
    
    Args:
        match_ids: List of match IDs to check.
        cache_duration_hours: Cache validity in hours.
        db: SQLAlchemy session.
    
    Returns:
        True if all are cached and valid, else False.
    """
    cached_count = db.query(PredictionsCache).filter(
        PredictionsCache.match_id.in_(match_ids),
        PredictionsCache.timestamp >= datetime.utcnow() - timedelta(hours=cache_duration_hours)
    ).count()
    is_all_cached = cached_count == len(match_ids)
    # logger.info(f"All cached: {is_all_cached} ({cached_count}/{len(match_ids)})")
    return is_all_cached


def get_cached_predictions(match_ids: list, db: Session) -> list:
    """
    Retrieve cached predictions for all match_ids (assumes all are cached).
    
    Args:
        match_ids: List of match IDs.
        db: SQLAlchemy session.
    
    Returns:
        List of prediction dicts.
    """
    cached = db.query(PredictionsCache).filter(
        PredictionsCache.match_id.in_(match_ids)
    ).all()
    cached_dict = {c.match_id: c.to_dict() for c in cached}
    return [cached_dict[mid] for mid in match_ids]


def update_cache(predictions_df: pd.DataFrame, db: Session, logger: logging.Logger):
    """
    Cache predictions for given match IDs (update or insert).
    
    Args:
        predictions_df: DataFrame with match_id, PredFTHG, PredFTAG.
        db: SQLAlchemy session.
    """
    for _, row in predictions_df.iterrows():
        cache_entry = db.query(PredictionsCache).filter(
            PredictionsCache.match_id == row["match_id"]
        ).first()
        if cache_entry:
            cache_entry.pred_fthg = row["PredFTHG"]
            cache_entry.pred_ftag = row["PredFTAG"]
            cache_entry.pred_score = row["PredScore"]
            cache_entry.pred_result = row["PredResult"]
            cache_entry.timestamp = datetime.utcnow()
        else:
            cache_entry = PredictionsCache(
                match_id=row["match_id"],
                pred_fthg=row["PredFTHG"],
                pred_ftag=row["PredFTAG"],
                pred_score=row["PredScore"],
                pred_result=row["PredResult"],
            )
            db.add(cache_entry)
    db.commit()
    logger.info(f"Cached/Updated {len(predictions_df)} predictions")


def predict_pipeline(fixtures_df: pd.DataFrame, cache_duration_hours: int, logger: logging.Logger):
    """
    Generate predictions for new season fixtures using historical data for features.
    
    Returns:
        pd.DataFrame: Fixtures with predicted scores (PredFTHG, PredFTAG).
    """
    logger.info("Starting prediction pipeline")

    match_ids = fixtures_df["match_id"].tolist()

    with get_session() as db:
        # if check_cache(match_ids, cache_duration_hours, db):
        #     logger.info("Returning all cached predictions")
        #     predictions = get_cached_predictions(match_ids, db)
        #     result_df = fixtures_df.copy()
        #     predictions_df = pd.DataFrame(predictions, index=fixtures_df.index)
        #     result_df[["PredFTHG", "PredFTAG", "PredScore", "PredResult"]] = predictions_df[["pred_fthg", "pred_ftag", "pred_score", "pred_result"]]
        #     return result_df

        ### Rerun predictions for all

        # Load historical data for Elo and other features
        historical_df = load_training_data()
        historical_df = clean_data(historical_df)

        # Load new season fixtures
        fixtures_df = get_this_seasons_fixtures_data() 
        fixtures_df = clean_data(fixtures_df.drop(columns=["FTHG", "FTAG"], errors="ignore"))

        # Combine historical and new season data for consistent Elo calculation
        combined_df = pd.concat([historical_df, fixtures_df], ignore_index=True)
        combined_df = preprocess_data(combined_df, test_data=True)

        # Split back into historical and new season data
        new_season_df = combined_df.iloc[len(historical_df):].copy()

        # Select features
        X = new_season_df[FEATURES]
        print(X[["elo_h", "elo_a"]].head())
        check_data(X)

        # Scaling features
        scaler = load_scaler()
        X_scaled = scaler.transform(X)

        # Load model
        model = load_model(SAVED_MODELS_DIRECTORY, "best_model.joblib", "best_model_metadata.json")

        # Predictions
        if isinstance(model, dict):  # Single-output model (e.g., Poisson Regression)
            future_scores = np.column_stack([
                np.round(model["model_home"].predict(X_scaled)).astype(int),
                np.round(model["model_away"].predict(X_scaled)).astype(int)
            ])
        else:
            future_scores = np.round(model.predict(X_scaled)).astype(int)

        # Assign predictions
        new_season_df = assign_predictions(new_season_df, future_scores)

        # Update cache for all
        update_cache(new_season_df[["match_id", "PredFTHG", "PredFTAG", "PredScore", "PredResult"]], db, logger)

    # Return results
    result_df = fixtures_df.copy()
    result_df[["PredFTHG", "PredFTAG", "PredScore", "PredResult"]] = new_season_df[["PredFTHG", "PredFTAG", "PredScore", "PredResult"]]
    logger.info("Predictions generated successfully")
    return result_df
