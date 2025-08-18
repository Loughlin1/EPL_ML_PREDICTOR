import pandas as pd


def get_superbru_points(df: pd.DataFrame) -> int:
    """
    Calculate points scored based on the accuracy of predictions.
    
    Args:
        df (pd.DataFrame): DataFrame with columns FTHG, FTAG, PredFTHG, PredFTAG, Result, PredResult.
    
    Returns:
        int: Total Superbru points scored.
    
    Raises:
        ValueError: If required columns are missing or contain invalid data.
    """
    # Validate required columns
    required_cols = ["FTHG", "FTAG", "PredFTHG", "PredFTAG", "Result", "PredResult"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Create a copy to avoid modifying input
    df = df.copy()

    # Convert goal columns to integers, handling NA values
    goal_cols = ["FTHG", "FTAG", "PredFTHG", "PredFTAG"]
    for col in goal_cols:
        # Convert to numeric, coercing errors to NaN
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Check for NA in predictions
    if df[["PredFTHG", "PredFTAG"]].isna().any().any():
        raise ValueError("PredFTHG or PredFTAG contains NaN values, ensure predictions are complete")
    
    # Convert predictions to integers
    df[["PredFTHG", "PredFTAG"]] = df[["PredFTHG", "PredFTAG"]].astype(int)
    
    # Filter rows with valid FTHG/FTAG for scoring (exclude future matches)
    valid_df = df.dropna(subset=["FTHG", "FTAG"]).copy()
    if valid_df.empty:
        print("No valid matches with FTHG and FTAG for scoring")
        return 0
    
    # Convert FTHG/FTAG to integers for valid rows
    valid_df[["FTHG", "FTAG"]] = valid_df[["FTHG", "FTAG"]].astype(int)
    
    points = 0

    # Exact scores: 3 points for exact match of home and away goals
    exact_scores = (df["FTHG"] == df["PredFTHG"]) & (df["FTAG"] == df["PredFTAG"])
    points += 3 * exact_scores.sum()

    # Close scores: 1.5 points for close predictions with correct result
    condition1 = (abs(df["PredFTHG"] - df["FTHG"]) <= 1) & (
        df["PredFTAG"] == df["FTAG"]
    )

    condition2 = (abs(df["PredFTAG"] - df["FTAG"]) <= 1) & (
        df["PredFTHG"] == df["FTHG"]
    )

    condition3 = (abs(df["PredFTHG"] - df["FTHG"]) <= 2) & (
        df["PredFTAG"] == df["FTAG"]
    )

    condition4 = (abs(df["PredFTAG"] - df["FTAG"]) <= 2) & (
        df["PredFTHG"] == df["FTHG"]
    )

    condition5 = (abs(df["PredFTHG"] - df["FTHG"]) <= 1) & (
        abs(df["PredFTAG"] - df["FTAG"]) <= 1
    )
    condition6 = abs(df["FTHG"] - df["FTAG"]) == abs(df["PredFTHG"] - df["PredFTAG"])

    one_goal_out_condition = condition1 | condition2
    two_goals_out_condition = (condition3 | condition4 | condition5) & condition6

    close_scores_condition = (
        (df["Result"] == df["PredResult"]) &  # Correct result
        (one_goal_out_condition | two_goals_out_condition) &  # Close score conditions
        (~exact_scores)  # Exclude exact scores to avoid double-counting
    )
    points += 1.5 * close_scores_condition.sum()

    # Correct result: 1 point for correct result (win/loss/draw) without close or exact score
    correct_result_condition = (
        (df["Result"] == df["PredResult"]) &  # Correct result
        (~exact_scores) &  # Not an exact score
        (~close_scores_condition)  # Not a close score
    )
    points += correct_result_condition.sum()

    # # Slam points
    # if num_result_correct >= 10:
    #     points += num_result_correct

    # elif num_result_correct >= 8:
    #     points += num_result_correct

    # elif num_result_correct >= 5:
    #     points += num_result_correct
    return points
