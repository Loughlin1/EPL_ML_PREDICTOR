from typing import List, Dict, Any
from pydantic import BaseModel


class PredictRequest(BaseModel):
    home_team: str
    away_team: str


class PredictResponse(BaseModel):
    home_win: float
    draw: float
    away_win: float
    predicted_result: str


class MatchInput(BaseModel):
    data: List[Dict[str, Any]]  # List of match data rows
