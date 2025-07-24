from pydantic import BaseModel

class PredictRequest(BaseModel):
    home_team: str
    away_team: str

class PredictResponse(BaseModel):
    home_win: float
    draw: float
    away_win: float
    predicted_result: str