import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    BROWSER        = os.getenv("BROWSER", "chrome")
    HEADLESS       = os.getenv("HEADLESS", "false").lower() == "true"
    IMPLICIT_WAIT  = int(os.getenv("IMPLICIT_WAIT", 10))
    EXPLICIT_WAIT  = int(os.getenv("EXPLICIT_WAIT", 20))
    BASE_URL       = os.getenv("BASE_URL", "https://www.google.com")

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    MCP_ENABLED       = os.getenv("MCP_ENABLED", "false").lower() == "true"

    OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
    OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    OLLAMA_URL     = os.getenv("OLLAMA_URL", "http://localhost:11434")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    SELENIUM_GRID_URL       = os.getenv("SELENIUM_GRID_URL", "")
    BROWSERSTACK_USERNAME   = os.getenv("BROWSERSTACK_USERNAME", "")
    BROWSERSTACK_ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY", "")

    DB_URL = os.getenv("DB_URL", "")

    APPIUM_SERVER_URL = os.getenv("APPIUM_SERVER_URL", "http://localhost:4723")
    PLATFORM_NAME     = os.getenv("PLATFORM_NAME", "Android")
    APP_PATH          = os.getenv("APP_PATH", "")

    SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    ALLURE_RESULTS_DIR    = os.getenv("ALLURE_RESULTS_DIR", "reports/allure-results")

    SCREENSHOTS_DIR = BASE_DIR / "screenshots"
    LOGS_DIR        = BASE_DIR / "logs"
    DATA_DIR        = BASE_DIR / "data"

    @classmethod
    def validate(cls):
        print("Config loaded successfully!")
        print(f"  Browser      : {cls.BROWSER}")
        print(f"  Base URL     : {cls.BASE_URL}")
        print(f"  Ollama       : {cls.OLLAMA_ENABLED}")
        print(f"  Ollama Model : {cls.OLLAMA_MODEL}")
        print(f"  MCP Enabled  : {cls.MCP_ENABLED}")


config = Config()