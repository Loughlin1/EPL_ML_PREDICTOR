import os

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)

data_dir = f"{root_dir}/data"
artifacts_dir = f"{parent_dir}/artifacts"

# ARTIFACTS
## ENCODERS
TEAMS_IDS_2024_FILEPATH = f"{artifacts_dir}/encoders/team_ids_2024-25.json"
TEAMS_IDS_TRAINING_FILEPATH = f"{artifacts_dir}/encoders/team_ids.json"

TEAMS_2024_FILEPATH = f"{artifacts_dir}/encoders/teams_2024.json"
TEAMS_TRAINING_FILEPATH = f"{artifacts_dir}//encoders/training_teams.json"

VENUE_ENCODER_FILEPATH = f"{artifacts_dir}/encoders/venue_encoder.pkl"
TEAM_ENCODER_FILEPATH = f"{artifacts_dir}/encoders/team_encoder.pkl"

## MODELS
SAVED_MODELS_DIRECTORY = f"{artifacts_dir}/models"


# DATA
SHOOTING_TRAINING_DATA_DIR = f"{data_dir}/shooting_data"
SHOOTING_TEST_DATA_DIR = f"{data_dir}/shooting_data_2024"

FIXTURES_TRAINING_DATA_DIR = f"{data_dir}/fixtures_training_data"
FIXTURES_TEST_DATA_FILEPATH = f"{data_dir}/fixtures_test_data/2024-25.csv"
