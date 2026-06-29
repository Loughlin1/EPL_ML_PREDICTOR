from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EXPECTED_METRICS = ("MAE_Home", "MAE_Away", "MAE_Total", "Correct_Result_%", "Correct_Scores_%")


def test_post_evaluate_matches():
    fixtures = client.get("/api/fixtures").json()
    predictions = client.post("/api/predict", json={"data": fixtures}).json()
    response = client.post("/api/evaluate", json={"data": predictions})
    assert response.status_code == 200
    evaluation = response.json()
    assert isinstance(evaluation, dict)
    for metric in EXPECTED_METRICS:
        assert metric in evaluation, f"Expected metric '{metric}' missing"
        assert isinstance(evaluation[metric], (int, float))


def test_get_evaluate_model_validation():
    response = client.get("/api/evaluate/validation")
    assert response.status_code == 200
    evaluation = response.json()
    assert isinstance(evaluation, dict)
    for metric in EXPECTED_METRICS:
        assert metric in evaluation, f"Expected metric '{metric}' missing"
        assert isinstance(evaluation[metric], (int, float))
