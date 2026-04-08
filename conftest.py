import pytest
from utils.driver_factory import DriverFactory
from utils.screenshot_utils import ScreenshotUtils
from config.config import config


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--env",     action="store", default="staging")


@pytest.fixture(scope="function")
def driver(request):
    browser = request.config.getoption("--browser")
    _driver = DriverFactory.get_driver(browser=browser)
    _driver.maximize_window()

    yield _driver

    # Screenshot on failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        if config.SCREENSHOT_ON_FAILURE:
            sc   = ScreenshotUtils(_driver)
            path = sc.capture(name=request.node.name)
            print(f"Failure screenshot: {path}")

    _driver.quit()
    print("Browser closed.")


@pytest.fixture(scope="session")
def api_client():
    from api.api_client import APIClient
    return APIClient(base_url=config.BASE_URL)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep     = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)