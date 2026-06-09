import random
import time
from os import environ
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
RETRYABLE_ERROR_TEXT = (
    "connection reset",
    "connection refused",
    "rate limit",
    "rate_limit",
    "temporarily unavailable",
    "timeout",
    "timed out",
    "too many requests",
)
OFFLINE_FALLBACK_ERROR_TEXT = RETRYABLE_ERROR_TEXT + (
    "groq_api_key is missing",
    "request too large",
    "tokens per minute",
)


def _is_retryable_error(exc: Exception) -> bool:
    """Return True when an exception appears safe to retry."""
    try:
        status_code: Optional[int] = getattr(exc, "status_code", None)
        message = str(exc).lower()
        return status_code in RETRYABLE_STATUS_CODES or any(text in message for text in RETRYABLE_ERROR_TEXT)
    except AttributeError:
        return False


def _retry_delay(attempt: int, base_delay: float = 1.0) -> float:
    """Return an exponential retry delay with small jitter."""
    try:
        return min(base_delay * (2 ** attempt), 8.0) + random.uniform(0, 0.25)
    except (OverflowError, ValueError):
        return base_delay


def is_offline_fallback_error(exc: Exception) -> bool:
    """Return True when callers should use deterministic offline generation."""
    try:
        message = str(exc).lower()
        return any(text in message for text in OFFLINE_FALLBACK_ERROR_TEXT)
    except AttributeError:
        return False


def call_groq(
    prompt: str,
    system: str,
    model: str = "llama-3.1-8b-instant",
    max_tokens: int = 2048,
    retry_attempts: int = 3,
) -> str:
    """Call Groq chat completions and return the response text."""
    try:
        api_key = environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is missing. Set GROQ_API_KEY in your environment or .env file.")

        client = Groq(api_key=api_key)
        last_error: Exception | None = None

        for attempt in range(max(1, retry_attempts)):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=max_tokens,
                )
                content = response.choices[0].message.content
                return content or ""
            except Exception as exc:
                last_error = exc
                if _is_retryable_error(exc) and attempt < max(1, retry_attempts) - 1:
                    time.sleep(_retry_delay(attempt))
                    continue
                raise

        if last_error is not None:
            raise last_error
        return ""
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Groq API request failed: {exc}") from exc
