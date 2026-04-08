from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from utils.wait_utils import WaitUtils
from utils.screenshot_utils import ScreenshotUtils
from config.config import config


class BasePage:

    def __init__(self, driver):
        self.driver     = driver
        self.wait       = WaitUtils(driver)
        self.screenshot = ScreenshotUtils(driver)
        self.base_url   = config.BASE_URL

    def open(self, path: str = "") -> "BasePage":
        url = f"{self.base_url}/{path}".rstrip("/")
        self.driver.get(url)
        self.wait.wait_for_page_load()
        print(f"Opened: {url}")
        return self

    def find(self, locator: tuple):
        return self.wait.wait_for_element_visible(locator)

    def click(self, locator: tuple) -> "BasePage":
        element = self.wait.wait_for_element_clickable(locator)
        element.click()
        print(f"Clicked: {locator}")
        return self

    def type_text(self, locator: tuple, text: str) -> "BasePage":
        element = self.find(locator)
        element.clear()
        element.send_keys(text)
        print(f"Typed '{text}' into {locator}")
        return self

    def get_text(self, locator: tuple) -> str:
        return self.find(locator).text

    def is_visible(self, locator: tuple) -> bool:
        try:
            return self.find(locator).is_displayed()
        except Exception:
            return False

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    def scroll_to(self, locator: tuple) -> "BasePage":
        element = self.find(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView(true);", element
        )
        return self

    def js_click(self, locator: tuple) -> "BasePage":
        element = self.find(locator)
        self.driver.execute_script("arguments[0].click();", element)
        return self

    def assert_url_contains(self, partial: str) -> "BasePage":
        self.wait.wait_for_url_contains(partial)
        return self

    def select_dropdown(self, locator: tuple,
                        value: str = None,
                        text: str = None) -> "BasePage":
        element = self.find(locator)
        sel = Select(element)
        if value:
            sel.select_by_value(value)
        elif text:
            sel.select_by_visible_text(text)
        return self