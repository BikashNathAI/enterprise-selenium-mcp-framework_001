import pytest
from pages.login_page import LoginPage
from data.data_factory import DataFactory


class TestLogin:

    @pytest.mark.smoke
    @pytest.mark.ui
    def test_google_opens(self, driver):
        """
        Simple smoke test — opens Google and checks title.
        Works without any login credentials.
        """
        driver.get("https://www.google.com")
        title = driver.title
        print(f"Page title: {title}")
        assert "Google" in title, f"Expected Google in title, got: {title}"

    @pytest.mark.smoke
    @pytest.mark.ui
    def test_google_search_box_visible(self, driver):
        """
        Check Google search input is visible.
        """
        from selenium.webdriver.common.by import By
        from utils.wait_utils import WaitUtils

        driver.get("https://www.google.com")
        wait    = WaitUtils(driver)
        search  = wait.wait_for_element_visible(
            (By.NAME, "q")
        )
        assert search.is_displayed(), "Search box should be visible"
        print("Google search box is visible!")

    @pytest.mark.smoke
    @pytest.mark.ui
    def test_google_search_works(self, driver):
        """
        Type in Google search and verify results page loads.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from utils.wait_utils import WaitUtils

        driver.get("https://www.google.com")
        wait   = WaitUtils(driver)
        search = wait.wait_for_element_visible((By.NAME, "q"))
        search.clear()
        search.send_keys("Selenium automation")
        search.send_keys(Keys.RETURN)
        wait.wait_for_url_contains("search")
        assert "search" in driver.current_url
        print("Search worked! URL:", driver.current_url)

    @pytest.mark.regression
    @pytest.mark.ui
    def test_faker_generates_user(self, driver):
        """
        Verify DataFactory generates valid user data.
        Does not need a browser — just checks the data layer.
        """
        user = DataFactory.generate_user()
        print(f"Generated: {user['first_name']} - {user['email']}")
        assert "@" in user["email"],    "Email should contain @"
        assert len(user["password"]) >= 12, "Password too short"
        assert user["role"] == "customer"
        print("DataFactory working perfectly!")