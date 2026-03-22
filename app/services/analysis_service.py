"""End-to-end analysis service that orchestrates the MVP flow."""

from __future__ import annotations

from collections.abc import Callable

from app.db.repositories import (
    build_initial_signals,
    get_client_by_id,
    list_interactions_by_client_id,
)
from app.models.churn_analysis import ChurnAnalysis
from app.models.client import Client
from app.models.client_signals import ClientSignals
from app.models.full_client_analysis import FullClientAnalysis
from app.models.interaction import Interaction
from app.schemas.context_interpretation import (
    ContextInterpretation,
    ContextInterpretationResult,
    DetectedSentiment,
)
from app.services.context_interpreter import ContextInterpreter
from app.services.message_generator import GeneratedMessageResult, MessageGenerator
from app.services.scoring import analyze_client_signals


class AnalysisServiceError(RuntimeError):
    """Base error for end-to-end analysis failures."""


class ClientNotFoundError(AnalysisServiceError):
    """Raised when the requested client does not exist in the data source."""


class ClientSignalsNotAvailableError(AnalysisServiceError):
    """Raised when initial signals cannot be built for a valid client."""


class AnalysisService:
    """Orchestrates fake data, context interpretation and rule-based scoring."""

    def __init__(
        self,
        *,
        client_loader: Callable[[str], Client | None] = get_client_by_id,
        interactions_loader: Callable[[str], list[Interaction]] = list_interactions_by_client_id,
        initial_signals_builder: Callable[[str], ClientSignals | None] = build_initial_signals,
        context_interpreter: ContextInterpreter | None = None,
        message_generator: MessageGenerator | None = None,
        scoring_function: Callable[[Client, ClientSignals], ChurnAnalysis] = analyze_client_signals,
    ) -> None:
        self._client_loader = client_loader
        self._interactions_loader = interactions_loader
        self._initial_signals_builder = initial_signals_builder
        self._context_interpreter = context_interpreter or ContextInterpreter()
        self._message_generator = message_generator or MessageGenerator()
        self._scoring_function = scoring_function

    def run_full_client_analysis(self, client_id: str) -> FullClientAnalysis:
        """Run the full MVP analysis flow for one client."""
        client = self._get_client_or_raise(client_id)
        interactions = self._interactions_loader(client_id)
        base_signals = self._get_initial_signals_or_raise(client_id)
        interpretation_result = self._interpret_context(client, interactions)
        consolidated_signals = self._consolidate_signals(
            base_signals=base_signals,
            interpretation=interpretation_result.interpretation,
        )
        churn_analysis, message_result = self._score_client(
            client=client,
            interactions=interactions,
            signals=consolidated_signals,
            context_interpretation=interpretation_result.interpretation,
        )

        return FullClientAnalysis(
            client=client,
            interactions=interactions,
            context_interpretation=interpretation_result.interpretation,
            consolidated_signals=consolidated_signals,
            churn_analysis=churn_analysis,
            interpretation_source=interpretation_result.source,
            used_ai=interpretation_result.used_ai or message_result.used_ai,
            used_fallback=interpretation_result.used_fallback or message_result.used_fallback,
            warning=self._merge_warnings(interpretation_result.warning, message_result.warning),
        )

    def _get_client_or_raise(self, client_id: str) -> Client:
        """Load one client or fail with a clear domain error."""
        client = self._client_loader(client_id)
        if client is None:
            raise ClientNotFoundError(f"Cliente '{client_id}' nao encontrado.")

        return client

    def _get_initial_signals_or_raise(self, client_id: str) -> ClientSignals:
        """Load baseline signals or fail with a clear domain error."""
        signals = self._initial_signals_builder(client_id)
        if signals is None:
            raise ClientSignalsNotAvailableError(
                f"Nao foi possivel montar sinais iniciais para o cliente '{client_id}'."
            )

        return signals

    def _interpret_context(
        self,
        client: Client,
        interactions: list[Interaction],
    ) -> ContextInterpretationResult:
        """Interpret the textual context while preserving graceful fallback metadata."""
        interaction_texts = [interaction.content for interaction in interactions[:5]]
        return self._context_interpreter.interpret_with_metadata(
            client_notes=client.notes,
            latest_interactions=interaction_texts,
        )

    def _consolidate_signals(
        self,
        *,
        base_signals: ClientSignals,
        interpretation: ContextInterpretation,
    ) -> ClientSignals:
        """Merge repository signals with Gemini-derived textual signals."""
        life_event_detected = (
            base_signals.life_event_detected or interpretation.life_event_detected
        )
        life_event_confidence = 0.0
        if life_event_detected:
            life_event_confidence = max(
                base_signals.life_event_confidence,
                interpretation.life_event_confidence,
            )

        return base_signals.model_copy(
            update={
                "negative_sentiment_detected": (
                    base_signals.negative_sentiment_detected
                    or interpretation.detected_sentiment == DetectedSentiment.NEGATIVE
                ),
                "life_event_detected": life_event_detected,
                "life_event_confidence": life_event_confidence,
                "financial_insecurity_detected": (
                    base_signals.financial_insecurity_detected
                    or interpretation.financial_insecurity_detected
                ),
            }
        )

    def _score_client(
        self,
        *,
        client: Client,
        interactions: list[Interaction],
        signals: ClientSignals,
        context_interpretation: ContextInterpretation,
    ) -> tuple[ChurnAnalysis, GeneratedMessageResult]:
        """Apply scoring and generate the final personalized message."""
        analysis = self._scoring_function(client, signals)
        message_result = self._message_generator.generate(
            client=client,
            analysis=analysis,
            context_interpretation=context_interpretation,
            interactions=interactions,
        )
        enriched_analysis = analysis.model_copy(
            update={
                "generated_message": message_result.message,
            }
        )
        return enriched_analysis, message_result

    @staticmethod
    def _merge_warnings(*warnings: str | None) -> str | None:
        """Combine non-empty warnings into one readable message."""
        valid_warnings = [warning for warning in warnings if warning]
        if not valid_warnings:
            return None

        return " | ".join(valid_warnings)


_default_analysis_service = AnalysisService()


def run_full_client_analysis(client_id: str) -> FullClientAnalysis:
    """Convenience wrapper for the default service instance."""
    return _default_analysis_service.run_full_client_analysis(client_id)
