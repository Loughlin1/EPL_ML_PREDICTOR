import logging

from fastapi import APIRouter

from ...schemas import TrainResponse
from ...services.models.train import train_model

router = APIRouter(tags=["Model"])
logger = logging.getLogger(__name__)


@router.post("/train", response_model=TrainResponse)
def run_training(season: str = None):
    """
    Train a model. If `season` is provided (e.g. "2024-2025"), trains on all data
    before that season and saves season-scoped artifacts. Otherwise trains on all
    available data and saves the default model for the current season.
    """
    return train_model(season=season)
