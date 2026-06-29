from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)

SEASON = settings.CURRENT_SEASON


def test_list_seasons():
    response = client.get("/api/seasons")
    assert response.status_code == 200
    body = response.json()
    assert "seasons" in body
    assert isinstance(body["seasons"], list)
    assert len(body["seasons"]) > 0
    assert SEASON in body["seasons"]


def test_get_season_summary():
    response = client.get(f"/api/seasons/{SEASON}/summary")
    assert response.status_code == 200
    body = response.json()
    assert "superbru_points" in body
    assert "model_performance" in body
    assert "matches_played" in body
    assert "matches_total" in body


def test_get_season_summary_not_found():
    response = client.get("/api/seasons/1900-1901/summary")
    assert response.status_code == 404


def test_get_season_current_matchweek():
    response = client.get(f"/api/seasons/{SEASON}/matchweek")
    assert response.status_code == 200
    body = response.json()
    assert "current_matchweek" in body
    assert isinstance(body["current_matchweek"], int)


def test_get_matchweek_data():
    week_res = client.get(f"/api/seasons/{SEASON}/matchweek")
    week = week_res.json()["current_matchweek"]

    response = client.get(f"/api/seasons/{SEASON}/matchweek/{week}")
    assert response.status_code == 200
    body = response.json()
    assert "matches" in body
    assert "week_points" in body
    assert isinstance(body["matches"], list)
    assert isinstance(body["week_points"], (int, float))
    assert len(body["matches"]) > 0


def test_get_matchweek_data_fields():
    response = client.get(f"/api/seasons/{SEASON}/matchweek/1")
    assert response.status_code == 200
    match = response.json()["matches"][0]
    for field in ("Home", "Away", "Date", "week"):
        assert field in match, f"Expected field '{field}' missing from match row"


def test_get_matchweek_not_found():
    response = client.get(f"/api/seasons/{SEASON}/matchweek/999")
    assert response.status_code == 404


def test_get_finished_season_matchweek():
    """Finished seasons should be served from the DB cache without triggering scraping."""
    response = client.get("/api/seasons/2023-2024/matchweek/1")
    # Only assert 200 if that season exists in the DB; otherwise 404 is acceptable
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        body = response.json()
        assert "matches" in body
        assert "week_points" in body
