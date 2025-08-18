import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split

from ...core.paths import SAVED_MODELS_DIRECTORY
from ..data_processing.data_loader import load_training_data, clean_data
from ..models.save_load import load_model
from ..models.train import preprocess_data
from ..models.config import LABELS, FEATURES


def evaluate_model_performance(y_true: pd.DataFrame, y_pred: pd.DataFrame):
    """
    Evaluate model performance using MAE, RMSE, and accuracy metrics.
    
    Args:
        y_true (pd.DataFrame): Actual results with FTHG, FTAG columns.
        y_pred (pd.DataFrame): Predicted results with FTHG, FTAG columns.
    
    Returns:
        dict: Metrics including MAE, RMSE, and accuracy for home and away goals.
    
    Raises:
        ValueError: If required columns are missing or contain invalid data.
    """
    # Validate required columns
    required_cols = ["FTHG", "FTAG"]
    for df, name in [(y_true, "y_true"), (y_pred, "y_pred")]:
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in {name}: {missing_cols}")

    # Create copies to avoid modifying input
    y_true = y_true.copy()
    y_pred = y_pred.copy()

    # Convert goal columns to numeric, handling invalid values
    for col in ["FTHG", "FTAG"]:
        y_true[col] = pd.to_numeric(y_true[col], errors="coerce")
        y_pred[col] = pd.to_numeric(y_pred[col], errors="coerce")

    # Filter rows with valid FTHG/FTAG (exclude future matches)
    valid_mask = y_true[["FTHG", "FTAG"]].notna().all(axis=1) & y_pred[["FTHG", "FTAG"]].notna().all(axis=1)
    if not valid_mask.any():
        print("No valid matches with FTHG and FTAG for evaluation")
        return {
            "MAE_Home": 0,
            "MAE_Away": 0,
            "MAE_Total": 0,
            "RMSE_Home": 0,
            "RMSE_Away": 0,
            "RMSE_Total": 0,
            "R2_Home": 0,
            "R2_Away": 0,
            "Correct_Results": 0,
            "Correct_Result_%": 0,
            "Correct_Scores": 0,
            "Correct_Scores_%": 0,
            "Goal_Difference_Accuracy": 0,
        }

    y_true = y_true[valid_mask].copy()
    y_pred = y_pred[valid_mask].copy()

    # Convert to integers
    y_true[["FTHG", "FTAG"]] = y_true[["FTHG", "FTAG"]].astype(int)
    y_pred[["FTHG", "FTAG"]] = y_pred[["FTHG", "FTAG"]].astype(int)

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
    model = load_model(SAVED_MODELS_DIRECTORY, "best_model.joblib")
    df = load_training_data()
    df = clean_data(df)
    df = preprocess_data(df)
    X = df[FEATURES]
    y = df[LABELS]
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    y_pred = model.predict(X_val)
    y_pred = pd.DataFrame(y_pred, columns=LABELS)
    results = evaluate_model_performance(y_val, y_pred)
    return results


if __name__ == "__main__":
    evaluate_model()
