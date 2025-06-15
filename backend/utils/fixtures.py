"""
backend/utils/fixtures.py

This module provides utility functions for 
    - sorting fixtures by week 
    - analyzing football match fixtures and predictions.
"""

from datetime import datetime, timedelta

import pandas as pd

from backend.config import FIXTURES_TEST_DATA_FILEPATH


def get_fixtures() -> pd.DataFrame:
    """
    Reads the fixtures data from a CSV file,
    drops rows with NaN values, and returns the DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing the fixtures data.
    """
    df = pd.read_csv(FIXTURES_TEST_DATA_FILEPATH, index_col=0)
    df.dropna(thresh=7, inplace=True)  # Dropping any NaN rows in the data
    return df


def get_this_weeks_fixtures(
    fixtures_df: pd.DataFrame, matchweek_no: int
) -> pd.DataFrame:
    """
    Filters the fixtures to only those for the specified match week.

    Parameters:
        fixtures_df (pd.DataFrame): DataFrame containing all fixtures.
        matchweek_no (int): Match week number to filter by.

    Returns:
        pd.DataFrame: DataFrame containing fixtures for specified match week.
    """
    fixtures_df = fixtures_df.loc[fixtures_df["Wk"] == matchweek_no]
    return fixtures_df


def get_this_week(df: pd.DataFrame) -> pd.DataFrame:
    """
    Finds and returns fixtures for the current week based on today's date.

    Parameters:
        df (pd.DataFrame): DataFrame containing all fixtures.

    Returns:
        pd.DataFrame: DataFrame containing fixtures for the current week.
    """
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.date
    today = datetime.today().date()

    has_season_ended = not df[df["Wk"] == 38].dropna(subset=["Score"], how="all").empty
    if has_season_ended:
        result_df = df[df["Wk"] == 38]
        return result_df, 38

    def find_matching_rows(date) -> tuple[pd.DataFrame, int]:
        matched_row = df[df["Date"] == date]
        if not matched_row.empty:
            matching_week = matched_row["Wk"].values[0]
            result_df = df[df["Wk"] == matching_week]
            return result_df, matching_week
        else:
            return None, None

    # Iterate over the last 7 days (including today)
    result_df = None
    for i in range(7):
        check_date = today - timedelta(days=i)
        result_df, matchweek_no = find_matching_rows(check_date)
        if result_df is not None:
            break
    return result_df, matchweek_no


def highlight_rows(s) -> pd.DataFrame:
    """
    Highlights rows in a DataFrame based on 
    the comparison of actual and predicted results and scores.

    Parameters:
        s (pd.DataFrame): DataFrame containing actual and predicted results and scores.

    Returns:
        pd.DataFrame: DataFrame with styles applied for highlighting.
    """
    styles = pd.DataFrame("", index=s.index, columns=s.columns)
    styles.loc[(s["Result"] == s["PredResult"]) & (s["Score"].notna()), :] = (
        "background-color: #FFDB58"
    )
    styles.loc[s["Score"] == s["PredScore"], :] = "background-color: #3CB371"
    return styles
