from datetime import datetime
from config.config import config

class ScreenshotUtils:

    def __init__(self, driver):
        self.driver = driver
        self.screenshots_dir = config.SCREENSHOTS_DIR
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, name: str = "screenshot") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"{name}_{timestamp}.png"
        filepath  = self.screenshots_dir / filename
        self.driver.save_screenshot(str(filepath))
        print(f"Screenshot saved: {filepath}")
        return str(filepath)