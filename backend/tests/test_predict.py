import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from ..app.core.paths import backend_dir

client = TestClient(app)

def test_predict_endpoint():

    with open(f"{backend_dir}/tests/example_fixtures_data.json", "r") as f:
        data = json.load(f)
    payload = {
        "data": data
    }

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    result = response.json()

    assert isinstance(result, list)
    assert "PredScore" in result[0]
    assert "PredResult" in result[0]