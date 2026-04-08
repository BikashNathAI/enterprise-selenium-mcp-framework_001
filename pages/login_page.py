from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class LoginPage(BasePage):

    # Locators
    EMAIL_INPUT      = (By.ID, "email")
    PASSWORD_INPUT   = (By.ID, "password")
    LOGIN_BUTTON     = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE    = (By.CSS_SELECTOR, ".error-message")
    DASHBOARD_HEADER = (By.CSS_SELECTOR, "h1.dashboard-title")

    PATH = "login"

    def open_login(self) -> "LoginPage":
        self.open(self.PATH)
        return self

    def enter_email(self, email: str) -> "LoginPage":
        self.type_text(self.EMAIL_INPUT, email)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        self.type_text(self.PASSWORD_INPUT, password)
        return self

    def click_login(self) -> "LoginPage":
        self.click(self.LOGIN_BUTTON)
        return self

    def login(self, email: str, password: str) -> "LoginPage":
        return (
            self.open_login()
                .enter_email(email)
                .enter_password(password)
                .click_login()
        )

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_login_error_visible(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE)

    def is_dashboard_visible(self) -> bool:
        return self.is_visible(self.DASHBOARD_HEADER)