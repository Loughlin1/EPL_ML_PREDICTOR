import pickle


def load_model(model_filename: str, model_directory: str):
    # Loads a machine learning model from a file
    with open(f"{model_directory}/{model_filename}", "rb") as file:
        model = pickle.load(file)
    return model


def save_model(model, model_filename: str, model_directory: str):
    # Saves a machine learning model to a file
    with open(f"{model_directory}/{model_filename}", "wb") as file:
        pickle.dump(model, file)
