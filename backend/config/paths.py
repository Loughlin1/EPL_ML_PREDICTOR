import os

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

# ENCODERS
TEAMS_IDS_2024_FILEPATH = f"{parent_dir}/artifacts/encoders/team_ids_2024-25.json"
TEAMS_IDS_TRAINING_FILEPATH = f"{parent_dir}/encoders/team_ids.json"

TEAMS_2024_FILEPATH = f"{parent_dir}/artifacts/encoders/teams_2024.json"
TEAMS_TRAINING_FILEPATH = f"{parent_dir}/artifacts/encoders/training_teams.json"

VENUE_ENCODER_FILEPATH = f"{parent_dir}/artifacts/encoders/venue_encoder.pkl"
TEAM_ENCODER_FILEPATH = f"{parent_dir}/artifacts/encoders/team_encoder.pkl"


# DATA
SHOOTING_TRAINING_DATA_DIR = f"{parent_dir}/data/shooting_data"
SHOOTING_TEST_DATA_DIR = f"{parent_dir}/data/shooting_data_2024"

FIXTURES_TRAINING_DATA_DIR = f"{parent_dir}/data/fixtures_training_data"
FIXTURES_TEST_DATA_FILEPATH = f"{parent_dir}/data/fixtures_test_data/2024-25.csv"

# ARTIFACTS
SAVED_MODELS_DIRECTORY = f"{parent_dir}/artifacts/models"