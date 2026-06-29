from typing import Union

from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_matchweek_includes_week_points():
    """Week points are now computed server-side inside the matchweek endpoint."""
    response = client.get(f"/api/seasons/{settings.CURRENT_SEASON}/matchweek/1")
    assert response.status_code == 200
    resj = response.json()
    assert "week_points" in resj
    assert isinstance(resj["week_points"], (int, float))
    assert "matches" in resj
    assert isinstance(resj["matches"], list)


def test_retrieve_superbru_leaderboard_points():
    response = client.get("/api/superbru/points/top/global")
    assert response.status_code == 200
    resj = response.json()
    assert isinstance(resj, dict)
    assert "global_top" in resj
    assert isinstance(resj["global_top"], Union[int, float])
    assert "global_top_10_pct" in resj
    assert isinstance(resj["global_top_10_pct"], Union[int, float])
    assert "uk_top_10_pct" in resj
    assert isinstance(resj["uk_top_10_pct"], Union[int, float])
