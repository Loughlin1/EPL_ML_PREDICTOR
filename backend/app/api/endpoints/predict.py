from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import json
import logging
import traceback

from app.services.models import predict as predictor
from app.schemas import MatchInput

router = APIRouter(
    tags=["Model"],
)
logger = logging.getLogger(__name__)

COLUMN_MAPPING = {
    "day": "Day",
    "date": "Date",
    "time": "Time",
    "home_team": "Home",
    "away_team": "Away",
    "Score": "Score",
    "Result": "Result",
    "PredScore": "PredScore",
    "PredResult": "PredResult",
    "venue": "Venue",
    "week": "week",
    "FTHG": "FTHG",
    "FTAG": "FTAG",
    "PredFTHG": "PredFTHG",
    "PredFTAG": "PredFTAG",
}


@router.post("/predict")
def predict_matches(request: MatchInput):
    try:
        df_input = pd.DataFrame(request.data)
        result_df = predictor.get_predictions(df_input, logger)
        result_df = result_df[COLUMN_MAPPING.keys()]
        result_df = result_df.rename(columns=COLUMN_MAPPING)
        # Map long venue name to short name
        result_df["Venue"] = result_df["Venue"].replace(
            "The American Express Community Stadium", "The AMEX"
        )
        return result_df.to_dict(orient="records")

    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Prediction failed: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/predict/base-model")
# def predict_matches(request: MatchInput):
#     try:
#         df_input = pd.DataFrame(request.data)
#         result_df = predictor.get_predictions(df_input, logger)
#         result_df.columns = result_df.columns.str.upper()
#         return result_df[COLUMNS].to_dict(orient="records")

#     except Exception as e:
#         logger.error(f"Prediction failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))
