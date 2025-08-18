from fastapi import APIRouter, HTTPException
import pandas as pd
import logging
import traceback

from ...services.models import predict as predictor
from ...schemas import MatchInput

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
    "result": "Result",
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
        print(df_input.head())
        predictions_df = predictor.predict_pipeline(
            df_input, cache_duration_hours=24, logger=logger
        )
        # Renaming columns
        predictions_df = predictions_df[COLUMN_MAPPING.keys()]
        predictions_df = predictions_df.rename(columns=COLUMN_MAPPING)
        # Map long venue name to short name
        predictions_df["Venue"] = predictions_df["Venue"].replace(
            "The American Express Community Stadium", "The AMEX"
        )
        predictions_df["Score"] = predictions_df["Score"].replace("None-None", "")
        return predictions_df.to_dict(orient="records")

    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Prediction failed: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))

