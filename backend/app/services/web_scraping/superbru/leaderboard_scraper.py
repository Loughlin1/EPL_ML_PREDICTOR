"""
leaderboard_scraper.py

    Module to scrape leaderboard data from Superbru.
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from ....core.config import settings
from .login import login_to_superbru


def get_top_points() -> tuple[int, int, int]:
    """Function to scrape the top points from the Superbru website.

    Returns:
        (global_top, global_top_10_pct, uk_top_10_pct)
        global_top       — points of the #1 player (~100k pool)
        global_top_10_pct — top-10% threshold (~rank 10,000)
        uk_top_10_pct    — top-10% threshold for UK pool (~15k players)
    """
    # LOGIN TEMPORARILY DISABLED
    # Realistic placeholders: 10 matches/week × 38 weeks, max 3pts/match
    # Global #1 ~19pts/week, top 10% ~14pts/week, UK top 10% slightly higher
    return 760, 530, 552

    # Step 1: Set up WebDriver
    options = Options()
    options.headless = False  # True
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
    top_global_10_pct_points = rows[-1][-1]
    # TODO: scrape uk_top_10_pct from the UK leaderboard tab
    uk_top_10_pct_points = None
    print(top_global_points, top_global_10_pct_points, uk_top_10_pct_points)

    driver.quit()
    return top_global_points, top_global_10_pct_points, uk_top_10_pct_points


if __name__ == "__main__":
    get_top_points()
