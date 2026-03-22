"""Tests for Gemini client retry and error handling behavior."""

import httpx
import pytest

from app.services.gemini_client import GeminiClient, GeminiGenerationError


class FakeResponse:
    """Minimal response stub compatible with the Gemini client tests."""

    def __init__(
        self,
        *,
        status_code: int,
        payload: dict | None = None,
        text: str = "",
    ) -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", "https://example.test")
            response = httpx.Response(
                self.status_code,
                request=request,
                json=self._payload or {"error": {"message": self.text or "error"}},
            )
            raise httpx.HTTPStatusError("error", request=request, response=response)

    def json(self) -> dict:
        return self._payload


class FakeHttpClient:
    """HTTP client stub that returns pre-seeded responses in order."""

    def __init__(self, sequence: list[FakeResponse | Exception]) -> None:
        self._sequence = sequence
        self.calls = 0

    def post(self, url: str, headers: dict, json: dict) -> FakeResponse:
        del url, headers, json
        item = self._sequence[self.calls]
        self.calls += 1
        if isinstance(item, Exception):
            raise item
        return item


def _success_payload(text: str) -> dict:
    return {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": text}],
                }
            }
        ]
    }


def test_gemini_client_retries_429_and_then_succeeds() -> None:
    """Retryable rate limiting should eventually succeed when a later response is good."""
    http_client = FakeHttpClient(
        [
            FakeResponse(status_code=429, payload={"error": {"message": "rate limit"}}),
            FakeResponse(status_code=200, payload=_success_payload("hello world")),
        ]
    )
    client = GeminiClient(
        api_key="test-key",
        model="test-model",
        http_client=http_client,
        retry_base_delay=0,
    )

    result = client.generate_text(prompt="hi", system_prompt="sys")

    assert result == "hello world"
    assert http_client.calls == 2


def test_gemini_client_retries_500_and_then_succeeds() -> None:
    """Retryable server failures should also retry before succeeding."""
    http_client = FakeHttpClient(
        [
            FakeResponse(status_code=500, payload={"error": {"message": "server error"}}),
            FakeResponse(status_code=200, payload=_success_payload("ok after retry")),
        ]
    )
    client = GeminiClient(
        api_key="test-key",
        model="test-model",
        http_client=http_client,
        retry_base_delay=0,
    )

    result = client.generate_text(prompt="hi", system_prompt="sys")

    assert result == "ok after retry"
    assert http_client.calls == 2


def test_gemini_client_does_not_retry_authentication_errors() -> None:
    """Authentication failures should fail fast instead of retrying."""
    http_client = FakeHttpClient(
        [
            FakeResponse(status_code=401, payload={"error": {"message": "invalid key"}}),
        ]
    )
    client = GeminiClient(
        api_key="test-key",
        model="test-model",
        http_client=http_client,
        retry_base_delay=0,
    )

    with pytest.raises(GeminiGenerationError):
        client.generate_text(prompt="hi", system_prompt="sys")

    assert http_client.calls == 1
