from fastapi import APIRouter, HTTPException
from app.services.models.train import train_model
import logging
import traceback

router = APIRouter(
    tags=["Model"],
)
logger = logging.getLogger(__name__)


@router.post("/train")
def run_training():
    try:
        result = train_model()
        return result
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Training failed: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))
