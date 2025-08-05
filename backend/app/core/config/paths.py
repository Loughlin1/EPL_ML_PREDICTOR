from pathlib import Path

backend_dir = Path(__file__).resolve().parents[3]  # backend
project_root = backend_dir.parent  # EPL_ML_PREDICTOR
data_dir = project_root / "data"
artifacts_dir = backend_dir / "app" / "services" / "artifacts"

# ARTIFACTS
TEAMS_IDS_2024_FILEPATH = artifacts_dir / "encoders" / "team_ids_2024-25.json"
TEAMS_IDS_TRAINING_FILEPATH = artifacts_dir / "encoders" / "team_ids.json"

TEAMS_2024_FILEPATH = artifacts_dir / "encoders" / "teams_2024.json"
TEAMS_TRAINING_FILEPATH = artifacts_dir / "encoders" / "training_teams.json"

VENUE_ENCODER_FILEPATH = artifacts_dir / "encoders" / "venue_encoder.pkl"
TEAM_ENCODER_FILEPATH = artifacts_dir / "encoders" / "team_encoder.pkl"

SAVED_MODELS_DIRECTORY = artifacts_dir / "models"

# DATA
SHOOTING_TRAINING_DATA_DIR = data_dir / "shooting_data"
SHOOTING_TEST_DATA_DIR = data_dir / "shooting_data_2024"

FIXTURES_TRAINING_DATA_DIR = data_dir / "fixtures_training_data"
FIXTURES_TEST_DATA_FILEPATH = data_dir / "fixtures_test_data" / "2024-25.csv"

PLAYER_RATINGS_DATA_DIR = data_dir / "player_ratings"

# CACHE
SUPERBRU_LEADERBOARD_CACHE = data_dir / "cache" / "leaderboard.json"

# CONTENT
CONTENT_DIR = backend_dir / "app" / "content"