"""
LLM Self-Improvement Agent
Читает utils.py и тесты, просит Claude/GPT улучшить код,
записывает результат обратно — только если тесты проходят.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from openai import OpenAI

# ── настройки ────────────────────────────────────────────────────
TARGET_FILE  = "utils.py"
TESTS_DIR    = "tests/"
MODEL        = "gpt-4o-mini"        # дёшево и достаточно умно
MAX_TOKENS   = 2048
# ────────────────────────────────────────────────────────────────


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def run_tests() -> tuple[bool, str]:
    """Запускает pytest и возвращает (success, output)."""
    result = subprocess.run(
        ["pytest", TESTS_DIR, "-v", "--tb=short", "--no-header"],
        capture_output=True,
        text=True,
    )
    passed = result.returncode == 0
    return passed, result.stdout + result.stderr


def ask_llm(current_code: str, current_tests: str) -> str:
    """Отправляет код в LLM и получает улучшенную версию."""
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    prompt = f"""You are a senior Python developer doing a code review and improvement pass.

Here is the CURRENT utils.py:
```python
{current_code}
```

Here are the EXISTING tests (DO NOT break them):
```python
{current_tests}
```

Your task — improve utils.py by doing ONE OR MORE of the following:
1. Add proper type hints to all functions
2. Add or improve docstrings (Google style)
3. Improve an existing function's implementation (edge cases, efficiency)
4. Add ONE new small utility function that fits the module's theme
   (and add its tests to tests/test_utils.py as well — IMPORTANT: also update the import line at the top of test_utils.py to include the new function name)

Rules:
- Return ONLY valid Python code, no markdown fences, no explanations
- All existing tests MUST still pass
- Keep the file clean and production-quality
- If you add a new function, end your response with the separator line:
  ### NEW_TEST ###
  and then the pytest code for the new function (plain Python, no fences)

Respond now with the improved utils.py content:
"""

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=0.6,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def parse_response(raw: str) -> tuple[str, str | None]:
    """Разбивает ответ LLM на (utils_code, new_test_code | None)."""
    separator = "### NEW_TEST ###"
    if separator in raw:
        parts = raw.split(separator, 1)
        return parts[0].strip(), parts[1].strip()
    return raw.strip(), None


def validate_python(code: str, label: str) -> bool:
    """Проверяет синтаксис через compile()."""
    try:
        compile(code, label, "exec")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {label}: {e}")
        return False


def main() -> None:
    print("🤖 Self-Improvement Agent starting...")
    
    # 1. Читаем текущее состояние
    current_utils = read_file(TARGET_FILE)
    current_tests = read_file(f"{TESTS_DIR}test_utils.py")

    # 2. Спрашиваем LLM
    print(f"📡 Calling {MODEL}...")
    raw_response = ask_llm(current_utils, current_tests)
    new_utils, new_test_snippet = parse_response(raw_response)

    # 3. Проверяем синтаксис
    if not validate_python(new_utils, "utils.py"):
        print("⚠️  LLM returned invalid Python for utils.py — skipping.")
        sys.exit(0)

    # 4. Сохраняем во временные файлы, запускаем тесты
    backup_utils = current_utils
    backup_tests = current_tests

    try:
        write_file(TARGET_FILE, new_utils)

        # Если LLM добавил новый тест — дописываем в файл
        if new_test_snippet:
            if validate_python(new_test_snippet, "new_test"):
                updated_tests = current_tests + "\n\n" + new_test_snippet
                write_file(f"{TESTS_DIR}test_utils.py", updated_tests)
            else:
                print("⚠️  New test code is invalid syntax — ignoring new test only.")

        passed, output = run_tests()
        print(output)

        if passed:
            print("✅ All tests pass — improvement committed!")
            # Покажем diff
            subprocess.run(["git", "diff", TARGET_FILE])
        else:
            print("❌ Tests failed — reverting to original code.")
            write_file(TARGET_FILE, backup_utils)
            write_file(f"{TESTS_DIR}test_utils.py", backup_tests)
            sys.exit(0)   # не падаем — просто не коммитим

    except Exception as exc:
        print(f"💥 Unexpected error: {exc} — reverting.")
        write_file(TARGET_FILE, backup_utils)
        write_file(f"{TESTS_DIR}test_utils.py", backup_tests)
        raise


if __name__ == "__main__":
    main()