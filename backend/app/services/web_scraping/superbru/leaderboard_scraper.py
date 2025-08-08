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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

target_url = os.environ["SUPERBRU_TARGET_URL"]
username = os.environ["SUPERBRU_USERNAME"]
password = os.environ["SUPERBRU_PASSWORD"]


def get_top_points() -> tuple[int, int]:
    """Function to scrape the top points from the Superbru website."""
    # Step 1: Set up WebDriver
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(target_url)

    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    (
                        "#qc-cmp2-ui > div.qc-cmp2-footer.qc-cmp2-footer-overlay."
                        "qc-cmp2-footer-scrolled > div > button.css-13brqst"
                    ),
                )
            )
        )
        cookie_button.click()
        print("Cookie popup dismissed.")
    except Exception as e:
        print("No cookie popup found or error occurred:", e)

    try:
        anchor_tag = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    (
                        "body > main > div > div > div > div > div > div > div > "
                        "div.entry > div.tab-bar > ul > li.tab-control.active > a"
                    ),
                )
            )
        )
        anchor_tag.click()
        print("Clicked the anchor tag.")
    except Exception as e:
        print("Anchor tag not found or timeout:", e)

    # Step 2: Log in
    driver.find_element(By.ID, "email-superbru").send_keys(username)
    driver.find_element(By.ID, "password-superbru").send_keys(password)
    driver.find_element(
        By.XPATH,
        (
            "/html/body/main/div/div/div/div/div/div/div/div[3]/div[2]/div[1]/"
            "form/div[3]/input"
        ),
    ).submit()

    # Step 3: Wait for the table to load and scrape it
    time.sleep(1)
    table = driver.find_element(
        By.XPATH,
        ("/html/body/main/div/div[2]/div/div[3]/div[2]/div/div[2]/table"),
    )
    html = table.get_attribute("outerHTML")

    soup = BeautifulSoup(html, "html.parser")
    rows = [[cell.text for cell in row.find_all("td")] for row in soup.find_all("tr")]

    print(rows)
    top_global_points = rows[2][-1]
    top_global_250_points = rows[-1][-1]
    print(top_global_points, top_global_250_points)

    driver.quit()
    return top_global_points, top_global_250_points
