import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config.paths import backend_dir
client = TestClient(app)

def test_get_fixtures():
    response = client.get("/api/fixtures")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert "Home" in response.json()[0]
