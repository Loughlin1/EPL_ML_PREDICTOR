import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_predict_endpoint():
    data = client.get("/api/fixtures").json()
    payload = {"data": data}
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    result = response.json()

    assert isinstance(result, list)
    assert "PredScore" in result[0]
    assert "PredResult" in result[0]
