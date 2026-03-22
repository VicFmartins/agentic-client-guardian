"""Tests for the Gemini-based context interpreter layer."""

from types import SimpleNamespace

import pytest

from app.schemas.context_interpretation import DetectedSentiment
from app.services.context_interpreter import ContextInterpreter
from app.services import gemini_client as gemini_client_module
from app.services.gemini_client import GeminiClient, GeminiClientConfigError


class FakeGeminiClient:
    """Small fake Gemini client for deterministic unit tests."""

    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def generate_structured_json(
        self,
        *,
        prompt: str,
        system_prompt: str,
        response_json_schema: dict[str, object],
        temperature: float = 0.1,
    ) -> dict[str, object]:
        assert prompt
        assert system_prompt
        assert response_json_schema["type"] == "object"
        return self._payload


def test_context_interpreter_returns_valid_gemini_payload() -> None:
    """A valid Gemini payload should be returned as a typed object."""
    interpreter = ContextInterpreter(
        gemini_client=FakeGeminiClient(
            {
                "detected_sentiment": "negative",
                "life_event_detected": True,
                "life_event_confidence": 0.84,
                "financial_insecurity_detected": False,
                "short_summary": "Cliente menciona chegada de filho e quer revisar o planejamento.",
            }
        )
    )

    result = interpreter.interpret(
        client_notes="Cliente comentou nascimento do filho.",
        latest_interactions=["Gostaria de revisar o planejamento financeiro da familia."],
    )

    assert result.detected_sentiment == DetectedSentiment.NEGATIVE
    assert result.life_event_detected is True
    assert result.life_event_confidence == 0.84


def test_context_interpreter_falls_back_on_invalid_gemini_payload() -> None:
    """Invalid model output should trigger the deterministic fallback."""
    interpreter = ContextInterpreter(
        gemini_client=FakeGeminiClient(
            {
                "detected_sentiment": "negative",
                "life_event_detected": False,
                "life_event_confidence": 0.9,
                "financial_insecurity_detected": True,
                "short_summary": "payload inconsistente",
            }
        )
    )

    result = interpreter.interpret(
        client_notes="Cliente esta com medo do mercado e da renda da familia.",
        latest_interactions=["Demonstrou receio com nova queda e pediu mais liquidez."],
    )

    assert result.financial_insecurity_detected is True
    assert result.life_event_detected is False
    assert result.life_event_confidence == 0.0
    assert result.detected_sentiment == DetectedSentiment.NEGATIVE


def test_gemini_client_raises_friendly_error_when_api_key_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing Gemini key should fail with a clear configuration error."""
    monkeypatch.setattr(
        gemini_client_module,
        "get_settings",
        lambda: SimpleNamespace(gemini_api_key=None, gemini_model="gemini-2.5-flash"),
    )

    with pytest.raises(GeminiClientConfigError):
        GeminiClient(api_key=None)
