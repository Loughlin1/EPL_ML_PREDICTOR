import os

FRONTEND_PORT = 8501
BACKEND_PORT = 8000
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"


current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

# ENCODERS
TEAMS_IDS_2024_FILEPATH = f"{current_dir}/encoders/team_ids_2024-25.json"
TEAMS_IDS_TRAINING_FILEPATH = f"{current_dir}/encoders/team_ids.json"

TEAMS_2024_FILEPATH = f"{current_dir}/encoders/teams_2024.json"
TEAMS_TRAINING_FILEPATH = f"{current_dir}/encoders/training_teams.json"

VENUE_ENCODER_FILEPATH = f"{current_dir}/encoders/venue_encoder.pkl"
TEAM_ENCODER_FILEPATH = f"{current_dir}/encoders/team_encoder.pkl"


# DATA
SHOOTING_TRAINING_DATA_DIR = f"{parent_dir}/data/shooting_data"
SHOOTING_TEST_DATA_DIR = f"{parent_dir}/data/shooting_data_2024"

FIXTURES_TRAINING_DATA_DIR = f"{parent_dir}/data/fixtures_training_data"
FIXTURES_TEST_DATA_FILEPATH = f"{parent_dir}/data/fixtures_test_data/2024-25.csv"
