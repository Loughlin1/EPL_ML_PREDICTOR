import os
import pandas as pd
from app.core.config.paths import FIXTURES_TEST_DATA_FILEPATH


def load_training_data(training_data_dir: str):
    if not os.path.exists(training_data_dir):
        raise FileExistsError(f"The path {training_data_dir} does NOT exist.")

    file_paths = [
        os.path.join(training_data_dir, f)
        for f in os.listdir(training_data_dir)
        if f.endswith(".csv") and os.path.isfile(os.path.join(training_data_dir, f))
    ]
    dfs = [
        pd.read_csv(file, index_col=0)
        for file in file_paths
    ]
    return pd.concat(dfs, ignore_index=False)


def clean_data(df):
    # ...existing code for cleaning...
    df.drop(columns=["Notes", "Match Report", "xG", "xG.1", "Attendance"], inplace=True)
    df.rename(columns={"Home": "HomeTeam", "Away": "AwayTeam"}, inplace=True)
    df.dropna(subset=["Day"], inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
    df["Wk"] = df["Wk"].astype(int)
    return df


def get_this_seasons_fixtures_data() -> pd.DataFrame:
    """
    Reads the fixtures data from a CSV file,
    drops rows with NaN values, and returns the DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing the fixtures data.
    """
    df = pd.read_csv(FIXTURES_TEST_DATA_FILEPATH, index_col=0)
    df.dropna(thresh=7, inplace=True)  # Dropping any NaN rows in the data
    return df    
