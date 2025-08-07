"""
prematch_lineups_scraper.py

    Module to scrape the pre-match lineups from the BBC Sports website
    when announced before the game.
"""

import random
import time
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from helper import match_on_name

base_url = f"https://www.bbc.com/sport/football/premier-league/scores-fixtures"


def print_element(element):
    print(f"Tag: {element.tag_name}, Class: {element.get_attribute('class')}, Text: {element.get_attribute('textContent')}")


def find_match_link(driver: webdriver.Chrome, home_team: str, away_team: str):
    try:
        element = driver.find_element(By.XPATH, f"//*[contains(text(),'{home_team}') and contains(text(), '{away_team}')]")
        parent_element = element.find_element(By.XPATH, "..")
        link_element = parent_element.find_element(By.XPATH, "..")
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
        home_formation_value_element = home_formation_element.find_element(By.XPATH, "following-sibling::span[1]")
        home_formation_value = home_formation_value_element.text
        home_formation = home_formation_value.replace(" ", "") if home_formation_value else None
        # print(f"Home Formation found: {home_formation}")

        away_formation_element = elements[1]
        away_formation_value_element = away_formation_element.find_element(By.XPATH, "following-sibling::span[1]")
        away_formation_value = away_formation_value_element.text
        away_formation = away_formation_value.replace(" ", "") if away_formation_value else None
        # print(f"Away Formation found: {away_formation}")
        return home_formation, away_formation
    except:
        error = traceback.format_exc()
        print(f"Error: {error}")
        print("Formation element not found on the page.")
        return None, None


def find_lineups(driver: webdriver.Chrome, team: str):
    def get_player_names_from_list(player_items: list):
        names = []
        for player in player_items:
            player_wrapper = player.find_element(By.XPATH, ".//div[contains(@class, 'PlayerWrapper')]")
            player_name_wrapper = player_wrapper.find_element(By.XPATH, ".//span[contains(@class, 'PlayerNameWrapper')]")
            name = player_name_wrapper.find_element(By.XPATH, ".//span[contains(@class, 'PlayerName')]")
            player_name = name.get_attribute("textContent")
            names.append(player_name)
        return names

    try:
        # elements = driver.find_elements(By.CSS_SELECTOR, "[class*='PlayerList']")
        team = team.replace(" ", "")
        team_sections = driver.find_elements(By.ID, team)
        section = team_sections[1]
        first_child_div = section.find_element(By.CSS_SELECTOR, "div:first-child")
        starting_div = first_child_div.find_element(By.XPATH, ".//div[contains(@class, 'TeamPlayers')]")
        subs_section = first_child_div.find_element(By.XPATH, ".//section[contains(@class, 'Substitutes')]")

        # Team Lineup  
        player_list = starting_div.find_element(By.XPATH, ".//ul[contains(@class, 'PlayerList')]")
        player_items = player_list.find_elements(By.TAG_NAME, "li")
        team_lineup = get_player_names_from_list(player_items)
        
        # Substitutes
        subs_list_div = subs_section.find_element(By.XPATH, ".//div[contains(@class, 'TeamPlayers')]")
        subs_list = subs_list_div.find_element(By.XPATH, ".//ul[contains(@class, 'PlayerList')]")
        subs_items = subs_list.find_elements(By.TAG_NAME, "li")
        team_subs = get_player_names_from_list(subs_items)
        return team_lineup, team_subs
    except:
        error = traceback.format_exc()
        print(f"Error: {error}")
        print("Lineups elements not found on the page.")
        return [], []


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
    home_starting_lineup, home_subs_list = find_lineups(driver, home_team)
    away_starting_lineup, away_subs_list = find_lineups(driver, away_team)
    driver.quit()
    return {
        "home_formation": home_formation,
        "away_formation": away_formation,
        "home_starting_lineup": home_starting_lineup,
        "home_subs_list": home_subs_list,
        "away_starting_lineup": away_starting_lineup,
        "away_subs_list": away_subs_list,
    }

# print(get_match_report("Ipswich Town", "West Ham United"))
