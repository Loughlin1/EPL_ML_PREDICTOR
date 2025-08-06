"""
backend/app/services/web_scraping/players/fifa_ratings.py
Module to scrape FIFA ratings data from SoFIFA and save it in a structured format.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time
import random
import os
import io

from app.core.config.paths import PLAYER_RATINGS_DATA_DIR


def scrape_all_fifa_ratings(start_season: int, end_season: int):
    """
    Args:
        start_season (int): The starting season for scraping. (2014/15 -> 15)
        end_season (int): The ending season for scraping (2015/16 -> 16)
    """
    # Set up Selenium with cache disabled
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment for headless mode
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-cache")
    options.add_argument("--disk-cache-size=0")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    page_size = 30

    # Ensure output directory exists
    os.makedirs(PLAYER_RATINGS_DATA_DIR, exist_ok=True)

    print("Starting to scrape ratings data...")
    # Loop through seasons (FIFA 15 to FIFA 24, adjust for EA Sports FC 25)
    for version in range(start_season, end_season):
        page = 1
        season_data = []
        r = version * 10000 + 1
        
        while True:
            try:
                # Use correct SoFIFA version parameter (e.g., v=15 for FIFA 15)
                url = f"https://www.futbin.com/{version}/players?page={page}&league=13&version=all_nif"
                print(f"Fetching {url}...")
                driver.get(url)
                
                # Clear cache to ensure fresh page
                driver.execute_script("window.localStorage.clear();")
                driver.execute_script("window.sessionStorage.clear();")
                driver.delete_all_cookies()
                driver.refresh()
                
                # Wait for table to load
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                html = driver.page_source
                
                # Extract table
                print("Reading HTML...")
                html_buffer = io.StringIO(html)

                tables = pd.read_html(html_buffer)
                if not tables:  # Check if tables are empty
                    print("No tables found, trying next page or breaking...")
                    break
                
                df = tables[2]
                df['Season'] = f"FIFA {version}"
                season_data.append(df)
                
                # Save page data
                # output_file = f"{PLAYER_RATINGS_DATA_DIR}/epl_players_fifa{version}page{page}.csv"
                # df.to_csv(output_file, index=False)
                # print(f"Saved {output_file}")
                
                page += 1
                time.sleep(random.uniform(1, 3))  # Avoid detection
                
                # Check if next page exists (e.g., fewer than page_size rows)
                if len(df) < page_size:
                    print("Reached last page")
                    break
                    
            except Exception as e:
                print(f"Failed to scrape FIFA {version}, page {page}: {e}")
        
        # Combine season data into a single file
        if season_data:
            combined_df = pd.concat(season_data, ignore_index=True)
            combined_df.dropna(thresh=6, inplace=True) # Remove empty rows

            combined_file = f"{PLAYER_RATINGS_DATA_DIR}/epl_players_fifa{version}.csv"
            combined_df.to_csv(combined_file, index=False)
            print(f"Combined data saved to {combined_file}")
        
        print(f"Scraped FIFA {version}")
        time.sleep(10)

    driver.quit()

def parse_fifa_ratings_csv(filepath: str):
    df = pd.read_csv(filepath, index_col=False)
    df.dropna(thresh=6, inplace=True)
    df.to_csv(filepath, index=False)


if __name__ == "__main__":
    scrape_all_fifa_ratings(22,26)
    # parse_fifa_ratings_csv(f"{PLAYER_RATINGS_DATA_DIR}/epl_players_fifa17.csv")