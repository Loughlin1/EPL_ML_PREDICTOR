import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_matchweek():
    response = client.get("/api/matchweek")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "current_matchweek" in response.json()
