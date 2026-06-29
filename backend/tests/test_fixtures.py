from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_fixtures():
    response = client.get("/api/fixtures")
    assert response.status_code == 200
    fixtures = response.json()
    assert isinstance(fixtures, list)
    assert len(fixtures) > 0
    assert "home_team" in fixtures[0]
    assert "away_team" in fixtures[0]
    assert "week" in fixtures[0]


def test_get_fixtures_with_matchweek():
    matchweek = 2
    response = client.get(f"/api/fixtures?matchweek={matchweek}")
    assert response.status_code == 200
    fixtures = response.json()
    assert isinstance(fixtures, list)
    assert len(fixtures) > 0
    assert all(f["week"] == matchweek for f in fixtures)


def test_get_fixtures_with_season():
    from app.core.config import settings
    response = client.get(f"/api/fixtures?season={settings.CURRENT_SEASON}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_seasons():
    response = client.get("/api/seasons")
    assert response.status_code == 200
    body = response.json()
    assert "seasons" in body
    assert isinstance(body["seasons"], list)
    assert len(body["seasons"]) > 0


def test_get_teams():
    response = client.get("/api/teams")
    assert response.status_code == 200
    body = response.json()
    assert "teams" in body
    assert isinstance(body["teams"], list)
    assert len(body["teams"]) > 0
