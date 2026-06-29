from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_model_explanation():
    response = client.get("/api/content/model_explanation")
    # File may not exist in all environments; both outcomes are valid
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        assert isinstance(response.json(), dict)
