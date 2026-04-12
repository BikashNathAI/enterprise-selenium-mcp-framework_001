"""
Mobile Tests — Demo Mode
Runs without real device or emulator.
Connect real device → change PLATFORM_NAME in .env
"""
import pytest
from mobile.mobile_driver_factory import MobileDriverFactory
from mobile.login_mobile_page import MobileLoginPage
from data.data_factory import DataFactory


@pytest.fixture(scope="function")
def mobile_driver():
    """
    Mobile driver fixture.
    Returns None in demo mode — pages handle it gracefully.
    """
    driver = MobileDriverFactory.get_driver("DEMO")
    yield driver
    if driver:
        driver.quit()


@pytest.fixture(scope="function")
def login_page(mobile_driver):
    """Fresh login page for each test."""
    page = MobileLoginPage(mobile_driver)
    yield page
    page.reset()  # Clean demo state


class TestMobileLogin:

    @pytest.mark.mobile
    @pytest.mark.smoke
    def test_valid_login_succeeds(self, login_page):
        """Valid credentials should login successfully."""
        users = DataFactory.get_json("users")
        user  = users["valid_user"]

        login_page.login(user["email"], user["password"])

        assert login_page.is_login_successful(), \
            "Login should succeed with valid credentials"
        print(f"PASS: Login successful for {user['email']}")

    @pytest.mark.mobile
    @pytest.mark.negative
    def test_invalid_email_shows_error(self, login_page):
        """Invalid email should show error message."""
        login_page.login("wrong@email.com", "wrongpass")

        assert login_page.is_error_shown(), \
            "Error should be shown for invalid credentials"
        error = login_page.get_error_text()
        assert "Invalid" in error
        print(f"PASS: Error shown — '{error}'")

    @pytest.mark.mobile
    @pytest.mark.negative
    def test_empty_email_shows_error(self, login_page):
        """Empty email should show error."""
        login_page.login("", "Test@1234")
        assert login_page.is_error_shown()
        print("PASS: Empty email blocked!")

    @pytest.mark.mobile
    @pytest.mark.negative
    def test_empty_password_shows_error(self, login_page):
        """Empty password should show error."""
        login_page.login("testuser@example.com", "")
        assert login_page.is_error_shown()
        print("PASS: Empty password blocked!")

    @pytest.mark.mobile
    @pytest.mark.negative
    def test_wrong_password_shows_error(self, login_page):
        """Wrong password should show error."""
        login_page.login("testuser@example.com", "wrong")
        assert login_page.is_error_shown()
        error = login_page.get_error_text()
        assert len(error) > 0
        print(f"PASS: Wrong password error — '{error}'")

    @pytest.mark.mobile
    def test_login_page_elements_exist(self, login_page):
        """Verify all login page elements are accessible."""
        assert login_page.EMAIL    is not None
        assert login_page.PASSWORD is not None
        assert login_page.LOGIN_BTN is not None
        print("PASS: All login elements accessible!")

    @pytest.mark.mobile
    def test_driver_capabilities(self):
        """Verify mobile driver configuration."""
        caps = MobileDriverFactory.get_capabilities_info()
        assert "platform"   in caps
        assert "appium_url" in caps
        assert "demo_mode"  in caps
        print(f"Platform: {caps['platform']}")
        print(f"Demo mode: {caps['demo_mode']}")
        print("PASS: Driver capabilities verified!")

    @pytest.mark.mobile
    def test_data_factory_generates_user(self):
        """Verify DataFactory works for mobile tests."""
        user = DataFactory.generate_user()
        assert "@" in user["email"]
        assert len(user["password"]) >= 12
        print(f"PASS: Generated user — {user['email']}")

    @pytest.mark.mobile
    @pytest.mark.parametrize("email,password", [
        ("",                        "Test@1234"),
        ("testuser@example.com",    ""),
        ("notanemail",              "Test@1234"),
        ("wrong@email.com",         "wrongpass"),
    ])
    def test_invalid_credentials_parametrized(
            self, login_page, email, password):
        """Data-driven negative tests for mobile login."""
        login_page.login(email, password)
        assert login_page.is_error_shown(), \
            f"Error should show for email='{email}'"
        login_page.reset()
        print(f"PASS: Blocked — email='{email}'")