from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class MatchRow(BaseModel):
    Day: Optional[str] = None
    Date: Optional[str] = None
    Time: Optional[str] = None
    Home: Optional[str] = None
    Away: Optional[str] = None
    Score: Optional[str] = None
    Result: Optional[str] = None
    PredScore: Optional[str] = None
    PredResult: Optional[str] = None
    Venue: Optional[str] = None
    week: Optional[int] = None
    FTHG: Optional[Any] = None
    FTAG: Optional[Any] = None
    PredFTHG: Optional[Any] = None
    PredFTAG: Optional[Any] = None

    model_config = {"extra": "allow"}


class MatchweekResponse(BaseModel):
    matches: List[MatchRow]
    week_points: float


class ModelPerformance(BaseModel):
    MAE_Home: float = 0
    MAE_Away: float = 0
    MAE_Total: float = 0
    RMSE_Home: float = 0
    RMSE_Away: float = 0
    RMSE_Total: float = 0
    R2_Home: float = 0
    R2_Away: float = 0
    Correct_Results: int = 0
    Correct_Result_pct: float = 0
    Correct_Scores: int = 0
    Correct_Scores_pct: float = 0
    Goal_Difference_Accuracy: float = 0

    model_config = {"extra": "allow"}


class SeasonSummaryResponse(BaseModel):
    season: str
    superbru_points: float
    model_performance: Dict[str, Any]
    matches_played: int
    matches_total: int
    computed_at: str


class SeasonsResponse(BaseModel):
    seasons: List[str]


class SuperbruLeaderboardResponse(BaseModel):
    global_top: Any
    global_top_10_pct: Any
    uk_top_10_pct: Any


class TrainResponse(BaseModel):
    status: str
    message: str


class ValidationPerformanceResponse(BaseModel):
    model_config = {"extra": "allow"}
