import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split
from ...core.paths import SAVED_MODELS_DIRECTORY, FIXTURES_TRAINING_DATA_DIR
from ..data_processing.data_loader import load_training_data, clean_data
from ..models.save_load import load_model
from ..models.train import preprocess_data
from ..models.config import LABELS


def evaluate_model_performance(y_true: pd.DataFrame, y_pred: pd.DataFrame):
    """
    Evaluates model performance on football score predictions with multiple metrics.
    """
    y_true = y_true.reset_index(drop=True)
    y_pred = y_pred.reset_index(drop=True)

    # Calculate Mean Absolute Error for FTHG and FTAG
    mae_home = mean_absolute_error(y_true["FTHG"], y_pred["FTHG"])  # FTHG
    mae_away = mean_absolute_error(y_true["FTAG"], y_pred["FTAG"])  # FTAG

    r2_home = r2_score(y_true["FTHG"], y_pred["FTHG"])
    r2_away = r2_score(y_true["FTAG"], y_pred["FTAG"])

    # Calculate Root Mean Squared Error for FTHG and FTAG
    rmse_home = root_mean_squared_error(y_true["FTHG"], y_pred["FTHG"])
    rmse_away = root_mean_squared_error(y_true["FTAG"], y_pred["FTAG"])

    # Calculate Total Mean Absolute Error and RMSE
    mae_total = (mae_home + mae_away) / 2
    rmse_total = (rmse_home + rmse_away) / 2

    # Exact Match Ratio (how often both FTHG and FTAG are predicted exactly)
    exact_matches = int(
        np.sum((y_true["FTHG"] == y_pred["FTHG"]) & (y_true["FTAG"] == y_pred["FTAG"]))
    )
    exact_match_percentage = 100 * exact_matches / len(y_true)

    # Goal Difference Prediction Accuracy
    goal_diff_true = y_true["FTHG"] - y_true["FTAG"]
    goal_diff_pred = y_pred["FTHG"] - y_pred["FTAG"]
    goal_diff_accuracy = float(
        np.mean(np.sign(goal_diff_true) == np.sign(goal_diff_pred))
    )

    true_result = np.select(
        [y_true["FTHG"] > y_true["FTAG"], y_true["FTHG"] < y_true["FTAG"]],
        choicelist=["W", "L"],
        default="D",
    )
    pred_result = np.select(
        [y_pred["FTHG"] > y_pred["FTAG"], y_pred["FTHG"] < y_pred["FTAG"]],
        choicelist=["W", "L"],
        default="D",
    )
    correct_results = int(np.sum(pred_result == true_result))
    correct_results_percentage = 100 * correct_results / pred_result.shape[0]
    return {
        "MAE_Home": np.round(mae_home, 3),
        "MAE_Away": np.round(mae_away, 3),
        "MAE_Total": np.round(mae_total, 3),
        "RMSE_Home": np.round(rmse_home, 3),
        "RMSE_Away": np.round(rmse_away, 3),
        "RMSE_Total": np.round(rmse_total, 3),
        "R2_Home": np.round(r2_home, 3),
        "R2_Away": np.round(r2_away, 3),
        "Correct_Results": correct_results,
        "Correct_Result_%": np.round(correct_results_percentage, 3),
        "Correct_Scores": exact_matches,
        "Correct_Scores_%": np.round(exact_match_percentage, 3),
        "Goal_Difference_Accuracy": np.round(goal_diff_accuracy, 3),
    }


def evaluate_model():
    model = load_model("random_forest_model.pkl", SAVED_MODELS_DIRECTORY)
    df = load_training_data()
    df = clean_data(df)
    X, y = preprocess_data(df)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    y_pred = model.predict(X_val)
    y_pred = pd.DataFrame(y_pred, columns=LABELS)
    results = evaluate_model_performance(y_val, y_pred)
    return results


if __name__ == "__main__":
    evaluate_model()
