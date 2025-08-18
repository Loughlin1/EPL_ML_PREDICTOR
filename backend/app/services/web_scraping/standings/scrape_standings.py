import os
import pandas as pd
import time
import io
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from ....core.config import settings
from ....core.paths import data_dir
from ...data_processing.data_loader import generate_seasons


FOOTBALL_DATA_BASE_URL = settings.FOOTBALL_DATA_BASE_URL


def scrape_standings(season: str) -> pd.DataFrame:
    """
    Args:
        season (str): The season for which fixtures are being scraped.
                      E.g. ("2024-2025")
    """

    url = f"{FOOTBALL_DATA_BASE_URL}/en/comps/9/{season}/{season}-Premier-League-Stats#all_league_summary"
    df = pd.read_html(url, attrs={"id": f"results{season}91_overall"})[0]
    df["season"] = season
    return df


def scrape_and_save_standings(seasons: list[str]) -> None:
    dfs = []
    for season in seasons:
        scrape_and_save_standings(season)
        time.sleep(3)

    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        filepath = f"{data_dir}/standings.csv"
        df.to_csv(filepath, index=False)
        print(f"Standings for {seasons} saved to {filepath}")
    else:
        print("No data scraped.")



def scrape_from_wikipedia():
    dfs = []
    for season in range(2022, 2025):
        url = f"https://en.wikipedia.org/wiki/{season}%E2%80%93{season-1999}_Premier_League"
        tables = pd.read_html(url)
        df = tables[4]
        df["Season"] = f"{season}-{season-1999}"
        dfs.append(df)
        import time
        time.sleep(2)

    return pd.concat(dfs, ignore_index=True)


    

filepath = f"{data_dir}/standings/2000-2022.csv"
df = pd.read_csv(filepath)
scraped_df = scrape_from_wikipedia()
print(scraped_df.tail())
df = pd.concat([df,scraped_df], ignore_index=True)
df.to_csv(filepath)

# if __name__ == "__main__":
#     seasons = generate_seasons(2014, 2024)
#     scrape_and_save_standings(seasons)
