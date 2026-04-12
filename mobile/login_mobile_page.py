"""
Mobile Login Page Object
Dual locators — Android + iOS
Works in demo mode without device
"""
from loguru import logger
from mobile.base_mobile_page import BaseMobilePage


class MobileLoginPage(BaseMobilePage):
    """
    Login screen Page Object for mobile app.

    Dual locators for Android and iOS.
    Demo mode returns mock responses.
    """

    # ── Android Locators ──────────────────────────────────────
    EMAIL_ANDROID    = ("id", "com.example.app:id/et_email")
    PASSWORD_ANDROID = ("id", "com.example.app:id/et_password")
    LOGIN_ANDROID    = ("id", "com.example.app:id/btn_login")
    ERROR_ANDROID    = ("id", "com.example.app:id/tv_error")
    TITLE_ANDROID    = ("id", "com.example.app:id/tv_title")

    # ── iOS Locators ──────────────────────────────────────────
    EMAIL_IOS    = ("accessibility id", "emailTextField")
    PASSWORD_IOS = ("accessibility id", "passwordTextField")
    LOGIN_IOS    = ("accessibility id", "loginButton")
    ERROR_IOS    = ("accessibility id", "errorLabel")
    TITLE_IOS    = ("accessibility id", "loginTitle")

    # ── Demo State ────────────────────────────────────────────
    _demo_email    = ""
    _demo_password = ""
    _demo_logged_in = False
    _demo_error    = ""

    @property
    def EMAIL(self):
        return self.by_platform(
            self.EMAIL_ANDROID, self.EMAIL_IOS
        )

    @property
    def PASSWORD(self):
        return self.by_platform(
            self.PASSWORD_ANDROID, self.PASSWORD_IOS
        )

    @property
    def LOGIN_BTN(self):
        return self.by_platform(
            self.LOGIN_ANDROID, self.LOGIN_IOS
        )

    @property
    def ERROR(self):
        return self.by_platform(
            self.ERROR_ANDROID, self.ERROR_IOS
        )

    def enter_email(self, email: str) -> "MobileLoginPage":
        if not self.driver:
            self._demo_email = email
            logger.info(f"[DEMO] Email entered: {email}")
            return self
        return self.type_text(self.EMAIL, email)

    def enter_password(self,
                        password: str) -> "MobileLoginPage":
        if not self.driver:
            self._demo_password = password
            logger.info("[DEMO] Password entered")
            return self
        return self.type_text(self.PASSWORD, password)

    def tap_login(self) -> "MobileLoginPage":
        if not self.driver:
            self._process_demo_login()
            return self
        return self.tap(self.LOGIN_BTN)

    def login(self, email: str,
               password: str) -> "MobileLoginPage":
        """Full login flow."""
        return (
            self.enter_email(email)
                .hide_keyboard()
                .enter_password(password)
                .hide_keyboard()
                .tap_login()
        )

    def get_error_text(self) -> str:
        if not self.driver:
            return self._demo_error
        return self.get_text(self.ERROR)

    def is_error_shown(self) -> bool:
        if not self.driver:
            return bool(self._demo_error)
        return self.is_visible(self.ERROR)

    def is_login_successful(self) -> bool:
        if not self.driver:
            return self._demo_logged_in
        return not self.is_visible(self.ERROR, timeout=2)

    def _process_demo_login(self):
        """Simulate login logic in demo mode."""
        valid_email    = "testuser@example.com"
        valid_password = "Test@1234"

        if (self._demo_email == valid_email and
                self._demo_password == valid_password):
            self._demo_logged_in = True
            self._demo_error     = ""
            logger.success("[DEMO] Login successful!")
        else:
            self._demo_logged_in = False
            self._demo_error     = "Invalid email or password"
            logger.warning("[DEMO] Login failed!")

    def reset(self):
        """Reset demo state for next test."""
        self._demo_email     = ""
        self._demo_password  = ""
        self._demo_logged_in = False
        self._demo_error     = ""