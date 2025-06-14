"""
scraper.py

Module to scrape data from the web and return it in a structured format.
"""
import os
import sys
import pandas as pd
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

target_url = os.getenv("TARGET_URL")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
football_data_url = os.getenv("FOOTBALL_DATA_URL")

# Ensure sensitive information is not hardcoded
assert target_url is not None, "TARGET_URL environment variable is not set"
assert username is not None, "USERNAME environment variable is not set"
assert password is not None, "PASSWORD environment variable is not set"
assert football_data_url is not None, "FOOTBALL_DATA_URL environment variable is not set"


def scrape_season_stats(url):
    try:
        df = pd.read_html(url, attrs={"id": "matchlogs_for"})[0]
        return df if not df.empty else None
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None


def scrape_teams_stats(seasons, squad_id, team_name):
    urls = ['https://fbref.com/en/squads/' + squad_id + '/' + season + '/matchlogs/c9/shooting/' + team_name + '-Match-Logs-Premier-League' for season in seasons]
    
    dfs = []
    for url in urls:
        df = scrape_season_stats(url)
        time.sleep(10)
        if df is not None:
            dfs.append(df)
    if dfs:
        df = pd.concat(dfs, ignore_index=False)
        df = df.droplevel(level=0, axis=1)
        df.to_csv(f'{parent_dir}/data/shooting_data_2024/' + team_name + '.csv')
        print(f"Exported {team_name} to /data/shooting_data_2024/{team_name}.csv")
    else:
        print(f"No valid data for team {team_name} in seasons {seasons}")


def scrape_all_teams_stats(seasons, team_ids):
    counter = 0
    for team, id in team_ids.items():
        scrape_teams_stats(seasons, id, team)
        if counter == 3:
            time.sleep(10)
        counter +=1


def scrape_fixtures() -> None:
    """Function to scrape the fixtures data from the web and save it to a CSV file."""
    df = pd.read_html(football_data_url, attrs={"id": "sched_2024-2025_9_1"})[0]
    df.to_csv('data/2024-25.csv')
    print("Data fetched and processed")

    # fetch shooting stats for each team
    teams_2024 = json.load(open(f"{parent_dir}/Encoders/team_ids_2024-25.json"))
    scrape_all_teams_stats(['2024-2025'], teams_2024)
    time.sleep(10)


def get_top_points() -> tuple:
    """Function to scrape the top points from the Superbru website."""
    # Step 1: Set up WebDriver
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)  # Or use another WebDriver
    driver.get(target_url)

    try:
        # Replace 'button.accept-cookies' with the actual selector for the accept button
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#qc-cmp2-ui > div.qc-cmp2-footer.qc-cmp2-footer-overlay.qc-cmp2-footer-scrolled > div > button.css-13brqst"))
        )
        cookie_button.click()
        print("Cookie popup dismissed.")
    except Exception as e:
        print("No cookie popup found or error occurred:", e)

    try:
        # Adjust the selector to match the desired anchor tag
        anchor_tag = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "body > main > div > div > div > div > div > div > div > div.entry > div.tab-bar > ul > li.tab-control.active > a"))
        )
        anchor_tag.click()
        print("Clicked the anchor tag.")
    except Exception as e:
        print("Anchor tag not found or timeout:", e)

    # Step 2: Log in (if needed)
    driver.find_element(By.ID, "email-superbru").send_keys(username)
    driver.find_element(By.ID, "password-superbru").send_keys(password)
    driver.find_element(By.XPATH, "/html/body/main/div/div/div/div/div/div/div/div[3]/div[2]/div[1]/form/div[3]/input").submit()

    # Step 3: Wait for the table to load and scrape it
    time.sleep(1)
    table = driver.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div[3]/div[2]/div/div[2]/table")  # CSS selector for multiple classes
    html = table.get_attribute("outerHTML")

    # Use BeautifulSoup to parse the table
    soup = BeautifulSoup(html, "html.parser")
    rows = [[cell.text for cell in row.find_all("td")] for row in soup.find_all("tr")]
    print(rows)
    top_global_points = rows[2][-1]
    top_global_250_points = rows[-1][-1]
    print(top_global_points, top_global_250_points)
    driver.quit()

    return top_global_points, top_global_250_points