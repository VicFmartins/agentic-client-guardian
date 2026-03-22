"""Tests for personalized message generation."""

from app.db.repositories import get_client_by_id, list_interactions_by_client_id
from app.models.churn_analysis import ChurnAnalysis
from app.models.enums import Channel, ChurnLevel, PriorityLevel
from app.schemas.context_interpretation import (
    ContextInterpretation,
    DetectedSentiment,
    InterpretationSource,
)
from app.services.message_generator import MessageGenerator


class FakeMessageGeminiClient:
    """Fake Gemini client that returns deterministic plain text."""

    def __init__(self, message: str) -> None:
        self._message = message

    def generate_text(
        self,
        *,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        assert prompt
        assert system_prompt
        return self._message


class BrokenMessageGeminiClient:
    """Fake Gemini client that simulates an invalid short output."""

    def generate_text(
        self,
        *,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        return "ok"


def _sample_analysis() -> ChurnAnalysis:
    return ChurnAnalysis(
        client_id="client-004",
        churn_score=42,
        priority_score=54,
        churn_level=ChurnLevel.MEDIUM,
        priority_level=PriorityLevel.MEDIUM,
        main_reason="Possivel evento de vida pode exigir ajuste no planejamento.",
        suggested_action="enviar mensagem consultiva",
        suggested_channel=Channel.WHATSAPP,
    )


def _sample_interpretation() -> ContextInterpretation:
    return ContextInterpretation(
        detected_sentiment=DetectedSentiment.NEUTRAL,
        life_event_detected=True,
        life_event_confidence=0.84,
        financial_insecurity_detected=False,
        short_summary="Cliente comentou chegada de filho e interesse em revisar planejamento.",
    )


def test_message_generator_uses_gemini_when_valid() -> None:
    """A valid Gemini response should be kept as the final message."""
    generator = MessageGenerator(
        gemini_client=FakeMessageGeminiClient(
            "Oi Diego, preparei uma sugestao objetiva para revisarmos seu planejamento com calma."
        )
    )
    client = get_client_by_id("client-004")
    interactions = list_interactions_by_client_id("client-004")

    assert client is not None

    result = generator.generate(
        client=client,
        analysis=_sample_analysis(),
        context_interpretation=_sample_interpretation(),
        interactions=interactions,
    )

    assert result.source == InterpretationSource.AI
    assert result.used_ai is True
    assert "Diego" in result.message


def test_message_generator_falls_back_when_gemini_output_is_invalid() -> None:
    """Invalid Gemini text should trigger the local fallback."""
    generator = MessageGenerator(gemini_client=BrokenMessageGeminiClient())
    client = get_client_by_id("client-004")
    interactions = list_interactions_by_client_id("client-004")

    assert client is not None

    result = generator.generate(
        client=client,
        analysis=_sample_analysis(),
        context_interpretation=_sample_interpretation(),
        interactions=interactions,
    )

    assert result.source == InterpretationSource.FALLBACK
    assert result.used_fallback is True
    assert "Diego Martins" in result.message
