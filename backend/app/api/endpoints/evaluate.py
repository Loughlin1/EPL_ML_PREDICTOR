from fastapi import APIRouter, HTTPException
import pandas as pd
import logging
import traceback

from ...schemas import MatchInput
from ...services.models.evaluation import evaluate_model, evaluate_model_performance
from ...services.models.config import LABELS

router = APIRouter(
    tags=["Model"],
)
logger = logging.getLogger(__name__)


@router.post("/evaluate")
def evaluate_matches(request: MatchInput):
    try:
        df_input = pd.DataFrame(request.data)
        y_true = df_input[LABELS]
        y_pred = df_input[["PredFTHG", "PredFTAG"]].rename(
            columns={"PredFTHG": "FTHG", "PredFTAG": "FTAG"}
        )
        return evaluate_model_performance(y_true, y_pred)

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/evaluate/validation")
def evaluate_model_validation():
    try:
        results = evaluate_model()
        return results

    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Evaluation failed: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))
