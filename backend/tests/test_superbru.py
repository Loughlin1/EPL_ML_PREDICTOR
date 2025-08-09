import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from ..app.core.paths import backend_dir


client = TestClient(app)

def test_calculate_superbru_points():
    with open(f"{backend_dir}/tests/example_predictions_data.json", "r") as f:
        data = json.load(f)
    payload = {
        "data": data
    }
    response = client.post("/api/superbru/points", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "points" in response.json()


def test_calculate_superbru_points():
    response = client.get("/api/superbru/points/top/global")
    assert response.status_code == 200
    resj = response.json()
    assert isinstance(resj, dict)
    assert "global_top" in resj
    assert "global_top_250" in resj
