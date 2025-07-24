from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from ...core.config.paths import SAVED_MODELS_DIRECTORY
from ..data_processing.data_loader import load_validation_data
from ..models.save_load import load_model


def evaluate_model(model):
    # Load model
    model = load_model("random_forest_model.pkl", SAVED_MODELS_DIRECTORY)

    # Load validation data
    X_val, y_val = load_validation_data()

    # Generate predictions
    y_pred = model.predict(X_val)

    # Calculate metrics
    rmse = root_mean_squared_error(y_val, y_pred, squared=False)
    mae = mean_absolute_error(y_val, y_pred)

    print(f"RMSE: {rmse}")
    print(f"MAE: {mae}")

    return rmse, mae


if __name__ == "__main__":
    evaluate_model()