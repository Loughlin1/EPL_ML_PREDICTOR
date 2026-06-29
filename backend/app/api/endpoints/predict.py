import logging

import pandas as pd
from fastapi import APIRouter

from ...core.config import settings
from ...schemas import MatchInput
from ...services.models import predict as predictor

router = APIRouter(tags=["Model"])
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

VENUE_ALIASES = {"The American Express Community Stadium": "The AMEX"}


@router.post("/predict")
def predict_matches(request: MatchInput):
    """Run prediction pipeline and return sanitised results."""
    season = request.season or settings.CURRENT_SEASON
    df_input = pd.DataFrame(request.data)
    predictions_df = predictor.predict_pipeline(
        df_input, cache_duration_hours=24, logger=logger, season=season
    )

    predictions_df = predictions_df[COLUMN_MAPPING.keys()].rename(columns=COLUMN_MAPPING)
    for long, short in VENUE_ALIASES.items():
        predictions_df["Venue"] = predictions_df["Venue"].replace(long, short)
    predictions_df["Score"] = predictions_df["Score"].replace("None-None", "")
    predictions_df = predictions_df.replace([float("inf"), float("-inf")], None).fillna("")

    return predictions_df.to_dict(orient="records")
