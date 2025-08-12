import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_fixtures():
    response = client.get("/api/fixtures")
    assert response.status_code == 200
    fixtures = response.json()
    assert isinstance(fixtures, list)
    assert "home_team" in fixtures[0]
    assert "away_team" in fixtures[0]


def test_get_fixtures_with_matchweek():
    matchweek = 2
    response = client.get(f"/api/fixtures?matchweek={matchweek}")
    assert response.status_code == 200
    fixtures = response.json()
    assert isinstance(fixtures, list)
    assert "home_team" in fixtures[0]
    assert "away_team" in fixtures[0]
    assert fixtures[0]["week"] == matchweek
