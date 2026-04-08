"""
RAG-Enhanced Test Generator
Combines Ollama AI + Knowledge Base + NLP
to generate intelligent, context-aware tests.
"""
import json
from pathlib import Path
from loguru import logger
from mcp_agent.rag.knowledge_base import TestKnowledgeBase
from mcp_agent.rag.nlp_processor import NLPProcessor
from config.config import config


class RAGTestGenerator:
    """
    The most powerful component in the framework.
    
    It:
    1. Scans your existing framework (pages, tests, features)
    2. Builds a knowledge base
    3. When you ask for tests, it searches the knowledge base
    4. Feeds relevant context to Ollama AI
    5. Generates tests that match YOUR actual application

    Usage:
        gen = RAGTestGenerator()
        gen.build_knowledge_base()
        
        # Generate tests with full context awareness
        result = gen.generate_smart_tests(
            "checkout page with credit card payment"
        )
        print(result["test_cases"])
        print(result["gherkin"])
    """

    def __init__(self):
        self.kb    = TestKnowledgeBase(use_vector=False)
        self.nlp   = NLPProcessor()
        self.base  = Path(__file__).resolve().parent.parent.parent
        logger.info("RAGTestGenerator initialized")

    def build_knowledge_base(self) -> int:
        """Build KB from your framework — call once at start."""
        count = self.kb.build_from_framework()
        self.kb.save()
        return count

    def generate_smart_tests(self, description: str) -> dict:
        """
        Generate context-aware tests using RAG + Ollama.

        Returns:
            {
                "test_cases":   [...],
                "gherkin":      "Feature: ...",
                "entities":     {...},
                "locators":     [...],
                "coverage_gap": {...}
            }
        """
        logger.info(f"Generating smart tests for: {description}")

        # Step 1: Get relevant context from knowledge base
        context = self.kb.get_context_for_ai(description)
        logger.debug(f"Context retrieved: {len(context)} chars")

        # Step 2: Extract entities using NLP
        entities = self.nlp.extract_test_entities(description)

        # Step 3: Generate test cases with context
        test_cases = self._generate_with_context(
            description, context
        )

        # Step 4: Generate Gherkin feature
        gherkin = self.nlp.requirement_to_gherkin(description)

        # Step 5: Suggest locators
        page = entities.get("page", "")
        elements = entities.get("elements", [description])
        locators = []
        for element in elements[:2]:
            locs = self.nlp.generate_locator_suggestions(element)
            locators.extend(locs)

        result = {
            "description": description,
            "test_cases":  test_cases,
            "gherkin":     gherkin,
            "entities":    entities,
            "locators":    locators[:5],
            "context_used": len(context) > 50
        }

        logger.success(
            f"Generated {len(test_cases)} smart tests "
            f"with RAG context"
        )
        return result

    def _generate_with_context(self, description: str,
                                context: str) -> list:
        """Generate test cases with RAG context injected."""
        if not config.OLLAMA_ENABLED:
            return self._template_tests(description)

        import ollama

        prompt = f"""You are a QA expert. Generate test cases using this context:

EXISTING FRAMEWORK CONTEXT:
{context[:1500]}

GENERATE TESTS FOR: {description}

Return ONLY a JSON array:
[
  {{
    "test_id": "TC001",
    "title": "descriptive test title",
    "type": "positive",
    "priority": "high",
    "precondition": "what must be true before test",
    "steps": ["step 1", "step 2", "step 3"],
    "expected": "expected result",
    "gherkin": "Given...When...Then..."
  }}
]

Generate 5 tests. Use context to make tests relevant. JSON only."""

        try:
            response = ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            raw   = response["message"]["content"].strip()
            start = raw.find("[")
            end   = raw.rfind("]") + 1
            if start != -1 and end > start:
                raw = raw[start:end]
            cases = json.loads(raw)
            return cases
        except Exception as e:
            logger.error(f"RAG generation failed: {e}")
            return self._template_tests(description)

    def save_gherkin_feature(self, gherkin: str,
                              filename: str = None) -> str:
        """Save generated Gherkin to a .feature file."""
        name = filename or "ai_generated"
        path = self.base / "features" / f"{name}.feature"
        with open(path, "w") as f:
            f.write(gherkin)
        logger.success(f"Feature saved: {path}")
        return str(path)

    def print_results(self, result: dict):
        """Print generated results in readable format."""
        print(f"\n{'='*65}")
        print(f"RAG + AI Test Generation Results")
        print(f"{'='*65}")
        print(f"Feature: {result['description']}")
        print(f"Context used: {result['context_used']}")
        print(f"{'='*65}")

        print(f"\nTest Cases ({len(result['test_cases'])}):")
        for tc in result["test_cases"]:
            print(f"\n  [{tc.get('test_id','?')}] {tc.get('title','?')}")
            print(f"    Type:     {tc.get('type','?')}")
            print(f"    Priority: {tc.get('priority','?')}")
            print(f"    Expected: {tc.get('expected','?')[:50]}")

        print(f"\nExtracted Entities:")
        for k, v in result["entities"].items():
            print(f"  {k}: {v}")

        print(f"\nLocator Suggestions:")
        for loc in result["locators"][:3]:
            print(f"  {loc}")

        print(f"\nGherkin Preview:")
        gherkin_lines = result["gherkin"].split("\n")[:8]
        for line in gherkin_lines:
            print(f"  {line}")
        print(f"{'='*65}\n")

    def _template_tests(self, description: str) -> list:
        return [
            {
                "test_id":      "TC001",
                "title":        f"Verify {description} - happy path",
                "type":         "positive",
                "priority":     "high",
                "precondition": "App is open",
                "steps":        ["Open app", "Perform action", "Verify"],
                "expected":     "Success",
                "gherkin":      f"Given app open\nWhen I do {description}\nThen success"
            }
        ]