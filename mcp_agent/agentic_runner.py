import time
from dataclasses import dataclass, field
from loguru import logger
from config.config import config


@dataclass
class AgentResult:
    goal:        str
    steps_taken: list  = field(default_factory=list)
    passed:      int   = 0
    failed:      int   = 0
    errors:      list  = field(default_factory=list)
    duration:    float = 0.0
    report:      str   = ""

    @property
    def success_rate(self) -> float:
        total = self.passed + self.failed
        return round((self.passed / total) * 100, 1) if total else 0.0


class AgenticTestRunner:

    def __init__(self):
        self.ai_enabled = False
        logger.info("AgenticRunner ready in demo mode")

    def run_goal(self, goal: str, url: str = None) -> AgentResult:
        result = AgentResult(goal=goal)
        start  = time.time()
        logger.info(f"Goal: {goal}")

        from utils.driver_factory import DriverFactory
        from utils.wait_utils import WaitUtils
        from utils.screenshot_utils import ScreenshotUtils
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys

        driver = None
        try:
            driver = DriverFactory.get_driver()
            driver.maximize_window()
            wait = WaitUtils(driver)

            # Step 1 - Navigate
            target = url or config.BASE_URL
            driver.get(target)
            wait.wait_for_page_load()
            result.steps_taken.append(
                {"step": "navigate", "status": "passed"}
            )
            result.passed += 1
            logger.success(f"Navigated to {target}")

            # Step 2 - Verify page loaded
            title = driver.title
            assert len(title) > 0
            result.steps_taken.append(
                {"step": "verify_title", "status": "passed"}
            )
            result.passed += 1
            logger.success(f"Title: {title}")

            # Step 3 - Search on Google
            if "google" in target.lower():
                search = wait.wait_for_element_visible(
                    (By.NAME, "q")
                )
                search.clear()
                search.send_keys("Selenium MCP automation")
                search.send_keys(Keys.RETURN)
                wait.wait_for_url_contains("search")
                result.steps_taken.append(
                    {"step": "search", "status": "passed"}
                )
                result.passed += 1
                logger.success("Search completed!")

            # Step 4 - Screenshot
            sc   = ScreenshotUtils(driver)
            path = sc.capture("agent_run")
            result.steps_taken.append(
                {"step": "screenshot", "path": path, "status": "passed"}
            )
            result.passed += 1
            logger.success(f"Screenshot: {path}")

        except Exception as e:
            logger.error(f"Failed: {e}")
            result.failed += 1
            result.errors.append(str(e))
        finally:
            if driver:
                driver.quit()

        result.duration = round(time.time() - start, 2)
        result.report   = self._build_report(result)
        return result

    def _build_report(self, result: AgentResult) -> str:
        lines = [
            "AGENTIC TEST REPORT",
            "=" * 50,
            f"Goal:     {result.goal}",
            f"Duration: {result.duration}s",
            f"Passed:   {result.passed}",
            f"Failed:   {result.failed}",
            f"Rate:     {result.success_rate}%",
            "=" * 50,
            "Steps:",
        ]
        for i, step in enumerate(result.steps_taken, 1):
            icon = "PASS" if step["status"] == "passed" else "FAIL"
            lines.append(f"  {i}. [{icon}] {step['step']}")
        if result.errors:
            lines.append("Errors:")
            for e in result.errors:
                lines.append(f"  - {e}")
        return "\n".join(lines)