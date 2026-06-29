"""
Shared test fixtures and mocks for all test modules.

All external I/O (database, ML model artifacts, scrapers, cache files) is
mocked at the import boundary so the test suite runs cleanly in CI without
any local database, trained models, or data files.
"""

import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_epl.db")
os.environ.setdefault("FOOTBALL_DATA_BASE_URL", "")
os.environ.setdefault("SUPERBRU_TARGET_URL", "")
os.environ.setdefault("SUPERBRU_USERNAME", "")
os.environ.setdefault("SUPERBRU_PASSWORD", "")

from app.main import app  # noqa: E402  (env vars must be set first)
from app.core.config import settings  # noqa: E402

SEASON = settings.CURRENT_SEASON

# ---------------------------------------------------------------------------
# Canonical test data
# ---------------------------------------------------------------------------

_FIXTURE_ROWS = [
    {
        "match_id": 1, "season": SEASON, "week": 1,
        "day": "Sat", "date": "2024-08-17", "time": "15:00",
        "home_team": "Arsenal", "away_team": "Wolves",
        "home_team_fullname": "Arsenal FC", "away_team_fullname": "Wolverhampton Wanderers",
        "Score": "2-1", "FTHG": 2, "FTAG": 1, "result": "H",
        "venue": "Emirates Stadium",
        "PredScore": "2-1", "PredResult": "H", "PredFTHG": 2, "PredFTAG": 1,
    },
    {
        "match_id": 2, "season": SEASON, "week": 1,
        "day": "Sat", "date": "2024-08-17", "time": "17:30",
        "home_team": "Chelsea", "away_team": "Manchester City",
        "home_team_fullname": "Chelsea FC", "away_team_fullname": "Manchester City FC",
        "Score": "1-2", "FTHG": 1, "FTAG": 2, "result": "A",
        "venue": "Stamford Bridge",
        "PredScore": "1-1", "PredResult": "D", "PredFTHG": 1, "PredFTAG": 1,
    },
    {
        "match_id": 3, "season": SEASON, "week": 2,
        "day": "Sat", "date": "2024-08-24", "time": "15:00",
        "home_team": "Arsenal", "away_team": "Chelsea",
        "home_team_fullname": "Arsenal FC", "away_team_fullname": "Chelsea FC",
        "Score": "1-0", "FTHG": 1, "FTAG": 0, "result": "H",
        "venue": "Emirates Stadium",
        "PredScore": "1-0", "PredResult": "H", "PredFTHG": 1, "PredFTAG": 0,
    },
]

MOCK_FIXTURES_DF = pd.DataFrame(_FIXTURE_ROWS)

MOCK_PREDICT_DF = MOCK_FIXTURES_DF.copy()

MOCK_SEASONS = [SEASON]

MOCK_TEAMS = [
    {"team_id": 1, "name": "Arsenal", "fullname": "Arsenal FC", "fbref_team_id": "abc1"},
    {"team_id": 2, "name": "Wolves", "fullname": "Wolverhampton Wanderers", "fbref_team_id": "abc2"},
    {"team_id": 3, "name": "Chelsea", "fullname": "Chelsea FC", "fbref_team_id": "abc3"},
    {"team_id": 4, "name": "Manchester City", "fullname": "Manchester City FC", "fbref_team_id": "abc4"},
]

MOCK_SUMMARY = {
    "season": SEASON,
    "superbru_points": 329.0,
    "matches_played": 30,
    "matches_total": 38,
    "model_name": "RandomForest",
    "model_performance": {
        "MAE_Home": 0.9,
        "MAE_Away": 0.85,
        "MAE_Total": 0.875,
        "Correct_Result_%": 52.0,
        "Correct_Scores_%": 12.0,
        "Correct_Results": 15,
        "Correct_Scores": 3,
    },
}

MOCK_MATCHWEEK = {
    "matches": _FIXTURE_ROWS,
    "week_points": 11.5,
}

MOCK_LEADERBOARD = {
    "global_top": 752.0,
    "global_top_10_pct": 525.0,
    "uk_top_10_pct": 548.0,
}


# ---------------------------------------------------------------------------
# Session-scoped autouse mock — covers the entire test run
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def mock_all_io():
    """
    Patch every external I/O boundary for the duration of the test session.
    Patches are applied at each module's local import binding.
    """
    patches = [
        # --- DB / fixtures ---
        patch("app.api.endpoints.fixtures.get_this_seasons_fixtures_data", return_value=MOCK_FIXTURES_DF),
        patch("app.api.endpoints.fixtures.get_available_seasons", return_value=MOCK_SEASONS),
        patch("app.api.endpoints.fixtures.db_get_teams", return_value=MOCK_TEAMS),
        patch("app.api.endpoints.fixtures.check_missing_results", return_value=False),
        patch("app.api.endpoints.fixtures.scrape_and_save_fixtures"),
        patch("app.api.endpoints.fixtures.scrape_and_save_shooting_stats"),

        # --- Seasons ---
        patch("app.api.endpoints.seasons.get_available_seasons", return_value=MOCK_SEASONS),
        patch("app.api.endpoints.seasons.get_this_seasons_fixtures_data", return_value=MOCK_FIXTURES_DF),
        patch(
            "app.api.endpoints.seasons.get_or_compute_summary",
            side_effect=lambda season, **kw: MOCK_SUMMARY if season == SEASON else None,
        ),
        patch(
            "app.services.seasons_service.get_matchweek",
            side_effect=lambda season, week: None if week == 999 else MOCK_MATCHWEEK,
        ),

        # --- Matchweek ---
        patch("app.api.endpoints.matchweek.get_this_seasons_fixtures_data", return_value=MOCK_FIXTURES_DF),

        # --- Predict ---
        patch("app.api.endpoints.predict.predictor.predict_pipeline", return_value=MOCK_PREDICT_DF),

        # --- Train ---
        patch("app.api.endpoints.train.train_model", return_value={"status": "success", "message": "Training complete"}),

        # --- Superbru ---
        patch("app.services.superbru_service.get_leaderboard", return_value=MOCK_LEADERBOARD),
    ]

    started = [p.start() for p in patches]
    yield
    for p in patches:
        p.stop()


@pytest.fixture(scope="session")
def client():
    return TestClient(app)
