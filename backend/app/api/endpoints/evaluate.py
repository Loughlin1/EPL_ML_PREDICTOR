from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import json
import logging

from app.services.models import predict as predictor
from app.schemas import MatchInput

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/evaluate")
def predict_matches(request: MatchInput):
    try:
        # Convert JSON list to DataFrame
        df_input = pd.DataFrame(request.data)
        total_predictions = df_input['Score'].count()
        if total_predictions == 0:
            score_perc = 0
            result_perc = 0
        else:   
            score_perc = 100*(len(df_input.loc[df_input["Score"] == df_input["PredScore"], :])) / total_predictions
            result_perc = 100*(len(df_input.loc[df_input["Result"] == df_input["PredResult"], :])) / total_predictions
        return {"CorrectScores": np.round(score_perc,2), "CorrectResults": np.round(result_perc,2)}

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

