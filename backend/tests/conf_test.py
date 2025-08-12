# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

import os

os.environ["SUPERBRU_TARGET_URL"] = ""
os.environ["USERNAME"] = ""
os.environ["PASSWORD"] = ""
os.environ["FOOTBALL_DATA_BASE_URL"] = ""


@pytest.fixture(scope="module")
def client():
    return TestClient(app)
