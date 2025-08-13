import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .login import login_to_superbru
from .popups import close_pop_up
from ....core.config import settings

# ABBREVIATIONS:
# h - home team, a - away team


def check_team_names_match(input_team: str, team_name: str, team_fullname: str):
    special_mappings = {
        "Manchester Utd": "Man. United",
        "Manchester City": "Man. City",
    }
    return input_team in [team_name, team_fullname, special_mappings.get(team_name)]


def save_predictions(driver: webdriver) -> None:
    """
    This function clicks the button to save the predictions on the SuperBru website.
    """
    # Hide the overlay if it exists
    try:
        driver.execute_script("document.querySelector('.rugby-trigger-mask').style.display = 'none';")
    except Exception as e:
        print("No rugby-trigger-mask overlay found or error hiding it:", e)

    # Now click the Continue button
    continue_button = driver.find_element(By.CSS_SELECTOR, "input.button[type='submit'][value='Continue']")
    continue_button.click()
    time.sleep(2)  # Short wait to ensure submission


def find_and_input_predictions(driver: webdriver, predictions: list[dict]) -> None:
    """
    This function finds and inputs the predictions on the SuperBru website.
    """
    for pred in predictions:
        PredFTHG = pred["PredFTHG"]
        PredFTAG = pred["PredFTAG"]

        driver.execute_script("window.stop();") # Prevent popups
        home_team_goal_inputs = driver.find_elements(
            By.XPATH, "//input[@class='editable-dropdown soccer-left-score']"
        )
        away_team_goal_inputs = driver.find_elements(
            By.XPATH, "//input[@class='editable-dropdown soccer-right-score']"
        )

        for h_element, a_element in zip(home_team_goal_inputs, away_team_goal_inputs):
            h_team_name = h_element.get_attribute("data-bru-team-name")
            a_team_name = a_element.get_attribute("data-bru-team-name")
            if (
                check_team_names_match(h_team_name, pred["home_team"], pred["home_team_fullname"])
                and check_team_names_match(a_team_name, pred["away_team"], pred["away_team_fullname"])
            ):
                print(f"Submitting prediction for {h_team_name} vs {a_team_name}: {pred['PredFTHG']}-{pred['PredFTAG']}")
                h_element.clear()
                h_element.send_keys(str(PredFTHG))
                a_element.clear()
                a_element.send_keys(str(PredFTAG))
                break


def submit_to_superbru(predictions: list[dict], week: int):

    # Step 1: Set up WebDriver
    options = Options()
    options.headless = False #True
    driver = webdriver.Chrome(options=options)

    # Step 2: Log in
    login_to_superbru(driver, settings.SUPERBRU_USERNAME, settings.SUPERBRU_PASSWORD)

    # Navigate and submit predictions (update selectors as needed)
    predictions_url = f"https://www.superbru.com/premierleague_predictor/play_tipping.php#tab=round{week}"
    driver.get(predictions_url)
    time.sleep(5) # Wait for the page to load
    close_pop_up(driver, "//button[text()='Close']", by="xpath")
    time.sleep(1) # Wait for the page to load

    find_and_input_predictions(driver, predictions)
    save_predictions(driver)
    driver.quit()


if __name__ == "__main__":
    predictions = [
        {
            "home_team": "Liverpool",
            "home_team_fullname": "Liverpool",
            "away_team": "Bournemouth",
            "away_team_fullname": "Bournemouth",
            "PredFTHG": 2,
            "PredFTAG": 1,
        }
    ]
    submit_to_superbru(predictions, week=1)