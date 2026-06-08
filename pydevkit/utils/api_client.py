
import time
from os import environ
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def _is_rate_limit_error(exc: Exception) -> bool:
    """Return True when an exception appears to be a rate limit failure."""
    try:
        status_code: Optional[int] = getattr(exc, "status_code", None)
        message = str(exc).lower()
        return status_code == 429 or "rate limit" in message or "rate_limit" in message
    except AttributeError:
        return False


def call_groq(
    prompt: str,
    system: str,
    model: str = "llama-3.1-8b-instant",
    max_tokens: int = 2048,
) -> str:
    """Call Groq chat completions and return the response text."""
    try:
        api_key = environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is missing. Set GROQ_API_KEY in your environment or .env file.")

        client = Groq(api_key=api_key)
        last_error: Exception | None = None

        for attempt in range(3):
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
                if _is_rate_limit_error(exc) and attempt < 2:
                    time.sleep(2)
                    continue
                raise

        if last_error is not None:
            raise last_error
        return ""
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Groq API request failed: {exc}") from exc
