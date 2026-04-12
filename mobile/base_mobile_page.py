"""
Enterprise Mobile Base Page
Supports Android (UiAutomator2) and iOS (XCUITest)
Works in demo mode without real device
"""
from loguru import logger
from config.config import config


class BaseMobilePage:
    """
    Base class for all Mobile Page Objects.
    All mobile pages inherit from this class.

    Supports:
    - Android via Appium UiAutomator2
    - iOS via Appium XCUITest
    - Demo mode (no device needed)
    """

    def __init__(self, driver=None):
        self.driver   = driver
        self.timeout  = config.EXPLICIT_WAIT
        self.platform = "DEMO"

        if driver:
            try:
                self.platform = driver.capabilities.get(
                    "platformName", "Android"
                ).upper()
            except Exception:
                self.platform = "ANDROID"

        logger.debug(
            f"Mobile page: {self.__class__.__name__} "
            f"[{self.platform}]"
        )

    def tap(self, locator: tuple) -> "BaseMobilePage":
        """Tap an element."""
        if not self.driver:
            logger.info(f"[DEMO] tap: {locator}")
            return self
        element = self._find(locator)
        element.click()
        logger.debug(f"Tapped: {locator}")
        return self

    def type_text(self, locator: tuple,
                   text: str) -> "BaseMobilePage":
        """Type text into an input field."""
        if not self.driver:
            logger.info(f"[DEMO] type_text: '{text}' → {locator}")
            return self
        element = self._find(locator)
        element.clear()
        element.send_keys(text)
        return self

    def get_text(self, locator: tuple) -> str:
        """Get text from an element."""
        if not self.driver:
            logger.info(f"[DEMO] get_text: {locator}")
            return "Demo Text"
        return self._find(locator).text

    def is_visible(self, locator: tuple,
                    timeout: int = 5) -> bool:
        """Check if element is visible."""
        if not self.driver:
            logger.info(f"[DEMO] is_visible: {locator}")
            return True
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    def scroll_down(self, swipes: int = 1) -> "BaseMobilePage":
        """Scroll down the screen."""
        if not self.driver:
            logger.info(f"[DEMO] scroll_down {swipes} times")
            return self
        size    = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.8)
        end_y   = int(size["height"] * 0.2)
        for _ in range(swipes):
            self.driver.swipe(start_x, start_y,
                              start_x, end_y, 600)
        return self

    def scroll_up(self, swipes: int = 1) -> "BaseMobilePage":
        """Scroll up the screen."""
        if not self.driver:
            logger.info(f"[DEMO] scroll_up {swipes} times")
            return self
        size    = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.2)
        end_y   = int(size["height"] * 0.8)
        for _ in range(swipes):
            self.driver.swipe(start_x, start_y,
                              start_x, end_y, 600)
        return self

    def hide_keyboard(self) -> "BaseMobilePage":
        """Hide the on-screen keyboard."""
        if not self.driver:
            logger.info("[DEMO] hide_keyboard")
            return self
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass
        return self

    def go_back(self) -> "BaseMobilePage":
        """Press the back button."""
        if not self.driver:
            logger.info("[DEMO] go_back")
            return self
        self.driver.back()
        return self

    def background_app(self,
                        seconds: int = 3) -> "BaseMobilePage":
        """Send app to background."""
        if not self.driver:
            logger.info(f"[DEMO] background_app {seconds}s")
            return self
        self.driver.background_app(seconds)
        return self

    def by_platform(self, android_locator: tuple,
                     ios_locator: tuple) -> tuple:
        """Return correct locator for current platform."""
        if self.platform == "IOS":
            return ios_locator
        return android_locator

    def _find(self, locator: tuple):
        """Find element with wait."""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )