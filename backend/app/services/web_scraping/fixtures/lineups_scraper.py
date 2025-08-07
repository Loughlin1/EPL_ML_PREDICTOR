
import os
import sys
import re
import random
import time
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import traceback

load_dotenv()
BASE_URL = os.environ["FOOTBALL_DATA_BASE_URL"]

from app.services.web_scraping.fixtures.helper import generate_seasons
from app.core.config.paths import LINEUPS_TRAINING_DATA_DIR, LINEUPS_TEST_DATA_DIR


def retrieve_fixtures_table(season: str) -> list[str]:
    """
    Retrieve the URLs of match reports for a season
    
    Args:
        season: str (e.g. "2024-2025")
    """
    url = f"{BASE_URL}/en/comps/9/{season}/schedule/{season}-Premier-League-Scores-and-Fixtures"
    
    df = pd.read_html(url, attrs={"id": f"sched_{season}_9_1"}, extract_links="body")[0]
    match_report_column = "Match Report"
    for col in df.columns.difference([match_report_column]):
        df[col] = df[col].apply(lambda x: x[0])
    df[match_report_column] = df[match_report_column].apply(lambda x: x[1])
    df.replace('', np.nan, inplace=True)
    df.dropna(thresh=5, inplace=True)
    return df


def find_formation(text: str) -> str:
    match = re.search(r'\((\d(?:-\d){2,4})\)', text)
    return match.group(1) if match else None


def get_starting_lineup(df: pd.DataFrame) -> list:
    return df.iloc[:10, 1].to_list()


def get_bench(df: pd.DataFrame) -> list:
    return df.iloc[12:, 1].to_list()


def scrape_match_report(url: str):
    url = f"{BASE_URL}{url}"
    dfs = pd.read_html(url)
    data = {}
    for i, team in enumerate(["home", "away"]):
        df = dfs[i]
        data[team] = {
            "formation": find_formation(df.columns[0]),
            "starting_lineup": get_starting_lineup(df),
            "bench": get_bench(df),
        }
    return data


def scrape_lineups(df: pd.DataFrame) -> pd.DataFrame:
    """"
    Fetches the lineups from the given DataFrame and returns a DataFrame with the lineups.
    """
    home_formations = []
    away_formations = []
    home_starting_lineup = []
    away_starting_lineup = []
    home_bench = []
    away_bench = []

    for index, row in df.iterrows():
        try:
            data = scrape_match_report(row["Match Report"])
        except:
            exception = traceback.format_exc()
            print(f"Error scraping match report for row {index}: {row['Match Report']}")
            print(f"\nException: {exception}\n")
            sys.exit(1)

        home_formations.append(data["home"]["formation"])
        away_formations.append(data["away"]["formation"])
        home_starting_lineup.append(data["home"]["starting_lineup"])
        away_starting_lineup.append(data["away"]["starting_lineup"])
        home_bench.append(data["home"]["bench"])
        away_bench.append(data["away"]["bench"])
        time.sleep(random.randint(3, 5))
        # time
        if index and index % 10 == 0:
            print(f"{index+1} matches scraped so far")
            time.sleep(10)

        df["home_formation"] = pd.Series(home_formations)
        df["away_formation"] = pd.Series(away_formations)
        df["home_starting_lineup"] = pd.Series(home_starting_lineup)
        df["away_starting_lineup"] = pd.Series(away_starting_lineup)
        df["home_bench"] = pd.Series(home_bench)
        df["away_bench"] = pd.Series(away_bench)

    return df


def scrape_fixtures_and_lineups(seasons: list[str], data_dir: str):
    os.makedirs(data_dir, exist_ok=True)
    for season in seasons:
        df = retrieve_fixtures_table(season)
        df = scrape_lineups(df)        
        print(df.head())
        filepath = f"{data_dir}/{season[:4]}-{season[7:9]}.csv"
        df.to_csv(filepath)
        print(f"Season {season} saved to {filepath}")
        time.sleep(30)


def main():
    seasons = generate_seasons(2014, 2014)
    scrape_fixtures_and_lineups(seasons, LINEUPS_TRAINING_DATA_DIR)


if __name__ == "__main__":
    main()
