"""
superbru/login.py

This module contains the `login_to_superbru` function which handles the
login process for Superbru.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def handle_cookie_popup(driver: WebDriver):
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


def login_to_superbru(driver: WebDriver, username: str, password: str):
    driver.get("https://www.superbru.com/login")
    time.sleep(1)
    handle_cookie_popup(driver)
    driver.find_element(By.ID, "email-superbru").send_keys(username)
    driver.find_element(By.ID, "password-superbru").send_keys(password)
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    # Wait for login to complete (adjust as needed)
    time.sleep(2)

