"""
NLP Processor
Converts plain English requirements into
structured test artifacts using Ollama AI.

Example:
Input:  "user should be able to login with Google OAuth"
Output: Gherkin feature + test cases + locator suggestions
"""
import json
import re
from loguru import logger
from config.config import config


class NLPProcessor:
    """
    Natural Language Processing for test generation.
    Understands plain English and converts to test artifacts.
    """

    def __init__(self):
        if config.OLLAMA_ENABLED:
            import ollama
            self.ollama     = ollama
            self.ai_enabled = True
            logger.info("NLPProcessor: Ollama mode ready")
        else:
            self.ollama     = None
            self.ai_enabled = False
            logger.warning("NLPProcessor: template mode")

    def requirement_to_gherkin(self, requirement: str) -> str:
        """
        Convert plain English requirement to Gherkin.

        Input:  "login page should validate empty password"
        Output: Full .feature file content
        """
        if not self.ai_enabled:
            return self._template_gherkin(requirement)

        prompt = f"""Convert this requirement to a Gherkin feature file:

Requirement: {requirement}

Return ONLY valid Gherkin syntax like this:
Feature: [feature name]

  Scenario: [scenario name]
    Given [precondition]
    When [action]
    Then [expected result]

  Scenario Outline: [data driven scenario]
    Given [precondition]
    When [action with <param>]
    Then [expected result]

    Examples:
      | param |
      | value1 |
      | value2 |

Return ONLY the Gherkin content. No explanation."""

        try:
            response = self.ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            gherkin = response["message"]["content"].strip()
            logger.success("Gherkin generated from requirement!")
            return gherkin
        except Exception as e:
            logger.error(f"NLP failed: {e}")
            return self._template_gherkin(requirement)

    def extract_test_entities(self, description: str) -> dict:
        """
        Extract key entities from test description.

        Input:  "login page email field and password field"
        Output: {
            "page": "login",
            "elements": ["email field", "password field"],
            "actions": ["enter", "click"],
            "assertions": ["visible", "enabled"]
        }
        """
        if not self.ai_enabled:
            return self._template_entities(description)

        prompt = f"""Extract test entities from: "{description}"

Return ONLY JSON:
{{
  "page": "page name",
  "elements": ["element1", "element2"],
  "actions": ["action1", "action2"],
  "assertions": ["assertion1", "assertion2"],
  "test_types": ["positive", "negative"]
}}

Return JSON only."""

        try:
            response = self.ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response["message"]["content"].strip()
            # Extract JSON
            start = raw.find("{")
            end   = raw.rfind("}") + 1
            if start != -1:
                raw = raw[start:end]
            entities = json.loads(raw)
            logger.success(f"Entities extracted: {entities}")
            return entities
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return self._template_entities(description)

    def generate_locator_suggestions(self,
                                     element_description: str) -> list:
        """
        Suggest Selenium locators for an element description.

        Input:  "submit button on login form"
        Output: [
            "button[type='submit']",
            "#login-submit",
            "//button[contains(text(),'Login')]"
        ]
        """
        if not self.ai_enabled:
            return [
                f"button[type='submit']",
                f"#submit-btn",
                f"//button[@type='submit']"
            ]

        prompt = f"""Suggest Selenium locators for: "{element_description}"

Return ONLY a JSON array of locator strings:
["css_selector_1", "css_selector_2", "xpath_1"]

Include CSS selectors and XPath. Return JSON array only."""

        try:
            response = self.ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            raw   = response["message"]["content"].strip()
            start = raw.find("[")
            end   = raw.rfind("]") + 1
            if start != -1:
                raw = raw[start:end]
            locators = json.loads(raw)
            logger.success(f"Locators suggested: {locators}")
            return locators
        except Exception as e:
            logger.error(f"Locator suggestion failed: {e}")
            return [f"#{element_description.replace(' ', '-').lower()}"]

    def analyze_test_coverage(self, test_files: list) -> dict:
        """
        Analyze existing tests and suggest missing coverage.
        """
        test_summary = "\n".join(test_files[:5])

        if not self.ai_enabled:
            return {
                "covered":  ["positive flows", "negative flows"],
                "missing":  ["edge cases", "performance tests"],
                "priority": "Add boundary value tests"
            }

        prompt = f"""Analyze these test files and suggest missing coverage:

{test_summary}

Return ONLY JSON:
{{
  "covered": ["what is tested"],
  "missing": ["what is missing"],
  "priority": "most important gap to fix"
}}"""

        try:
            response = self.ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            raw   = response["message"]["content"].strip()
            start = raw.find("{")
            end   = raw.rfind("}") + 1
            if start != -1:
                raw = raw[start:end]
            analysis = json.loads(raw)
            return analysis
        except Exception as e:
            logger.error(f"Coverage analysis failed: {e}")
            return {"error": str(e)}

    def _template_gherkin(self, requirement: str) -> str:
        return f"""Feature: {requirement}

  @positive
  Scenario: Successful execution
    Given the application is open
    When I perform the action
    Then the result should be successful

  @negative
  Scenario: Failed execution
    Given the application is open
    When I perform an invalid action
    Then an error message should appear"""

    def _template_entities(self, description: str) -> dict:
        words = description.lower().split()
        return {
            "page":       words[0] if words else "unknown",
            "elements":   [description],
            "actions":    ["click", "enter", "verify"],
            "assertions": ["visible", "present", "enabled"],
            "test_types": ["positive", "negative"]
        }