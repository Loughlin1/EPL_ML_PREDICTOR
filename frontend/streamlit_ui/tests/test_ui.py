import os

import pytest
from streamlit.testing.v1 import AppTest


# Dynamically compute the path to Home.py (your Streamlit app)
@pytest.fixture
def sample_script_path():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(current_dir)
    return os.path.join(parent_dir, "Home.py")


def test_streamlit_runs_without_errors(sample_script_path):
    app = AppTest.from_file(sample_script_path)
    app.run()
    assert app.exception is None, "Streamlit app raised an exception"
    assert app.status == "COMPLETE", "Streamlit app did not complete execution"


def test_streamlit_renders_ui(sample_script_path):
    app = AppTest.from_file(sample_script_path)
    app.run()
    assert app.status == "COMPLETE", "Streamlit app failed to complete"
    assert app.deltas, "No UI elements rendered (deltas are empty)"


def test_streamlit_no_exceptions(sample_script_path):
    app = AppTest.from_file(sample_script_path)
    app.run()
    assert app.exception is None, "Streamlit app raised an exception"


def test_streamlit_fetches_prediction(sample_script_path, mocker):
    # Mock the response from requests.get
    mock_response = {"prediction": "Sample prediction"}
    mocker.patch(
        "requests.get",
        return_value=mocker.Mock(status_code=200, json=lambda: mock_response),
    )

    app = AppTest.from_file(sample_script_path)
    app.run()

    assert app.status == "COMPLETE", "Streamlit app failed to run"
    assert app.deltas, "No UI elements rendered"

    # Optional: Check if the prediction string appears
    prediction_found = any("Sample prediction" in str(delta) for delta in app.deltas)
    assert prediction_found, "Prediction not found in UI output"
