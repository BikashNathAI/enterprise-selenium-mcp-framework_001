"""
AI Self-Healing Locator Engine
When a Selenium locator fails, this calls Claude AI
to suggest a working replacement locator.
"""
import json
from loguru import logger
from config.config import config


class SelfHealer:
    """
    How it works:
    1. A locator fails in your test
    2. SelfHealer captures the current page DOM
    3. Sends it to Claude AI with the broken locator
    4. Claude suggests a new working locator
    5. Test retries with the healed locator
    6. Repair is logged for your review
    """

    def __init__(self, driver):
        self.driver   = driver
        self.heal_log = []

        if config.MCP_ENABLED and config.ANTHROPIC_API_KEY:
            import anthropic
            self.client = anthropic.Anthropic(
                api_key=config.ANTHROPIC_API_KEY
            )
            self.ai_enabled = True
            logger.info("SelfHealer: AI mode enabled")
        else:
            self.client     = None
            self.ai_enabled = False
            logger.warning(
                "SelfHealer: AI disabled — "
                "set ANTHROPIC_API_KEY and MCP_ENABLED=true in .env"
            )

    def get_healed_locator(self, broken_locator: tuple,
                           element_description: str) -> tuple | None:
        """
        Main method — call this when a locator fails.
        Returns a new locator tuple or None if healing fails.

        Usage in your test:
            try:
                element = driver.find_element(*locator)
            except:
                healer = SelfHealer(driver)
                new_locator = healer.get_healed_locator(
                    locator, "submit button on login page"
                )
                if new_locator:
                    element = driver.find_element(*new_locator)
        """
        if not self.ai_enabled:
            logger.warning("AI healing skipped — not configured")
            return self._try_common_fallbacks(broken_locator)

        # Get page DOM snapshot (trimmed to 5000 chars)
        try:
            dom = self.driver.execute_script(
                "return document.documentElement.outerHTML;"
            )[:5000]
        except Exception as e:
            logger.error(f"Could not get DOM: {e}")
            return None

        prompt = f"""
You are a Selenium expert. A locator has FAILED.

BROKEN LOCATOR:
Type:  {broken_locator[0]}
Value: {broken_locator[1]}

ELEMENT DESCRIPTION: "{element_description}"

CURRENT PAGE DOM (truncated):
{dom}

Suggest ONE alternative locator. Reply in EXACTLY this format:
LOCATOR_TYPE: By.CSS_SELECTOR
LOCATOR_VALUE: button.submit-btn
REASON: Found matching element by class name

Only these 3 lines. Nothing else.
"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text.strip()
            lines    = response.split("\n")

            locator_type_str = lines[0].split(": ", 1)[1].strip()
            locator_value    = lines[1].split(": ", 1)[1].strip()
            reason           = lines[2].split(": ", 1)[1].strip()

            from selenium.webdriver.common.by import By
            by_map = {
                "By.CSS_SELECTOR": By.CSS_SELECTOR,
                "By.XPATH":        By.XPATH,
                "By.ID":           By.ID,
                "By.NAME":         By.NAME,
                "By.CLASS_NAME":   By.CLASS_NAME,
                "By.TAG_NAME":     By.TAG_NAME,
            }

            by_type = by_map.get(locator_type_str, By.CSS_SELECTOR)
            healed  = (by_type, locator_value)

            self.heal_log.append({
                "broken":      broken_locator,
                "healed":      healed,
                "reason":      reason,
                "description": element_description,
            })

            logger.success(
                f"Healed: {broken_locator} → {healed}"
            )
            logger.info(f"Reason: {reason}")
            return healed

        except Exception as e:
            logger.error(f"AI healing failed: {e}")
            return self._try_common_fallbacks(broken_locator)

    def _try_common_fallbacks(self, broken_locator: tuple) -> tuple | None:
        """
        Rule-based fallbacks when AI is not available.
        Tries common alternative locator patterns.
        """
        from selenium.webdriver.common.by import By

        by, value = broken_locator

        fallbacks = []

        # If ID fails, try name attribute
        if by == By.ID:
            fallbacks = [
                (By.NAME,         value),
                (By.CSS_SELECTOR, f"#{value}"),
                (By.CSS_SELECTOR, f"[id='{value}']"),
            ]

        # If CSS fails, try XPath
        elif by == By.CSS_SELECTOR:
            fallbacks = [
                (By.XPATH, f"//*[@class='{value}']"),
                (By.XPATH, f"//*[contains(@class,'{value}')]"),
            ]

        # If XPath fails, try CSS
        elif by == By.XPATH:
            fallbacks = [
                (By.CSS_SELECTOR, value.replace("//", "")),
            ]

        for fallback in fallbacks:
            try:
                self.driver.find_element(*fallback)
                logger.info(f"Fallback worked: {fallback}")
                return fallback
            except Exception:
                continue

        logger.error("All fallbacks failed")
        return None

    def save_heal_report(self, path: str = "reports/heal_report.json"):
        """Save all healing events to a JSON report."""
        import os
        os.makedirs("reports", exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.heal_log, f, indent=2)
        logger.info(f"Heal report saved: {path}")
        return path