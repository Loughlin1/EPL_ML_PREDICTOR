"""
backend/utils/data_processing.py

"""

import pandas as pd
from backend.config.paths import FIXTURES_TRAINING_DATA_DIR


def load_training_data():
    file_paths = [
        "2014-15.csv",
        "2015-16.csv",
        "2016-17.csv",
        "2017-18.csv",
        "2018-19.csv",
        "2019-20.csv",
        "2020-21.csv",
        "2021-22.csv",
        "2022-23.csv",
        "2023-24.csv",
    ]
    dfs = [
        pd.read_csv(f"{FIXTURES_TRAINING_DATA_DIR}/{file}", index_col=0)
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


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    # Preprocesses raw data for model input
    # ...existing code...
    ...
