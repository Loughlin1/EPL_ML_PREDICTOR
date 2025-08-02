from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import json
import logging
import traceback

from app.services.models import predict as predictor
from app.schemas import MatchInput
from app.services.models.evaluation import (
    calc_correct_result_percentage,
    calc_correct_score_percentage,
    evaluate_model,
    evaluate_model_performance
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/evaluate")
def evaluate_matches(request: MatchInput):
    try:
        df_input = pd.DataFrame(request.data)
        y_true = df_input[["FTHG", "FTAG"]]
        y_pred = df_input[["PredFTHG", "PredFTAG"]].rename(columns={"PredFTHG": "FTHG", "PredFTAG": "FTAG"})
        return evaluate_model_performance(y_true, y_pred)
        # score_perc = calc_correct_score_percentage(df_input)
        # result_perc = calc_correct_result_percentage(df_input)
        # return {
        #     "CorrectScores": np.round(score_perc,2),
        #     "CorrectResults": np.round(result_perc,2),
        # }

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
    