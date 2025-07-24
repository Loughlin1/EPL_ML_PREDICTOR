import pickle

from backend.config.paths import SAVED_MODELS_DIRECTORY


def load_model(model_filename: str):
    # Loads a machine learning model from a file
    with open(f"{SAVED_MODELS_DIRECTORY}/{model_filename}", "rb") as file:
        model = pickle.load(file)
    return model


def save_model(model, model_filename: str):
    # Saves a machine learning model to a file
    with open(f"{SAVED_MODELS_DIRECTORY}/{model_filename}", "wb") as file:
        pickle.dump(model, file)
