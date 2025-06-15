from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the EPL Predictor API"}


def test_predict():
    response = client.get("/predict")
    assert response.status_code == 200
    assert "prediction" in response.json()
