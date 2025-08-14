from pathlib import Path

backend_dir = Path(__file__).resolve().parents[2]  # backend
project_root = backend_dir.parent  # EPL_ML_PREDICTOR
data_dir = project_root / "data"
artifacts_dir = backend_dir / "app" / "services" / "artifacts"

# ARTIFACTS

VENUE_ENCODER_FILEPATH = artifacts_dir / "encoders" / "venue_encoder.pkl"
TEAM_ENCODER_FILEPATH = artifacts_dir / "encoders" / "team_encoder.pkl"
SAVED_MODELS_DIRECTORY = artifacts_dir / "models"

# DATA
FIXTURES_TRAINING_DATA_DIR = data_dir / "fixtures_training_data"
LINEUPS_TRAINING_DATA_DIR = data_dir / "lineups_training_data"

# CACHE
SUPERBRU_LEADERBOARD_CACHE = data_dir / "cache" / "leaderboard.json"

# CONTENT
CONTENT_DIR = backend_dir / "app" / "content"
