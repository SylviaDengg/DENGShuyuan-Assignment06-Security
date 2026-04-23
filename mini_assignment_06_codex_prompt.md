# Codex Prompt for Mini-Assignment 6

Use the prompt below directly in Codex.

---

You are editing a beginner-friendly Python project for **IIMT3688 Mini-Assignment 6: Security & Ethics Integration**.

## Goal
Build a lightweight but complete security layer for an AI agent workflow.

The assignment requires:
- input validation and sanitization
- rate limiting
- ethical content filtering
- integration into a callable workflow before/after model execution
- demonstration script
- basic tests
- README documentation

## Deliverables to create or update
Create these files:
- `security.py`
- `demo.py`
- `test_security.py`
- `README.md`
- `prompt-log.md` placeholder structure only if missing
- `.gitignore` if missing
- `requirements.txt` if missing

## Hard constraints
1. Use **only Python scripts**, no notebooks.
2. Keep the code **simple, readable, beginner-friendly**.
3. **Do not use logging libraries**. If logging flagged content is needed, write simple JSON lines to a local file like `flagged_content.jsonl` using basic file I/O.
4. Do not expose or hardcode API keys.
5. Load environment variables from `.env` using `python-dotenv`.
6. `security.py` should stay roughly **100–150 lines** if possible, but correctness is more important than hitting the exact number.
7. Use type hints and short docstrings.
8. Avoid clever abstractions, inheritance-heavy designs, or unnecessary frameworks.
9. Make sure the security components are actually used inside **one callable workflow function**.

## Required design

### 1. `security.py`
Implement these three classes:

#### `InputValidator`
Requirements:
- configurable `max_length`
- reject empty or whitespace-only input
- reject over-length input
- basic input format validation
- sanitize input by removing control characters and normalizing whitespace
- return helpful messages

Suggested API:
- `sanitize(text: str) -> str`
- `validate(text: str) -> tuple[bool, str, str]`
  - returns `(passed, message, sanitized_text)`

#### `RateLimiter`
Requirements:
- track request counts per `user_id` or `session_id`
- enforce limits like 10 requests per minute
- return an appropriate message when limit exceeded
- reset automatically after the time window

Suggested API:
- `allow_request(user_id: str) -> tuple[bool, str]`

Implementation hint:
- use an in-memory dictionary mapping user IDs to timestamp lists

#### `EthicalGuard`
Requirements:
- check for harmful or inappropriate content patterns
- filter unsafe requests
- log flagged content for review
- provide appropriate user feedback

Include simple pattern categories such as:
- violence / harm
- hate / harassment
- illegal hacking / credential theft / malware
- self-harm encouragement
- prompt injection phrases like `ignore previous instructions`, `reveal system prompt`, `system prompt`

Suggested API:
- `check(text: str, user_id: str = "anonymous") -> tuple[bool, str]`

Logging hint:
- append JSON objects to `flagged_content.jsonl`
- each record should include timestamp, user_id, reason/category, and text

### 2. Integration workflow in `security.py`
Add one function that integrates everything, for example:

```python
def secure_process_request(user_id: str, input_text: str, model_callable) -> dict:
    ...
```

Required flow:
1. validate + sanitize input
2. apply rate limit
3. apply ethical guard
4. call model only if safe
5. optionally screen output for a basic unsafe pattern check
6. return a structured dictionary

Example success response:
```python
{
    "ok": True,
    "stage": "completed",
    "message": "Request processed successfully.",
    "sanitized_input": "...",
    "output": "..."
}
```

Example failure response:
```python
{
    "ok": False,
    "stage": "ethical_guard",
    "message": "Request blocked due to unsafe content."
}
```

## 3. `demo.py`
Create a simple demonstration script.

Requirements:
- load `.env`
- try to use DeepSeek via OpenAI-compatible SDK if API credentials exist
- otherwise fall back to a mock model function so the demo still runs
- demonstrate multiple cases clearly

Demo cases to include:
1. safe valid input
2. empty or malformed input
3. over-length input
4. repeated requests that trigger rate limiting
5. harmful request blocked by ethical guard
6. prompt injection request blocked or flagged

Print each case in a clean readable way.

## 4. `test_security.py`
Write basic tests.

Test at least these behaviors:

### InputValidator
- rejects empty input
- rejects too-long input
- sanitizes control characters / extra whitespace
- accepts valid input

### RateLimiter
- allows requests under limit
- blocks when over limit
- resets after time window

### EthicalGuard
- allows benign content
- blocks harmful content
- blocks prompt injection text
- creates a flag log entry

### Integration
- safe input reaches model callable
- blocked input does not reach model callable
- blocked ethical request does not reach model callable

You may use `unittest` or `pytest`, but keep it simple.

## 5. `README.md`
Write a concise but solid README.

It must include:
- short system overview
- workflow / key components
- threat model
- security measures implemented
- how to run the demo
- how to run tests
- limitations
- future improvements

The README should explain the threat model in plain English:
- oversized/malformed input
- spam / abuse
- harmful prompts
- prompt injection attempts
- credential leakage risk

## 6. `.gitignore`
Ensure it ignores at least:
```gitignore
.env
__pycache__/
*.pyc
venv/
flagged_content.jsonl
```

## 7. `requirements.txt`
Ensure it includes at least:
```txt
openai
python-dotenv
pytest
```

If tests use only `unittest`, `pytest` can be omitted.

## 8. Code style expectations
- Keep functions short.
- Add type hints.
- Add short docstrings.
- Prefer explicit `if` logic over compact tricks.
- Avoid advanced patterns.
- Make sure I can explain every part in class.

## 9. Important grading emphasis
Optimize for these priorities:
1. clear validation and sanitization
2. correct request tracking and reset behavior
3. effective ethical filtering and user feedback
4. real integration into one callable workflow
5. reliability in demo and tests
6. documentation quality

## 10. Final self-check before finishing
Before you stop, verify all of this:
- `security.py` has the 3 required classes
- the workflow function uses all 3 classes
- `demo.py` clearly shows pass/fail scenarios
- `test_security.py` runs without needing a real API key
- no secrets are hardcoded
- README explains threats, design, usage, limitations
- code is simple and not overengineered

Now generate the files and fill them with working code.

---
