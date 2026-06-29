import json
import pickle

import joblib
from sklearn.preprocessing import StandardScaler

from ...core.paths import SAVED_MODELS_DIRECTORY, artifacts_dir, season_model_path, season_scaler_path

SCALER_FILEPATH = artifacts_dir / "scaler.pkl"


def load_model(
    model_directory: str, model_filename: str, metadata_filename: str = None
):
    # Loads a machine learning model from a file
    if model_filename.endswith(".pkl"):
        with open(f"{model_directory}/{model_filename}", "rb") as file:
            model = pickle.load(file)
    elif model_filename.endswith(".joblib"):
        model = joblib.load(f"{model_directory}/{model_filename}")

    if metadata_filename:
        with open(f"{model_directory}/{metadata_filename}", "r") as f:
            model_info = json.load(f)
        print(model_info)
    return model


def load_model_for_season(season: str):
    """Load season-scoped model, falling back to best_model.joblib."""
    path = season_model_path(season)
    if path.exists():
        return joblib.load(path)
    fallback = SAVED_MODELS_DIRECTORY / "best_model.joblib"
    return joblib.load(fallback)


def save_model(model, model_filename: str, model_directory: str):
    # Saves a machine learning model to a file
    with open(f"{model_directory}/{model_filename}", "wb") as file:
        pickle.dump(model, file)


def save_model_for_season(model, season: str) -> None:
    joblib.dump(model, season_model_path(season))


def save_scaler(scaler: StandardScaler) -> None:
    joblib.dump(scaler, SCALER_FILEPATH)


def save_scaler_for_season(scaler: StandardScaler, season: str) -> None:
    joblib.dump(scaler, season_scaler_path(season))


def load_scaler() -> StandardScaler:
    return joblib.load(SCALER_FILEPATH)


def load_scaler_for_season(season: str) -> StandardScaler:
    """Load season-scoped scaler, falling back to the global scaler."""
    path = season_scaler_path(season)
    if path.exists():
        return joblib.load(path)
    return joblib.load(SCALER_FILEPATH)


def select_and_save_best_model(losses, models_trained, save_path="best_model"):
    """
    Select the best model based on validation MSE and save it along with metadata.

    Parameters:
    - losses: Dictionary with model names as keys and {"train_mse": float, "val_mse": float} as values
    - models_trained: Dictionary with model names as keys and trained model objects as values
    - feature_importances: Dictionary with model names as keys and feature importance dicts as values
    - save_path: Base path for saving model and metadata (default: "best_model")

    Returns:
    - best_model: The trained model with lowest val_mse
    - best_model_info: Dictionary with model name, losses, and feature importances
    """
    # Find model with lowest validation MSE
    best_model_name = min(losses, key=lambda x: losses[x]["val_mse"])
    best_model = models_trained[best_model_name]

    # Prepare metadata
    best_model_info = {
        "model_name": best_model_name,
        "train_mse": losses[best_model_name]["train_mse"],
        "val_mse": losses[best_model_name]["val_mse"],
    }

    # Save the model
    joblib.dump(best_model, f"{save_path}.joblib")

    print(
        f"Best model: {best_model_name} (val_mse: {losses[best_model_name]['val_mse']:.4f})"
    )
    print(best_model_info)
    # Save metadata as JSON
    with open(f"{save_path}_metadata.json", "w") as f:
        json.dump(best_model_info, f, indent=4)

    print(
        f"Saved model to {save_path}.joblib and metadata to {save_path}_metadata.json"
    )

    return best_model, best_model_info
