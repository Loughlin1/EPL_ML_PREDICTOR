import logging

import pandas as pd
from fastapi import APIRouter

from ...schemas import MatchInput
from ...services.models.config import LABELS
from ...services.models.evaluation import evaluate_model, evaluate_model_performance

router = APIRouter(tags=["Model"])
logger = logging.getLogger(__name__)


@router.post("/evaluate")
def evaluate_matches(request: MatchInput):
    """Evaluate model performance against provided ground-truth match data."""
    df_input = pd.DataFrame(request.data)
    y_true = df_input[LABELS]
    y_pred = df_input[["PredFTHG", "PredFTAG"]].rename(
        columns={"PredFTHG": "FTHG", "PredFTAG": "FTAG"}
    )
    return evaluate_model_performance(y_true, y_pred)


@router.get("/evaluate/validation")
def evaluate_model_validation():
    """Run offline validation of the saved model against held-out data."""
    return evaluate_model()
