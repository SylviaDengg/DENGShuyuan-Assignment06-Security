# Security & Ethics Integration Demo

This project adds a lightweight security layer around an AI agent workflow. It checks user input before the model runs, blocks clearly unsafe requests, limits repeated abuse, and returns structured results that are easy to explain in class.

## System Overview

The project has one main workflow function in `security.py`:

`secure_process_request(user_id, input_text, model_callable)`

That function applies security controls in this order:

1. Input validation and sanitization
2. Rate limiting
3. Ethical content filtering
4. Model execution
5. Basic output screening

## Key Components

- `InputValidator`: removes control characters, normalizes whitespace, rejects empty input, rejects over-length input, and performs a simple format check.
- `RateLimiter`: tracks request timestamps per user and blocks users who exceed the allowed number of requests inside the time window.
- `EthicalGuard`: uses simple keyword patterns to block harmful prompts, prompt injection attempts, and other unsafe requests. Flagged content is written to `flagged_content.jsonl`.

## Threat Model

This project focuses on common beginner-level risks in an AI workflow:

- Oversized or malformed input: very long or broken input can waste resources or cause unexpected behavior.
- Spam or abuse: repeated requests from one user can overload a simple system.
- Harmful prompts: a user may ask for violent, illegal, or abusive content.
- Prompt injection attempts: a user may try to bypass instructions with phrases like "ignore previous instructions" or "reveal the system prompt."
- Credential leakage risk: AI workflows should not hardcode secrets or expose API keys in source code.

## Security Measures Implemented

- Input sanitization removes control characters and compresses repeated whitespace.
- Input validation rejects empty input, whitespace-only input, over-length input, and text with no letters or numbers.
- Rate limiting uses an in-memory dictionary of timestamps and automatically resets when the time window expires.
- Ethical filtering blocks simple categories such as violence, harassment, illegal hacking or password theft, self-harm encouragement, and prompt injection phrases.
- Flagged content is recorded with basic JSON lines file output for later review.
- Environment variables are loaded from `.env` with `python-dotenv`.
- The demo can run without a real API key by using a mock model fallback.

## How To Run The Demo

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Optional: create a `.env` file if you want to try DeepSeek through the OpenAI-compatible client:

```env
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

3. Run the demo:

```bash
python3 demo.py
```

If no API key is available, the demo uses a mock model so it still works.

## How To Run Tests

```bash
python3 -m pytest -v
```

The tests do not require a real API key.

## Limitations

- The ethical filter is keyword-based, so it can miss some unsafe content and may also block some safe content.
- The rate limiter is in memory only, so it resets when the program restarts.
- The output screening is basic and uses the same simple pattern approach as the input filter.
- This project is a teaching example, not a production-ready safety system.

## Future Improvements

- Replace keyword matching with a stronger moderation service.
- Store rate limit data in Redis or a database for multi-user deployments.
- Add stronger input rules for HTML, code blocks, and file uploads.
- Add more detailed review tools for flagged content.
- Improve output filtering with risk scoring and category-specific handling.
