import pandas as pd


def get_superbru_points(df: pd.DataFrame) -> int:
    """
    Calculate and returns the points scored based on the accuracy of the predictions.
    """
    points = 0

    # Exact scores
    points += 3 * len(df.loc[df["Score"] == df["PredScore"], :])

    # Close scores
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
    # Combine conditions
    final_condition = (
        (df["Result"] == df["PredResult"])
        & (one_goal_out_condition | two_goals_out_condition)
        & (df["Score"] != df["PredScore"])  # Can't double count the points for exact.
    )

    # Count number of rows where the conditions are met
    close_predictions_count = len(df.loc[final_condition, :])

    points += 1.5 * close_predictions_count

    # Result scores

    num_result_correct = len(
        df.loc[
            (df["Result"] == df["PredResult"])
            & (df["Score"] != df["PredScore"])
            & ~final_condition,
            :,
        ]
    )
    points += num_result_correct

    # Slam points
    if num_result_correct >= 10:
        points += num_result_correct

    elif num_result_correct >= 8:
        points += num_result_correct

    elif num_result_correct >= 5:
        points += num_result_correct

    return points
