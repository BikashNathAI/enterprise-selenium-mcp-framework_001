from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config.config import config

class WaitUtils:

    def __init__(self, driver):
        self.driver = driver
        self.timeout = config.EXPLICIT_WAIT

    def wait_for_element_visible(self, locator: tuple, timeout: int = None):
        t = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, t).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            print(f"Element not visible after {t}s: {locator}")
            raise

    def wait_for_element_clickable(self, locator: tuple, timeout: int = None):
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_url_contains(self, partial_url: str, timeout: int = None):
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.url_contains(partial_url)
        )

    def wait_for_text_in_element(self, locator: tuple, text: str, timeout: int = None):
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.text_to_be_present_in_element(locator, text)
        )

    def wait_for_page_load(self, timeout: int = None):
        t = timeout or self.timeout
        WebDriverWait(self.driver, t).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )