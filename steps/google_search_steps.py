import pytest
from pytest_bdd import given, when, then, parsers, scenarios
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.wait_utils import WaitUtils

scenarios("../features/google_search.feature")

SEARCH_BOX = (By.NAME, "q")
RESULTS    = (By.ID, "search")


@given("the browser is open on Google")
def open_google(driver):
    driver.get("https://www.google.com")
    wait = WaitUtils(driver)
    wait.wait_for_page_load()
    print("Google opened!")


@when(parsers.parse('the user types "{text}" in search box'))
def type_in_search(driver, text):
    wait    = WaitUtils(driver)
    search  = wait.wait_for_element_visible(SEARCH_BOX)
    search.clear()
    search.send_keys(text)
    print(f"Typed: {text}")


@when("the user presses Enter")
def press_enter(driver):
    wait   = WaitUtils(driver)
    search = wait.wait_for_element_visible(SEARCH_BOX)
    search.send_keys(Keys.RETURN)
    print("Pressed Enter")


@then("the results page should load")
def results_page_loads(driver):
    wait = WaitUtils(driver)
    wait.wait_for_url_contains("search")
    assert "search" in driver.current_url
    print(f"Results loaded: {driver.current_url}")


@then(parsers.parse('the URL should contain "{text}"'))
def url_contains(driver, text):
    assert text in driver.current_url, \
        f"Expected '{text}' in URL: {driver.current_url}"
    print(f"URL contains '{text}' - OK")


@then("the search box should be visible")
def search_box_visible(driver):
    wait   = WaitUtils(driver)
    search = wait.wait_for_element_visible(SEARCH_BOX)
    assert search.is_displayed()
    print("Search box is visible!")


@then(parsers.parse('the page title should contain "{text}"'))
def title_contains(driver, text):
    assert text in driver.title, \
        f"Expected '{text}' in title: {driver.title}"
    print(f"Title contains '{text}' - OK")