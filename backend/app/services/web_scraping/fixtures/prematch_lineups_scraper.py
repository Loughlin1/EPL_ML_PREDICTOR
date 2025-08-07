"""
prematch_lineups_scraper.py

    Module to scrape the pre-match lineups from the BBC Sports website
    when announced before the game.
"""

import re
import time
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


base_url = f"https://www.bbc.com/sport/football/premier-league/scores-fixtures"


def find_match_link(driver: webdriver.Chrome, home_team: str, away_team: str):
    try:
        element = driver.find_element(By.XPATH, f"//*[contains(text(),'{home_team}') and contains(text(), '{away_team}')]")
        # print(f"Element with partial text found: {element.text}, {element.tag_name}")
        parent_element = element.find_element(By.XPATH, "..")
        # print(f"parent element: {parent_element}, {parent_element.tag_name}")
        link_element = parent_element.find_element(By.XPATH, "..")
        # print(f"link element: {link_element}, {link_element.tag_name}")
        link = link_element.get_attribute("href")
        print(f"link found: {link}")
        return f"{link}#Line-ups"
    except:
        print("Partial text not found on the page.")
        return None


def find_formations(driver: webdriver.Chrome) -> tuple[str, str]:
    try:
        elements = driver.find_elements(By.XPATH, "//*[contains(text(),'Formation:')]")
        home_formation_element = elements[0]
        home_formation_element = home_formation_element.find_element(By.XPATH, "following-sibling::span[1]")
        home_formation = home_formation_element.text
        home_formation = home_formation.replace(" ", "") if home_formation else None
        print(f"Home Formation found: {home_formation}")

        away_formation_element = elements[1]
        away_formation_element = away_formation_element.find_element(By.XPATH, "following-sibling::span[1]")
        away_formation = away_formation_element.text
        away_formation = away_formation.replace(" ", "") if away_formation else None
        print(f"Away Formation found: {away_formation}")
        return home_formation, away_formation_element
    except:
        error = traceback.format_exc()
        print(f"Error: {error}")
        print("Formation element not found on the page.")
        return None, None


def find_lineups(driver: webdriver.Chrome):
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "[class*='PlayerList']")
        print(f"Found {len(elements)} elements")
        for element in elements:
            text = element.text
            regex_name = re.compile(r'^([A-Z]\.)([a-z]+)*( [a-z]+)*$', re.IGNORECASE)
            print(text)
            match = re.search('\b\w\.\s*(\1)\b', text, re.IGNORECASE)
            if match:
                print(f"Match found: {match.group(1)}")
    except:
        error = traceback.format_exc()
        print(f"Error: {error}")
        print("Lineups elements not found on the page.")



def get_match_report(home_team: str, away_team: str) -> dict:
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    current_month = "2025-05" #datetime.date.today().strftime('%Y-%m')
    target_url = f"{base_url}/{current_month}"
    driver.get(target_url)

    link = find_match_link(driver, home_team, away_team)
    if not link:
        driver.quit()
        return

    driver.get(link)
    time.sleep(1)
    home_formation, away_formation = find_formations(driver)
    find_lineups(driver)
    # time.sleep(10)
    driver.quit()

# get_match_report("Ipswich Town", "West Ham United")