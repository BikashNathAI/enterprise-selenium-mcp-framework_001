from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from config.config import config


class DriverFactory:

    @staticmethod
    def get_driver(browser: str = None):
        browser = (browser or config.BROWSER).lower()
        print(f"Starting browser: {browser}")

        if browser == "chrome":
            return DriverFactory._get_chrome()
        elif browser == "firefox":
            return DriverFactory._get_firefox()
        else:
            raise ValueError(f"Unsupported browser: {browser}")

    @staticmethod
    def _get_chrome():
        opts = ChromeOptions()
        if config.HEADLESS:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        try:
            # Try webdriver-manager first
            service = ChromeService(ChromeDriverManager().install())
            driver  = webdriver.Chrome(service=service, options=opts)
        except Exception as e:
            print(f"WebDriver Manager failed: {e}")
            print("Trying Selenium built-in manager...")
            # Selenium 4.6+ can manage driver automatically
            driver = webdriver.Chrome(options=opts)

        driver.implicitly_wait(config.IMPLICIT_WAIT)
        print("Chrome started successfully!")
        return driver

    @staticmethod
    def _get_firefox():
        opts = FirefoxOptions()
        if config.HEADLESS:
            opts.add_argument("--headless")
        try:
            service = FirefoxService(GeckoDriverManager().install())
            driver  = webdriver.Firefox(service=service, options=opts)
        except Exception:
            driver = webdriver.Firefox(options=opts)
        driver.implicitly_wait(config.IMPLICIT_WAIT)
        print("Firefox started successfully!")
        return driver