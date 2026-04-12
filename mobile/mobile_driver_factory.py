"""
Appium Mobile Driver Factory
Supports Android and iOS
Demo mode when no device connected
"""
from loguru import logger
from config.config import config


class MobileDriverFactory:
    """
    Creates Appium drivers for Android and iOS.

    Usage:
        driver = MobileDriverFactory.get_driver("ANDROID")
        driver = MobileDriverFactory.get_driver("IOS")
        driver = MobileDriverFactory.get_driver("DEMO")
    """

    @staticmethod
    def get_driver(platform: str = None):
        platform = (
            platform or config.PLATFORM_NAME
        ).upper()
        logger.info(f"Creating mobile driver: {platform}")

        if platform == "DEMO":
            logger.warning("Running in DEMO mode — no device")
            return None

        if platform == "ANDROID":
            return MobileDriverFactory._android()
        elif platform == "IOS":
            return MobileDriverFactory._ios()
        else:
            logger.warning(f"Unknown platform: {platform}")
            return None

    @staticmethod
    def _android():
        """Create Android driver via Appium."""
        try:
            from appium import webdriver
            from appium.options import UiAutomator2Options

            options = UiAutomator2Options()
            options.platform_name       = "Android"
            options.automation_name     = "UiAutomator2"
            options.app                 = config.APP_PATH
            options.no_reset            = False
            options.new_command_timeout = 300
            options.auto_grant_permissions = True

            driver = webdriver.Remote(
                command_executor=config.APPIUM_SERVER_URL,
                options=options
            )
            logger.success("Android driver ready!")
            return driver

        except Exception as e:
            logger.error(f"Android driver failed: {e}")
            logger.warning("Switching to DEMO mode")
            return None

    @staticmethod
    def _ios():
        """Create iOS driver via Appium."""
        try:
            from appium import webdriver
            from appium.options import XCUITestOptions

            options = XCUITestOptions()
            options.platform_name       = "iOS"
            options.automation_name     = "XCUITest"
            options.app                 = config.APP_PATH
            options.no_reset            = False
            options.new_command_timeout = 300

            driver = webdriver.Remote(
                command_executor=config.APPIUM_SERVER_URL,
                options=options
            )
            logger.success("iOS driver ready!")
            return driver

        except Exception as e:
            logger.error(f"iOS driver failed: {e}")
            logger.warning("Switching to DEMO mode")
            return None

    @staticmethod
    def get_capabilities_info() -> dict:
        """Return current capability settings."""
        return {
            "platform":    config.PLATFORM_NAME,
            "appium_url":  config.APPIUM_SERVER_URL,
            "app_path":    config.APP_PATH,
            "demo_mode":   not bool(config.APP_PATH),
        }