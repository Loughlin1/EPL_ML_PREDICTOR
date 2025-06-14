import pytest
from streamlit.testing import TestRunner
from streamlit.runtime.scriptrunner import ScriptRunnerEvent

# Mock function to simulate running a Streamlit script
def run_streamlit_script(script_path):
    runner = TestRunner(script_path)
    runner.start()
    events = list(runner.get_events())
    runner.stop()
    return events

@pytest.fixture
def sample_script_path():
    # Replace with the actual path to your Streamlit script
    return "/Users/loughlindavidson/Documents/development/EPL_project/EPL_ML_PREDICTOR/frontend/app.py"

def test_streamlit_script_runs_without_errors(sample_script_path):
    events = run_streamlit_script(sample_script_path)
    assert any(event.name == ScriptRunnerEvent.SCRIPT_STARTED for event in events), "Script did not start"
    assert any(event.name == ScriptRunnerEvent.SCRIPT_STOPPED for event in events), "Script did not stop"

def test_streamlit_ui_elements_render(sample_script_path):
    events = run_streamlit_script(sample_script_path)
    assert any(event.name == ScriptRunnerEvent.DELTA_GENERATED for event in events), "UI elements were not rendered"

def test_streamlit_no_exceptions(sample_script_path):
    events = run_streamlit_script(sample_script_path)
    assert not any(event.name == ScriptRunnerEvent.SCRIPT_EXCEPTION_RAISED for event in events), "Script raised an exception"

def test_streamlit_fetches_prediction(sample_script_path, mocker):
    mock_response = {"prediction": "Sample prediction"}
    mocker.patch("requests.get", return_value=mocker.Mock(status_code=200, json=lambda: mock_response))
    
    events = run_streamlit_script(sample_script_path)
    assert any(event.name == ScriptRunnerEvent.DELTA_GENERATED for event in events), "UI elements were not rendered"
    # Additional assertions can be added to verify the prediction is displayed