"""Gemini API client used by EduGenie.

The client is deliberately defensive because temporary Gemini 503/429 responses
should not crash the FastAPI application or produce a non-JSON response for the UI.
"""

import os
import time
from functools import lru_cache
from typing import Any, Iterable

from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - allows tests without Google SDK installed
    genai = None
    types = None

load_dotenv()

DEFAULT_MODEL = "gemini-3.5-flash"
DEFAULT_FALLBACK_MODELS = ("gemini-3.5-flash-lite", "gemini-3.8-flash")


def _api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()


def _configured_models() -> list[str]:
    primary = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    fallback_text = os.getenv("GEMINI_FALLBACK_MODELS", "")
    configured_fallbacks = [m.strip() for m in fallback_text.split(",") if m.strip()]

    models: list[str] = []
    for model in [primary, *configured_fallbacks, *DEFAULT_FALLBACK_MODELS]:
        if model and model not in models:
            models.append(model)
    return models


@lru_cache(maxsize=1)
def get_gemini_client():
    if genai is None:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install -r requirements.txt"
        )

    api_key = _api_key()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Copy .env.example to .env and add your key."
        )

    return genai.Client(api_key=api_key)


def _is_retryable_error(exc: Exception) -> bool:
    """Return True for temporary capacity/service errors."""
    text = str(exc).upper()
    return any(
        marker in text
        for marker in (
            "503",
            "UNAVAILABLE",
            "429",
            "RESOURCE_EXHAUSTED",
            "INTERNAL",
            "DEADLINE_EXCEEDED",
        )
    )


def _request(
    prompt: str,
    *,
    temperature: float,
    max_output_tokens: int,
    response_schema: Any | None = None,
) -> str:
    if types is None:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install -r requirements.txt"
        )

    last_error: Exception | None = None
    client = get_gemini_client()

    for model in _configured_models():
        # Two attempts per model: a quick retry handles short-lived 503 spikes.
        for attempt in range(2):
            try:
                config_kwargs = {
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens,
                }

                if response_schema is not None:
                    config_kwargs.update(
                        {
                            "response_mime_type": "application/json",
                            "response_schema": response_schema,
                        }
                    )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs),
                )

                text = (response.text or "").strip()
                if not text:
                    raise RuntimeError(
                        f"Gemini returned an empty response using model '{model}'."
                    )
                return text

            except Exception as exc:
                last_error = exc

                if not _is_retryable_error(exc):
                    raise RuntimeError(
                        f"Gemini request failed using model '{model}': {exc}"
                    ) from exc

                if attempt == 0:
                    # 2 seconds is enough for most transient service spikes while
                    # keeping the web UI responsive.
                    time.sleep(2)

        # If the primary model is temporarily unavailable, try the next supported
        # fallback model before returning an error to the frontend.
        continue

    raise RuntimeError(
        "Gemini service is temporarily unavailable after retries. "
        "Please try again in a moment. "
        f"Last error: {last_error}"
    ) from last_error


def generate_text(
    prompt: str,
    *,
    temperature: float = 0.3,
    max_output_tokens: int = 2048,
) -> str:
    return _request(
        prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )


def generate_structured(
    prompt: str,
    schema: Any,
    *,
    temperature: float = 0.2,
    max_output_tokens: int = 2048,
) -> str:
    return _request(
        prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_schema=schema,
    )
