"""
leaderboard_scraper.py

    Module to scrape leaderboard data from Superbru.
"""

import os
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from ....core.config import settings
from .login import login_to_superbru


def get_top_points() -> tuple[int, int]:
    """Function to scrape the top points from the Superbru website."""
    # Step 1: Set up WebDriver
    options = Options()
    options.headless = False #True
    driver = webdriver.Chrome(options=options)
    # Step 2: Log in
    login_to_superbru(driver, settings.SUPERBRU_USERNAME, settings.SUPERBRU_PASSWORD)

    # Step 3: Go to leaderboard page
    leaderboard_url = settings.SUPERBRU_TARGET_URL
    driver.get(leaderboard_url)

    # Step 3: Wait for the table to load and scrape it
    # time.sleep(1)
    table = driver.find_element(
        By.XPATH,
        ("/html/body/main/div/div[2]/div/div[3]/div[2]/div/div[2]/table"),
    )
    html = table.get_attribute("outerHTML")

    soup = BeautifulSoup(html, "html.parser")
    rows = [[cell.text for cell in row.find_all("td")] for row in soup.find_all("tr")]

    # print(rows)
    top_global_points = rows[2][-1]
    top_global_250_points = rows[-1][-1]
    print(top_global_points, top_global_250_points)

    driver.quit()
    return top_global_points, top_global_250_points


if __name__ == "__main__":
    get_top_points()
