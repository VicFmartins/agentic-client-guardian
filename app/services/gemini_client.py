"""Small Gemini REST client used by the MVP services."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx

from app.core.config import get_settings

_logger = logging.getLogger(__name__)


class GeminiClientError(RuntimeError):
    """Base error for Gemini client failures."""


class GeminiClientConfigError(GeminiClientError):
    """Raised when Gemini runtime configuration is missing."""


class GeminiGenerationError(GeminiClientError):
    """Raised when Gemini generation fails or returns an unusable payload."""


class GeminiClient:
    """Minimal wrapper around the Gemini REST API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 20.0,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        http_client: httpx.Client | None = None,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
    ) -> None:
        settings = get_settings()
        resolved_api_key = api_key or settings.gemini_api_key
        resolved_model = model or settings.gemini_model

        if not resolved_api_key:
            raise GeminiClientConfigError(
                "GEMINI_API_KEY nao configurada. Defina a variavel no ambiente ou no arquivo .env."
            )

        self._api_key = resolved_api_key
        self._model = resolved_model
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._http_client = http_client
        self._max_retries = max_retries
        self._retry_base_delay = retry_base_delay

    @property
    def model(self) -> str:
        """Expose the configured Gemini model."""
        return self._model

    def generate_structured_json(
        self,
        *,
        prompt: str,
        system_prompt: str,
        response_json_schema: dict[str, Any],
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """Request structured JSON from Gemini and parse the first candidate."""
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
                "responseJsonSchema": response_json_schema,
            },
        }

        response_data = self._post_generate_content(payload)
        response_text = self._extract_text_candidate(response_data)

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise GeminiGenerationError("Gemini retornou JSON invalido.") from exc

        if not isinstance(parsed, dict):
            raise GeminiGenerationError("Gemini retornou um JSON diferente de objeto.")

        return parsed

    def generate_text(
        self,
        *,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        """Request plain text from Gemini and return the first text candidate."""
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
            },
        }

        response_data = self._post_generate_content(payload)
        return self._extract_text_candidate(response_data)

    def _post_generate_content(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Send a `generateContent` request with exponential-backoff retries."""
        url = f"{self._base_url}/models/{self._model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self._api_key,
        }

        last_exc: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                if self._http_client is not None:
                    response = self._http_client.post(url, headers=headers, json=payload)
                else:
                    with httpx.Client(timeout=self._timeout_seconds) as client:
                        response = client.post(url, headers=headers, json=payload)

                response.raise_for_status()

            except httpx.HTTPStatusError as exc:
                # 429 / 5xx are retryable; 4xx client errors are not
                retryable = exc.response.status_code in {429, 500, 502, 503, 504}
                if not retryable or attempt == self._max_retries:
                    detail = self._extract_error_message(exc.response)
                    raise GeminiGenerationError(
                        f"Falha ao chamar Gemini ({exc.response.status_code}): {detail}"
                    ) from exc
                delay = self._retry_base_delay * (2 ** (attempt - 1))
                _logger.warning(
                    "Gemini retornou %s; tentativa %d/%d em %.1fs.",
                    exc.response.status_code,
                    attempt,
                    self._max_retries,
                    delay,
                )
                time.sleep(delay)
                last_exc = exc
                continue

            except httpx.HTTPError as exc:
                if attempt == self._max_retries:
                    raise GeminiGenerationError("Falha de rede ao chamar Gemini.") from exc
                delay = self._retry_base_delay * (2 ** (attempt - 1))
                _logger.warning(
                    "Erro de rede ao chamar Gemini; tentativa %d/%d em %.1fs: %s",
                    attempt,
                    self._max_retries,
                    delay,
                    exc,
                )
                time.sleep(delay)
                last_exc = exc
                continue

            else:
                break
        else:
            raise GeminiGenerationError("Gemini nao respondeu apos todas as tentativas.") from last_exc

        try:
            data = response.json()
        except ValueError as exc:
            raise GeminiGenerationError("Gemini retornou uma resposta nao JSON.") from exc

        if not isinstance(data, dict):
            raise GeminiGenerationError("Gemini retornou um payload inesperado.")

        return data

    @staticmethod
    def _extract_text_candidate(response_data: dict[str, Any]) -> str:
        """Extract the generated text from the first response candidate."""
        prompt_feedback = response_data.get("promptFeedback")
        if isinstance(prompt_feedback, dict) and prompt_feedback.get("blockReason"):
            raise GeminiGenerationError(
                f"Gemini bloqueou a resposta: {prompt_feedback['blockReason']}"
            )

        candidates = response_data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise GeminiGenerationError("Gemini nao retornou candidates na resposta.")

        first_candidate = candidates[0]
        if not isinstance(first_candidate, dict):
            raise GeminiGenerationError("Gemini retornou um candidate invalido.")

        content = first_candidate.get("content")
        if not isinstance(content, dict):
            raise GeminiGenerationError("Gemini nao retornou content no candidate.")

        parts = content.get("parts")
        if not isinstance(parts, list) or not parts:
            raise GeminiGenerationError("Gemini nao retornou parts no content.")

        text_chunks = [
            part.get("text", "")
            for part in parts
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        ]
        text = "".join(text_chunks).strip()

        if not text:
            raise GeminiGenerationError("Gemini nao retornou texto utilizavel.")

        return text

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        """Try to extract a friendly API error message."""
        try:
            data = response.json()
        except ValueError:
            return response.text.strip() or "erro desconhecido"

        if isinstance(data, dict):
            error = data.get("error")
            if isinstance(error, dict):
                message = error.get("message")
                if isinstance(message, str) and message.strip():
                    return message.strip()

        return "erro desconhecido"
