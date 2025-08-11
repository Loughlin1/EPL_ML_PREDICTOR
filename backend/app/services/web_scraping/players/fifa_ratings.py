from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
import time
import random
import os
import io
import re

from ....core.paths import PLAYER_RATINGS_DATA_DIR
from ....db.loaders.player_ratings import add_players, add_ratings


def fifa_version_to_season(version: int) -> str:
    """
    Args:
        version (int): The FIFA version number. E.g. (24)
    Returns:
       str: The corresponding season. E.g. ("2023-2024")
    """
    return f"20{version-1}-20{version}"


def clean_player_name(name: str) -> str:
    """
    Clean player name by removing numeric prefix and optional suffix.

    Args:
        name: Raw player name (e.g., "56 Leon Chiwome Normal").

    Returns:
        Cleaned name (e.g., "Leon Chiwome") or original if no match.
    """
    # Match: number, space, name, optional (space, word)
    match = re.match(r"^\d+\s+(.+?)(?:\s+\w+)?$", name)
    return match.group(1).strip() if match else name.strip()


def generate_initials(name: str) -> str:
    """
    Generate initials from a player name.

    Args:
        name: Player name (e.g., "Harry Kane", "Leon Chiwome").

    Returns:
        Initials (e.g., "H. Kane", "L. Chiwome").
    """
    if not name or not isinstance(name, str):
        return None
    parts = name.strip().split()
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0][0]}. {parts[-1]}"


def locate_correct_table(tables: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Identify the correct table containing player ratings.

    Args:
        tables: List of DataFrames parsed from the page.

    Returns:
        pd.DataFrame: The table with expected columns.

    Raises:
        Exception: If no table with correct columns is found.
    """
    for table in tables:
        if "Name" in table.columns:
            if "RAT" in table.columns and "POS" in table.columns:
                return table
            if "RATOrder By Rating" in table.columns:
                return table
    raise Exception("Cannot find table with correct columns")

def scrape_all_fifa_ratings(start_season: int, end_season: int):
    """
    Scrape FIFA ratings from FUTBIN for specified seasons and save to database.

    Args:
        start_season (int): The starting season for scraping (e.g., 15 for 2014-15).
        end_season (int): The ending season for scraping (e.g., 16 for 2015-16).
    """
    # Set up Selenium with optimized options
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment for headless mode
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-cache")
    options.add_argument("--disk-cache-size=0")
    options.add_argument("--disable-extensions")
    options.add_argument("--blink-settings=imagesEnabled=false")  # Disable images
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Set page load timeout
    driver.set_page_load_timeout(30)  # 30 seconds max for page load

    # Ensure output directory exists
    os.makedirs(PLAYER_RATINGS_DATA_DIR, exist_ok=True)

    print("Starting to scrape ratings data...")
    for version in range(start_season, end_season + 1):
        page = 1
        season = fifa_version_to_season(version)
        while True:
            try:
                url = f"https://www.futbin.com/{version}/players?page={page}&league=13&version=gold,silver,bronze,all_nif"
                print(f"Fetching {url}...")
                
                # Try loading the page with timeout
                try:
                    driver.get(url)
                    # Stop further loading after initial fetch
                    driver.execute_script("window.stop();")
                except TimeoutException:
                    print(f"Page load timeout for FIFA {version}, page {page}. Stopping load and proceeding.")
                    driver.execute_script("window.stop();")
                
                # Wait for table to load
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                    )
                except TimeoutException:
                    print(f"Table not found for FIFA {version}, page {page}. Skipping page.")
                    break
                
                # Extract HTML and parse tables
                html = driver.page_source
                html_buffer = io.StringIO(html)
                tables = pd.read_html(html_buffer)
                
                if not tables:
                    print(f"No tables found for FIFA {version}, page {page}. Breaking.")
                    break
                
                # Process table
                df = locate_correct_table(tables)
                player_map = add_players(df)
                add_ratings(df, season, player_map)
                
                print(f"Processed FIFA {version}, page {page}.")
                
                # Check if next page exists
                if len(df) < 30:  # Assuming page_size = 30
                    print(f"Reached last page for FIFA {version}.")
                    break
                
                page += 1
                time.sleep(random.uniform(2, 5))  # Random delay to avoid detection
                
            except Exception as e:
                print(f"Error scraping FIFA {version}, page {page}: {e}")
                break
        
        print(f"Completed scraping FIFA {version}.")
        time.sleep(random.uniform(5, 10))  # Delay between seasons
    
    driver.quit()

def parse_fifa_ratings_csv(filepath: str):
    """
    Parse and clean a FIFA ratings CSV file.

    Args:
        filepath (str): Path to the CSV file.
    """
    df = pd.read_csv(filepath, index_col=False)
    df.dropna(thresh=6, inplace=True)
    df.to_csv(filepath, index=False)


# if __name__ == "__main__":
#     scrape_all_fifa_ratings(15, 25)
    # parse_fifa_ratings_csv(f"{PLAYER_RATINGS_DATA_DIR}/epl_players_fifa17.csv")