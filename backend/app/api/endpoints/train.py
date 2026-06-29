import logging
import traceback

from fastapi import APIRouter, HTTPException

from ...services.models.train import train_model

router = APIRouter(
    tags=["Model"],
)
logger = logging.getLogger(__name__)


@router.post("/train")
def run_training(season: str = None):
    """
    Train a model. If `season` is provided (e.g. "2024-2025"), trains on all data
    before that season and saves season-scoped artifacts. Otherwise trains on all
    available data and saves the default model used for the current season.
    """
    try:
        result = train_model(season=season)
        return result
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Training failed: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))
