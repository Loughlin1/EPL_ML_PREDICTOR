"""
backend/app/services/utils/fixtures.py

This module provides utility functions for
    - sorting fixtures by week
    - analyzing football match fixtures and predictions.
"""

from datetime import datetime, timedelta
import pandas as pd

from app.core.config.paths import FIXTURES_TEST_DATA_FILEPATH


def get_fixtures_data() -> pd.DataFrame:
    """
    Reads the fixtures data from a CSV file,
    drops rows with NaN values, and returns the DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing the fixtures data.
    """
    df = pd.read_csv(FIXTURES_TEST_DATA_FILEPATH, index_col=0)
    df.dropna(thresh=7, inplace=True)  # Dropping any NaN rows in the data
    return df
