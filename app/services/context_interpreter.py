"""Client-context interpreter that uses Gemini with a safe local fallback."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import ValidationError

from app.prompts.context_interpreter_prompt import (
    CONTEXT_INTERPRETATION_RESPONSE_SCHEMA,
    CONTEXT_INTERPRETER_SYSTEM_PROMPT,
    build_context_interpreter_prompt,
)
from app.schemas.context_interpretation import (
    ContextInterpretation,
    ContextInterpretationResult,
    DetectedSentiment,
    InterpretationSource,
)
from app.services.gemini_client import (
    GeminiClient,
    GeminiClientConfigError,
    GeminiGenerationError,
)

_NEGATIVE_KEYWORDS = (
    "preocup",
    "insegur",
    "medo",
    "receio",
    "queda",
    "perda",
    "frustr",
    "volatil",
)
_POSITIVE_KEYWORDS = (
    "obrigad",
    "otimo",
    "tranquilo",
    "confiante",
    "interesse",
    "gostei",
    "feliz",
)
_LIFE_EVENT_KEYWORDS = (
    "filho",
    "bebe",
    "gravidez",
    "casamento",
    "divorcio",
    "aposentadoria",
    "mudanca",
)
_FINANCIAL_INSECURITY_KEYWORDS = (
    "insegur",
    "medo",
    "receio",
    "renda",
    "liquidez",
    "despesas",
    "mercado",
    "volatil",
    "queda",
    "perda",
)


class ContextInterpreter:
    """Interpret client free text and return a typed structured summary."""

    def __init__(self, gemini_client: GeminiClient | None = None) -> None:
        self._gemini_client = gemini_client

    def interpret(
        self,
        *,
        client_notes: str | None,
        latest_interactions: Sequence[str],
    ) -> ContextInterpretation:
        """Return only the structured interpretation payload."""
        return self.interpret_with_metadata(
            client_notes=client_notes,
            latest_interactions=latest_interactions,
        ).interpretation

    def interpret_with_metadata(
        self,
        *,
        client_notes: str | None,
        latest_interactions: Sequence[str],
    ) -> ContextInterpretationResult:
        """
        Interpret client text with Gemini and validate the structured response.

        If Gemini returns invalid or unusable content, the interpreter falls back
        to a deterministic local heuristic so the MVP remains operational.
        """
        prompt = build_context_interpreter_prompt(
            client_notes=client_notes,
            latest_interactions=latest_interactions,
        )

        try:
            raw_output = self._get_gemini_client().generate_structured_json(
                prompt=prompt,
                system_prompt=CONTEXT_INTERPRETER_SYSTEM_PROMPT,
                response_json_schema=CONTEXT_INTERPRETATION_RESPONSE_SCHEMA,
            )
            return ContextInterpretationResult(
                interpretation=ContextInterpretation.model_validate(raw_output),
                source=InterpretationSource.AI,
                used_ai=True,
                used_fallback=False,
            )
        except GeminiClientConfigError as exc:
            return ContextInterpretationResult(
                interpretation=self._fallback_interpretation(
                    client_notes=client_notes,
                    latest_interactions=latest_interactions,
                ),
                source=InterpretationSource.FALLBACK,
                used_ai=False,
                used_fallback=True,
                warning=str(exc),
            )
        except (GeminiGenerationError, ValidationError, ValueError) as exc:
            return ContextInterpretationResult(
                interpretation=self._fallback_interpretation(
                    client_notes=client_notes,
                    latest_interactions=latest_interactions,
                ),
                source=InterpretationSource.FALLBACK,
                used_ai=False,
                used_fallback=True,
                warning=str(exc),
            )

    def _get_gemini_client(self) -> GeminiClient:
        """Create the Gemini client lazily to allow graceful fallback paths."""
        if self._gemini_client is None:
            self._gemini_client = GeminiClient()

        return self._gemini_client

    @staticmethod
    def _fallback_interpretation(
        *,
        client_notes: str | None,
        latest_interactions: Sequence[str],
    ) -> ContextInterpretation:
        """Produce a safe deterministic interpretation without external AI."""
        texts = [client_notes or "", *latest_interactions]
        combined_text = " ".join(texts).lower()

        negative_hits = _keyword_hits(combined_text, _NEGATIVE_KEYWORDS)
        positive_hits = _keyword_hits(combined_text, _POSITIVE_KEYWORDS)
        life_event_hits = _keyword_hits(combined_text, _LIFE_EVENT_KEYWORDS)
        financial_hits = _keyword_hits(combined_text, _FINANCIAL_INSECURITY_KEYWORDS)

        if negative_hits > positive_hits:
            detected_sentiment = DetectedSentiment.NEGATIVE
        elif positive_hits > negative_hits:
            detected_sentiment = DetectedSentiment.POSITIVE
        else:
            detected_sentiment = DetectedSentiment.NEUTRAL

        life_event_detected = life_event_hits > 0
        life_event_confidence = 0.0
        if life_event_detected:
            life_event_confidence = min(0.95, round(0.55 + (life_event_hits * 0.12), 2))

        financial_insecurity_detected = financial_hits > 0

        return ContextInterpretation(
            detected_sentiment=detected_sentiment,
            life_event_detected=life_event_detected,
            life_event_confidence=life_event_confidence,
            financial_insecurity_detected=financial_insecurity_detected,
            short_summary=_build_short_summary(
                detected_sentiment=detected_sentiment,
                life_event_detected=life_event_detected,
                financial_insecurity_detected=financial_insecurity_detected,
                client_notes=client_notes,
                latest_interactions=latest_interactions,
            )
        )


def _keyword_hits(text: str, keywords: tuple[str, ...]) -> int:
    """Count the number of keyword matches in a normalized text."""
    return sum(1 for keyword in keywords if keyword in text)


def _build_short_summary(
    *,
    detected_sentiment: DetectedSentiment,
    life_event_detected: bool,
    financial_insecurity_detected: bool,
    client_notes: str | None,
    latest_interactions: Sequence[str],
) -> str:
    """Build a short Portuguese summary for downstream business logic."""
    parts: list[str] = []

    if life_event_detected:
        parts.append("Cliente menciona possivel evento de vida.")
    if financial_insecurity_detected:
        parts.append("Ha sinais de inseguranca financeira ou receio com mercado.")
    if detected_sentiment == DetectedSentiment.NEGATIVE:
        parts.append("Tom geral das interacoes parece negativo.")
    elif detected_sentiment == DetectedSentiment.POSITIVE:
        parts.append("Tom geral das interacoes parece positivo.")
    else:
        parts.append("Tom geral das interacoes parece neutro.")

    if not parts:
        parts.append("Contexto textual sem sinais fortes no momento.")

    source_text = " ".join(filter(None, [client_notes, *latest_interactions])).strip()
    if source_text:
        excerpt = source_text[:120].strip()
        if excerpt:
            parts.append(f"Resumo base: {excerpt}.")

    summary = " ".join(parts)
    return summary[:280].strip()
