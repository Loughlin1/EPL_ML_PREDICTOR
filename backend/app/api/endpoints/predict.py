from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import json
import logging

from app.services.models import predict as predictor
from app.core.config.paths import TEAMS_2024_FILEPATH
from app.schemas import MatchInput

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict")
def predict_matches(request: MatchInput):
    try:
        # Convert JSON list to DataFrame
        df_input = pd.DataFrame(request.data)

        # Run the model
        result_df = predictor.get_predictions(df_input, logger)

        # Return selected columns
        return result_df.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/base-model")
def predict_matches(request: MatchInput):
    try:
        # Convert JSON list to DataFrame
        df_input = pd.DataFrame(request.data)

        # Run the model
        result_df = predictor.get_predictions(df_input, logger)

        # Return selected columns
        return result_df.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams")
def get_teams():
    try:
        with open(TEAMS_2024_FILEPATH, "r") as f:
            teams = json.load(f)
        return {"teams": teams}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load teams: {str(e)}")
