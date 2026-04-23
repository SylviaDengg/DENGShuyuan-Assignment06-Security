# Mini-Assignment 6 Guidelines: Security & Ethics Integration

## 1. What this assignment is really asking for

This assignment is **not** asking for a full product UI. It is asking for a **security layer wrapped around an AI agent workflow**.

Your code should show that every request goes through this order:

1. **Input validation**
2. **Rate limiting**
3. **Ethical guardrails**
4. **Model execution**
5. **Optional output check / final response packaging**

That order matters because the assignment explicitly says the security components must be integrated into a **callable workflow** and exercised **before/after model execution**.

## 2. Best scoring strategy

To score well, optimize for the rubric instead of overbuilding.

### Highest-value choices
- Use a **simple Python script workflow**, not Streamlit.
- Implement **three clean classes** in `security.py`:
  - `InputValidator`
  - `RateLimiter`
  - `EthicalGuard`
- Add one **integration function** such as `secure_process_request(...)`.
- Use `demo.py` to show several cases clearly:
  - valid request
  - invalid input
  - rate-limited user
  - harmful request blocked
  - optional safe request that reaches the model
- Use `test_security.py` to prove each class works.
- Write a README with a **clear threat model** and **limitations**.

### Avoid these mistakes
- Building a big UI that the assignment does not require.
- Writing classes but **not integrating them into one workflow**.
- Only checking input length and calling it “validation”.
- Blocking harmful input without **logging flagged content for review**.
- Forgetting that `prompt-log.md` must contain the **full AI chat history**, not a short summary.
- Committing API keys.

## 3. Recommended file structure

```text
mini-assignment-06/
├── .env
├── .gitignore
├── requirements.txt
├── security.py
├── demo.py
├── test_security.py
├── README.md
└── prompt-log.md
```

### Suggested `requirements.txt`
```txt
openai
python-dotenv
```

If you want tests via `pytest`, add:
```txt
pytest
```

## 4. Recommended implementation design

## `security.py`
Keep this file compact and readable. A good design is:

### A. `InputValidator`
Responsible for:
- max length check
- empty input check
- basic format check
- sanitization
- helpful error messages

### Suggested validation rules
- Reject empty or whitespace-only input.
- Reject input above a max length, e.g. `1000`.
- Reject obviously broken format, such as too few alphanumeric characters.
- Sanitize by:
  - removing null bytes and control characters
  - normalizing repeated whitespace
  - stripping surrounding whitespace
  - optionally escaping or removing raw HTML tags

### Suggested methods
```python
sanitize(text: str) -> str
validate(text: str) -> tuple[bool, str, str]
```

Where the tuple can mean:
- `passed`
- `message`
- `sanitized_text`

That makes later integration easier.

---

### B. `RateLimiter`
Responsible for:
- tracking requests by `user_id` or `session_id`
- allowing up to a fixed number in a time window
- rejecting extra requests with a helpful message
- resetting automatically when old timestamps expire

### Recommended design
Use a dictionary like:
```python
{
    "user_1": [timestamp1, timestamp2, ...]
}
```

### Suggested methods
```python
allow_request(user_id: str) -> tuple[bool, str]
```

### Good defaults
- `max_requests = 10`
- `window_seconds = 60`

For testing, use smaller values like 2 requests per 3 seconds.

---

### C. `EthicalGuard`
Responsible for:
- checking for harmful or inappropriate request patterns
- blocking disallowed content
- logging flagged requests for review
- returning appropriate user feedback

### Keep it simple
You do **not** need a perfect moderation engine. A pattern-based filter is enough if it is structured and documented.

### Suggested categories
Use keyword/regex lists for categories such as:
- violence / harm
- hate / harassment
- illegal hacking / malware / credential theft
- explicit self-harm encouragement
- prompt injection attempts, e.g. “ignore previous instructions”, “reveal system prompt”

### Suggested methods
```python
check(text: str, user_id: str = "anonymous") -> tuple[bool, str]
```

### Logging flagged content
Since the project preference is beginner-friendly and avoids logging libraries, use a simple helper that appends JSON lines to a file like:
- `flagged_content.log`
- or `flagged_content.jsonl`

Each flagged record can contain:
- timestamp
- user_id
- category
- original text
- reason

## 5. The integration piece that will matter most

This is the part that will likely separate average work from strong work.

Your workflow should include a **single callable function** such as:

```python
secure_process_request(user_id: str, input_text: str, model_callable) -> dict
```

### Recommended flow

```text
receive request
→ validate and sanitize
→ check rate limit
→ check ethical guardrails
→ call model if safe
→ optionally inspect output
→ return structured response
```

### Example response format
```python
{
    "ok": True,
    "stage": "completed",
    "message": "Request processed successfully.",
    "sanitized_input": "...",
    "output": "..."
}
```

### On failure
Return structured errors such as:
```python
{
    "ok": False,
    "stage": "ethical_guard",
    "message": "Request blocked due to unsafe content."
}
```

