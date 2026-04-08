import json
from loguru import logger
from config.config import config


class MCPTestPlanner:

    def __init__(self):
        if config.OLLAMA_ENABLED:
            import ollama
            self.ollama     = ollama
            self.ai_enabled = True
            self.mode       = "ollama"
            logger.info(f"TestPlanner: Ollama mode — {config.OLLAMA_MODEL}")
        else:
            self.ollama     = None
            self.ai_enabled = False
            self.mode       = "template"
            logger.warning("TestPlanner: template mode")

    def generate_test_cases(self, feature_description: str) -> list:
        if self.ai_enabled:
            return self._generate_with_ollama(feature_description)
        return self._generate_template(feature_description)

    def _generate_with_ollama(self, description: str) -> list:
        prompt = f"""You are a QA expert. Generate test cases for: {description}

Return ONLY a JSON array, no other text:
[
  {{
    "test_id": "TC001",
    "title": "test title here",
    "type": "positive",
    "priority": "high",
    "steps": ["step 1", "step 2", "step 3"],
    "expected": "expected result",
    "gherkin": "Given...When...Then..."
  }}
]

Generate exactly 5 test cases covering positive, negative, and edge cases.
Return JSON array only. No explanation."""

        try:
            logger.info(f"Asking Ollama: {config.OLLAMA_MODEL}")
            response = self.ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response["message"]["content"].strip()

            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]

            start = raw.find("[")
            end   = raw.rfind("]") + 1
            if start != -1 and end > start:
                raw = raw[start:end]

            cases = json.loads(raw)
            logger.success(f"Ollama generated {len(cases)} test cases!")
            return cases

        except Exception as e:
            logger.error(f"Ollama failed: {e}")
            return self._generate_template(description)

    def _generate_template(self, description: str) -> list:
        return [
            {
                "test_id":  "TC001",
                "title":    f"Verify {description} - happy path",
                "type":     "positive",
                "priority": "high",
                "steps":    ["Open app", "Perform action", "Verify result"],
                "expected": "Action completes successfully",
                "gherkin":  f"Given app is open\nWhen I perform {description}\nThen it succeeds"
            },
            {
                "test_id":  "TC002",
                "title":    f"Verify {description} - invalid input",
                "type":     "negative",
                "priority": "high",
                "steps":    ["Open app", "Enter invalid data", "Verify error"],
                "expected": "Error message shown",
                "gherkin":  f"Given app is open\nWhen I enter invalid data\nThen error is shown"
            },
            {
                "test_id":  "TC003",
                "title":    f"Verify {description} - boundary values",
                "type":     "edge",
                "priority": "medium",
                "steps":    ["Open app", "Enter boundary values", "Verify behaviour"],
                "expected": "System handles edge case",
                "gherkin":  f"Given app is open\nWhen I enter boundary values\nThen system handles correctly"
            },
        ]

    def print_test_cases(self, cases: list):
        print(f"\n{'='*60}")
        print(f"Generated {len(cases)} Test Cases using {self.mode.upper()} AI")
        print('='*60)
        for case in cases:
            print(f"\n[{case.get('test_id', 'TC?')}] {case.get('title', 'No title')}")
            print(f"  Type:     {case.get('type', 'N/A')}")
            print(f"  Priority: {case.get('priority', 'N/A')}")
            gherkin = case.get('gherkin', case.get('scenario', 'N/A'))
            print(f"  Gherkin:  {str(gherkin)[:80]}...")
        print('='*60)