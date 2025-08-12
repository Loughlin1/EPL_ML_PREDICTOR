from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_train_endpoint():
    response = client.post("/api/train")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
