"""
LLM Self-Improvement Agent
It reads utils.py and the tests, asks GPT to improve the code,
and writes the result back—only if the tests pass.
"""

import os
import sys
import subprocess
from openai import OpenAI

TARGET_FILE = "utils.py"
TESTS_FILE  = "tests/test_utils.py"
MODEL       = "gpt-4o-mini"
MAX_TOKENS  = 2048


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def run_tests() -> tuple[bool, str]:
    result = subprocess.run(
        ["pytest", "tests/", "-v", "--tb=short", "--no-header"],
        capture_output=True, text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


def ask_llm(current_utils: str, current_tests: str) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    prompt = f"""You are a senior Python developer doing a code review and improvement pass.

CURRENT utils.py:
```python
{current_utils}
```

CURRENT test_utils.py:
```python
{current_tests}
```

Your task: improve utils.py by doing ONE OR MORE of:
1. Add proper type hints to all functions
2. Add or improve docstrings (Google style)
3. Improve an existing function's implementation (edge cases, efficiency)
4. Add ONE new small utility function that fits the module's theme

RESPONSE FORMAT — return both files separated by exactly this line:
### TEST_FILE ###

- First: the complete improved utils.py (no markdown fences, plain Python only)
- Then the separator line
- Then: the COMPLETE updated test_utils.py

CRITICAL rules for test_utils.py:
- Keep ALL existing tests unchanged
- If you added a new function to utils.py — add its test
- The import line MUST import every function that appears in tests
- Example: from utils import add, multiply, validate_email, count_words, reverse_string, new_func

Respond now:
"""

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def parse_response(raw: str) -> tuple[str, str | None]:
    separator = "### TEST_FILE ###"
    if separator in raw:
        parts = raw.split(separator, 1)
        return parts[0].strip(), parts[1].strip()
    return raw.strip(), None


def validate_python(code: str, label: str) -> bool:
    try:
        compile(code, label, "exec")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {label}: {e}")
        return False


def main() -> None:
    print("🤖 Self-Improvement Agent starting...")

    current_utils = read_file(TARGET_FILE)
    current_tests = read_file(TESTS_FILE)

    print(f"📡 Calling {MODEL}...")
    raw = ask_llm(current_utils, current_tests)
    new_utils, new_tests = parse_response(raw)

    if not validate_python(new_utils, "utils.py"):
        print("⚠️  Invalid Python in utils.py — skipping.")
        sys.exit(0)

    if new_tests and not validate_python(new_tests, "test_utils.py"):
        print("⚠️  Invalid Python in test_utils.py — using original tests.")
        new_tests = None

    write_file(TARGET_FILE, new_utils)
    if new_tests:
        write_file(TESTS_FILE, new_tests)

    passed, output = run_tests()
    print(output)

    if passed:
        print("✅ All tests pass — improvement will be committed!")
        subprocess.run(["git", "diff", TARGET_FILE])
    else:
        print("❌ Tests failed — reverting.")
        write_file(TARGET_FILE, current_utils)
        write_file(TESTS_FILE, current_tests)
        sys.exit(0)


if __name__ == "__main__":
    main()