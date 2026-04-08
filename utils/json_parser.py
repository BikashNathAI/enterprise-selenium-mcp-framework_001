import json
import re

def parse_ollama_output(raw_text):
    try:
        raw_text = raw_text.strip()

        # ✅ CASE 1: Proper JSON array
        array_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if array_match:
            return json.loads(array_match.group(0))

        # ✅ CASE 2: Single JSON object → wrap into array
        object_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if object_match:
            obj = json.loads(object_match.group(0))
            return [obj]

        # ❌ Nothing found
        raise ValueError("No valid JSON found")

    except Exception as e:
        print("\n❌ JSON Parse Error:", e)
        print("\n🔴 RAW OUTPUT:\n", raw_text)
        return None