from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EXPECTED_FIELDS = ("Home", "Away", "PredScore", "PredResult", "PredFTHG", "PredFTAG")


def test_predict_endpoint():
    data = client.get("/api/fixtures").json()
    response = client.post("/api/predict", json={"data": data})
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) > 0
    for field in EXPECTED_FIELDS:
        assert field in result[0], f"Expected field '{field}' missing from prediction"


def test_predict_with_season():
    from app.core.config import settings
    data = client.get("/api/fixtures").json()
    response = client.post("/api/predict", json={"data": data, "season": settings.CURRENT_SEASON})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_predict_no_nan_in_scores():
    """Prediction scores should never be NaN or Inf — they should be empty string or a value."""
    data = client.get("/api/fixtures").json()
    result = client.post("/api/predict", json={"data": data}).json()
    for row in result:
        assert row.get("PredFTHG") != float("inf")
        assert row.get("PredFTAG") != float("inf")
