import pytest
from typing import Union
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_calculate_superbru_points():
    fixtures = client.get("/api/fixtures").json()
    data = client.post("/api/predict", json={"data": fixtures}).json()

    payload = {"data": data}
    response = client.post("/api/superbru/points", json=payload)
    assert response.status_code == 200
    resj = response.json()
    assert isinstance(resj, dict)
    assert "points" in resj
    assert isinstance(resj["points"], float)


def test_retrieve_superbru_leaderboard_points():
    response = client.get("/api/superbru/points/top/global")
    assert response.status_code == 200
    resj = response.json()
    assert isinstance(resj, dict)
    assert "global_top" in resj
    assert isinstance(resj["global_top"], Union[int, float])
    assert "global_top_250" in resj
    assert isinstance(resj["global_top_250"], Union[int, float])
