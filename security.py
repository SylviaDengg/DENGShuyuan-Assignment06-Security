"""Simple security checks for a beginner-friendly AI workflow."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ModelCallable = Callable[[str], str]


class InputValidator:
    """Validate and sanitize user input."""

    def __init__(self, max_length: int = 500) -> None:
        self.max_length = max_length

    def sanitize(self, text: str) -> str:
        """Remove control characters and normalize whitespace."""
        cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", text)
        return re.sub(r"\s+", " ", cleaned).strip()

    def validate(self, text: str) -> tuple[bool, str, str]:
        """Return validation status, message, and sanitized text."""
        if not isinstance(text, str):
            return False, "Input must be a text string.", ""

        sanitized = self.sanitize(text)
        if not sanitized:
            return False, "Input cannot be empty or only whitespace.", ""
        if len(sanitized) > self.max_length:
            return False, f"Input is too long. Maximum length is {self.max_length} characters.", sanitized
        if not re.search(r"[A-Za-z0-9]", sanitized):
            return False, "Input must contain at least one letter or number.", sanitized

        return True, "Input is valid.", sanitized


class RateLimiter:
    """Track request counts inside a rolling time window."""

    def __init__(
        self,
        max_requests: int = 10,
        window_seconds: int = 60,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.time_func = time_func or time.time
        self.requests: dict[str, list[float]] = {}

    def allow_request(self, user_id: str) -> tuple[bool, str]:
        """Return whether a request should be allowed."""
        now = self.time_func()
        recent = [
            timestamp
            for timestamp in self.requests.get(user_id, [])
            if now - timestamp < self.window_seconds
        ]
        self.requests[user_id] = recent

        if len(recent) >= self.max_requests:
            wait_seconds = max(1, int(self.window_seconds - (now - recent[0])))
            return False, f"Rate limit exceeded. Try again in about {wait_seconds} seconds."

        recent.append(now)
        self.requests[user_id] = recent
        return True, "Request allowed."


class EthicalGuard:
    """Block unsafe prompts using simple keyword patterns."""

    def __init__(self, log_path: str = "flagged_content.jsonl") -> None:
        self.log_path = Path(log_path)
        self.patterns = {
            "violence_or_harm": [r"\bkill\b", r"\bmurder\b", r"\bbomb\b", r"\bhurt someone\b"],
            "hate_or_harassment": [r"\bharass\b", r"\bbully\b", r"\bdegrade a group\b"],
            "illegal_hacking": [r"\bmalware\b", r"\bphishing\b", r"\bsteal passwords?\b", r"\bkeylogger\b"],
            "self_harm": [r"\bend your life\b", r"\bhow to self-harm\b", r"\bcut yourself\b"],
            "prompt_injection": [
                r"ignore previous instructions",
                r"reveal (the )?system prompt",
                r"\bsystem prompt\b",
            ],
        }

    def _log_flag(self, user_id: str, reason: str, text: str) -> None:
        """Append a flagged event as one JSON line."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "reason": reason,
            "text": text,
        }
        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")

    def check(self, text: str, user_id: str = "anonymous") -> tuple[bool, str]:
        """Return whether text passes the ethical content check."""
        lowered = text.lower()
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, lowered):
                    self._log_flag(user_id, category, text)
                    return False, f"Request blocked due to unsafe content: {category}."
        return True, "Content passed ethical checks."


DEFAULT_VALIDATOR = InputValidator()
DEFAULT_RATE_LIMITER = RateLimiter()
DEFAULT_GUARD = EthicalGuard()


def secure_process_request(
    user_id: str,
    input_text: str,
    model_callable: ModelCallable,
    validator: InputValidator | None = None,
    rate_limiter: RateLimiter | None = None,
    guard: EthicalGuard | None = None,
) -> dict[str, object]:
    """Run input checks, call the model, and return a structured response."""
    validator = validator or DEFAULT_VALIDATOR
    rate_limiter = rate_limiter or DEFAULT_RATE_LIMITER
    guard = guard or DEFAULT_GUARD

    valid, message, sanitized = validator.validate(input_text)
    if not valid:
        return {"ok": False, "stage": "input_validation", "message": message, "sanitized_input": sanitized}

    allowed, message = rate_limiter.allow_request(user_id)
    if not allowed:
        return {"ok": False, "stage": "rate_limiter", "message": message, "sanitized_input": sanitized}

    safe, message = guard.check(sanitized, user_id=user_id)
    if not safe:
        return {"ok": False, "stage": "ethical_guard", "message": message, "sanitized_input": sanitized}

    try:
        output = str(model_callable(sanitized))
    except Exception as exc:
        return {"ok": False, "stage": "model_execution", "message": f"Model call failed: {exc}"}

    output_safe, _ = guard.check(output, user_id=f"{user_id}:output")
    if not output_safe:
        return {
            "ok": False,
            "stage": "output_guard",
            "message": "Model output was blocked because it matched an unsafe pattern.",
            "sanitized_input": sanitized,
        }

    return {
        "ok": True,
        "stage": "completed",
        "message": "Request processed successfully.",
        "sanitized_input": sanitized,
        "output": output,
    }
