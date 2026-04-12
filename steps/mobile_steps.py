"""
Mobile BDD Step Definitions
"""
import pytest
from pytest_bdd import given, when, then, parsers, scenarios
from mobile.login_mobile_page import MobileLoginPage
from mobile.mobile_driver_factory import MobileDriverFactory

scenarios("../features/mobile_login.feature")

_page = None


@given("the mobile app login screen is open")
def mobile_login_open():
    global _page
    driver = MobileDriverFactory.get_driver("DEMO")
    _page  = MobileLoginPage(driver)
    _page.reset()
    print("[DEMO] Mobile login screen opened")


@when(parsers.parse('the user enters mobile email "{email}"'))
def enter_mobile_email(email):
    _page.enter_email(email)


@when(parsers.parse('the user enters mobile password "{password}"'))
def enter_mobile_password(password):
    _page.enter_password(password)


@when("the user taps the login button")
def tap_login():
    _page.tap_login()


@then("the mobile login should be successful")
def login_successful():
    assert _page.is_login_successful(), \
        "Mobile login should succeed"


@then("no error message should be displayed")
def no_error():
    assert not _page.is_error_shown(), \
        "No error should be shown after successful login"


@then("a mobile error message should appear")
def error_appears():
    assert _page.is_error_shown(), \
        "Error message should appear"


@then(parsers.parse('the error should say "{message}"'))
def error_message(message):
    actual = _page.get_error_text()
    assert message in actual, \
        f"Expected '{message}' in '{actual}'"