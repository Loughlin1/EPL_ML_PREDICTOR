
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def close_pop_up(driver: WebDriver, selector: str, by: str = "css"):
    """
    Attempts to close a popup using the given selector.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        selector (str): The selector string (CSS or XPath).
        by (str): Selector type, "css" for CSS selector, "xpath" for XPath. Default is "css".
    """
    try:
        if by == "css":
            popup = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
        elif by == "xpath":
            popup = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
        else:
            raise ValueError("Selector type must be 'css' or 'xpath'")
        popup.click()
        print("Popup dismissed.")
    except Exception as e:
        print(f"No popup found or error occurred: {e}")