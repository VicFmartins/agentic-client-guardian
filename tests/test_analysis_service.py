"""Tests for the end-to-end client analysis service."""

import pytest

from app.db.repositories import build_initial_signals, get_client_by_id, list_interactions_by_client_id
from app.schemas.context_interpretation import (
    ContextInterpretation,
    ContextInterpretationResult,
    DetectedSentiment,
    InterpretationSource,
)
from app.services.analysis_service import AnalysisService, ClientNotFoundError
from app.services.message_generator import GeneratedMessageResult


class FakeAIInterpreter:
    """Deterministic interpreter stub that simulates successful AI usage."""

    def interpret_with_metadata(
        self,
        *,
        client_notes: str | None,
        latest_interactions: list[str],
    ) -> ContextInterpretationResult:
        return ContextInterpretationResult(
            interpretation=ContextInterpretation(
                detected_sentiment=DetectedSentiment.NEGATIVE,
                life_event_detected=True,
                life_event_confidence=0.88,
                financial_insecurity_detected=False,
                short_summary="Cliente menciona filho recente e quer rever o planejamento.",
            ),
            source=InterpretationSource.AI,
            used_ai=True,
            used_fallback=False,
        )


class FakeFallbackInterpreter:
    """Deterministic interpreter stub that simulates fallback mode."""

    def interpret_with_metadata(
        self,
        *,
        client_notes: str | None,
        latest_interactions: list[str],
    ) -> ContextInterpretationResult:
        return ContextInterpretationResult(
            interpretation=ContextInterpretation(
                detected_sentiment=DetectedSentiment.NEGATIVE,
                life_event_detected=False,
                life_event_confidence=0.0,
                financial_insecurity_detected=True,
                short_summary="Cliente demonstra medo do mercado e pede mais liquidez.",
            ),
            source=InterpretationSource.FALLBACK,
            used_ai=False,
            used_fallback=True,
            warning="Gemini indisponivel; usada heuristica local.",
        )


class FakeMessageGenerator:
    """Deterministic message generator used by analysis-service tests."""

    def generate(self, *, client, analysis, context_interpretation, interactions):
        return GeneratedMessageResult(
            message=f"Mensagem teste para {client.name}.",
            source=InterpretationSource.AI,
            used_ai=True,
            used_fallback=False,
        )


def test_analysis_service_runs_full_flow_with_ai_metadata() -> None:
    """The full service should merge AI interpretation into the final result."""
    service = AnalysisService(
        client_loader=get_client_by_id,
        interactions_loader=list_interactions_by_client_id,
        initial_signals_builder=build_initial_signals,
        context_interpreter=FakeAIInterpreter(),
        message_generator=FakeMessageGenerator(),
    )

    result = service.run_full_client_analysis("client-004")

    assert result.used_ai is True
    assert result.used_fallback is False
    assert result.interpretation_source == InterpretationSource.AI
    assert result.consolidated_signals.life_event_detected is True
    assert result.consolidated_signals.life_event_confidence == 0.88
    assert result.churn_analysis.generated_message is not None
    assert result.used_ai is True


def test_analysis_service_continues_when_interpretation_uses_fallback() -> None:
    """Fallback interpretation should still produce a complete churn analysis."""
    service = AnalysisService(
        client_loader=get_client_by_id,
        interactions_loader=list_interactions_by_client_id,
        initial_signals_builder=build_initial_signals,
        context_interpreter=FakeFallbackInterpreter(),
        message_generator=FakeMessageGenerator(),
    )

    result = service.run_full_client_analysis("client-005")

    assert result.used_ai is True
    assert result.used_fallback is True
    assert result.warning is not None
    assert result.consolidated_signals.financial_insecurity_detected is True
    assert result.churn_analysis.client_id == "client-005"


def test_analysis_service_raises_friendly_error_for_missing_client() -> None:
    """Unknown clients should raise a clear domain-specific error."""
    service = AnalysisService(
        client_loader=get_client_by_id,
        interactions_loader=list_interactions_by_client_id,
        initial_signals_builder=build_initial_signals,
        context_interpreter=FakeAIInterpreter(),
        message_generator=FakeMessageGenerator(),
    )

    with pytest.raises(ClientNotFoundError):
        service.run_full_client_analysis("missing-client")
