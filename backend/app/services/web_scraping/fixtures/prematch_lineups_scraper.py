"""
prematch_lineups_scraper.py

    Module to scrape the pre-match lineups from the BBC Sports website
    when announced before the game.
"""

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


base_url = f"https://www.bbc.com/sport/football/premier-league/scores-fixtures"


def get_lineup(home_team: str, away_team: str) -> dict:
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    current_month = "2025-08" #datetime.date.today().strftime('%Y-%m')
    target_url = f"{base_url}/{current_month}"
    driver.get(target_url)

    try:
        home_element = driver.find_element(By.XPATH, f"//*//a[contains(text(),'{home_team}')]")
        print(f"Element with partial text found: {home_element.text}")
    except:
        print("Partial text not found on the page.")

    driver.quit()

get_lineup("AFC Bournemouth", "Leicester City")