import ollama
import json
import os


def parse_ollama_output(raw_text):
    """
    Extract and parse JSON array safely from Ollama output
    """
    try:
        start = raw_text.find("[")
        end = raw_text.rfind("]") + 1

        clean_json = raw_text[start:end]

        return json.loads(clean_json)

    except Exception as e:
        print("\n❌ JSON Parse Error:", e)
        print("\nRaw Output:", raw_text)
        return None


def generate_feature_file(test_cases):
    """
    Convert JSON → Gherkin feature file
    """
    feature_content = "Feature: AI Generated Test Cases\n\n"

    for tc in test_cases:
        feature_content += f"  Scenario: {tc['title']}\n"
        feature_content += f"    {tc['gherkin']}\n\n"

    os.makedirs("features", exist_ok=True)

    with open("features/generated.feature", "w") as f:
        f.write(feature_content)

    print("\n✅ Feature file generated: features/generated.feature")


def main():
    print("🚀 Testing Ollama raw output...\n")

    prompt = """You are a QA expert.

Generate 3 test cases for: User login

STRICT RULES:
- Return ONLY valid JSON array
- No explanation
- No text before or after JSON
- No markdown

Format:
[
  {
    "test_id": "TC001",
    "title": "Valid login test",
    "type": "positive",
    "priority": "high",
    "steps": ["open app", "enter credentials", "click login"],
    "expected": "user logged in",
    "gherkin": "Given app is open When I login Then I see dashboard"
  }
]
"""

    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}]
    )

    raw = response['message']['content']

    print("===== RAW OUTPUT =====")
    print(raw)
    print("=" * 50)

    parsed = parse_ollama_output(raw)

    if parsed:
        print("\n✅ PARSED JSON:")
        for tc in parsed:
            print(tc)

        generate_feature_file(parsed)
    else:
        print("\n❌ Failed to parse JSON. Fix prompt or model output.")


if __name__ == "__main__":
    main()