That makes the workflow easier to demo and easier to test.

## 6. Should you use the real DeepSeek model?

Use this practical approach:

### Best option
- In `demo.py`, try to load `.env` and call DeepSeek if credentials exist.
- If credentials are missing, fall back to a **mock model function**.

That gives you:
- a real AI workflow when available
- a runnable demo even without API access
- clean tests without hitting the real API

### Mock model example
```python
def mock_model(prompt: str) -> str:
    return f"Mock response for: {prompt[:80]}"
```

## 7. Recommended `demo.py`

The demo should prove behavior, not just run once.

### Suggested scenarios
1. **Valid request** → passes all checks and reaches model.
2. **Too long input** → blocked by validator.
3. **Whitespace or malformed input** → blocked by validator.
4. **Repeated requests from same user** → blocked by rate limiter.
5. **Harmful request** → blocked by ethical guard and logged.
6. **Prompt injection attempt** → blocked or flagged.

### Demo style
Keep it simple:
- print case title
- print input
- print returned dictionary

That is enough for demonstration.

## 8. Recommended `test_security.py`

At minimum, test these behaviors.

### InputValidator tests
- rejects empty input
- rejects over-length input
- sanitizes control characters / extra whitespace
- accepts a normal valid input

### RateLimiter tests
- allows requests under limit
- blocks request when limit exceeded
- resets after window passes

### EthicalGuard tests
- allows benign request
- blocks harmful request
- blocks prompt injection phrase
- writes a flagged log entry

### Integration tests
- a safe request reaches the model callable
- blocked input never reaches the model callable
- blocked ethical request never reaches the model callable

## 9. README outline

Your README should be practical and rubric-oriented.

## Title
`Mini-Assignment 6: Security & Ethics Integration`

## A. System overview
Briefly explain:
- the problem
- the workflow
- the key components

## B. Threat model
List realistic threats such as:
- oversized inputs
- malformed input
- prompt injection attempts
- abusive repeated requests
- harmful content requests
- accidental credential leakage

## C. Security measures implemented
Explain:
- input validation
- sanitization
- rate limiting
- ethical guardrails
- flagged-content logging
- optional output filtering

## D. How to run
Include:
- install dependencies
- set up `.env`
- run `demo.py`
- run tests

## E. Limitations
Be explicit:
- keyword-based guardrails can miss nuanced harmful content
- in-memory rate limiting does not persist across server restarts
- not suitable for distributed production use without shared storage
- no full authentication system
- no advanced moderation API

## F. Future improvements
Examples:
- persistent store like Redis for rate limiting
- stronger moderation model
- role-based access control
- output moderation
- audit dashboard

## 10. Threat model you can directly use

### Threat 1: Oversized or malformed input
Risk:
- crashes or unstable behavior
- poor model responses

Mitigation:
- length limits
- empty/format checks
- sanitization

### Threat 2: Request spam / abuse
Risk:
- excessive API cost
- degraded performance
- denial of service against the demo system

Mitigation:
- per-user rate limiting with time window

### Threat 3: Harmful or inappropriate prompts
Risk:
- unsafe outputs
- unethical usage
- reputational issues

Mitigation:
- ethical content filter
- blocking + user feedback + logging

### Threat 4: Prompt injection attempts
Risk:
- attempts to override instructions or reveal hidden configuration

Mitigation:
- pattern detection for common injection phrases
- deny or flag suspicious requests

### Threat 5: Credential leakage
Risk:
- exposed API key in repository or prompt logs

Mitigation:
- `.env`
- `.gitignore`
- no secrets in prompt log or code

## 11. Practical design choices I would recommend

### Choice 1: In-memory rate limiter
Good for:
- this assignment
- short demo
- beginner-friendly code

Not good for:
- multi-process or production deployment

### Choice 2: Pattern-based ethical filter
Good for:
- demonstrating guardrails clearly
- simple tests
- easy explanation

Not good for:
- nuanced moderation at scale

### Choice 3: Structured dictionaries for workflow output
Good for:
- clean demo output
- easy testing
- explicit failure stage

## 12. Submission checklist

Before submitting, verify all of these:

- `security.py` contains the three required classes.
- security checks are integrated into a callable workflow.
- `demo.py` demonstrates pass/fail cases clearly.
- `test_security.py` covers validation, rate limiting, ethical filtering, and integration.
- `README.md` includes system overview, threat model, measures, usage, and limitations.
- `prompt-log.md` contains full AI interaction history.
- `.env` is ignored in `.gitignore`.
- no API key appears in repository files or prompt logs.
- code is simple enough that you can explain every function.

## 13. Recommended final positioning

If you want the project to feel strong but still realistic, frame it like this:

> This assignment implements a lightweight security gateway for an AI agent workflow. Every request is validated, rate-limited, and screened for harmful or manipulative content before model execution. Unsafe requests are blocked early, flagged events are recorded for review, and safe requests continue through a controlled workflow.

That wording matches the assignment closely and makes the integration logic very clear.
