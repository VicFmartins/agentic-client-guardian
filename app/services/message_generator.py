"""Generate personalized advisor messages with Gemini and safe fallback."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.churn_analysis import ChurnAnalysis
from app.models.client import Client
from app.models.interaction import Interaction
from app.prompts.message_generator_prompt import (
    MESSAGE_GENERATOR_SYSTEM_PROMPT,
    build_message_generator_prompt,
)
from app.schemas.context_interpretation import ContextInterpretation, InterpretationSource
from app.services.gemini_client import (
    GeminiClient,
    GeminiClientConfigError,
    GeminiGenerationError,
)


@dataclass(frozen=True)
class GeneratedMessageResult:
    """Result of personalized-message generation."""

    message: str
    source: InterpretationSource
    used_ai: bool
    used_fallback: bool
    warning: str | None = None


class MessageGenerator:
    """Generate short and consultive client-facing messages."""

    def __init__(self, gemini_client: GeminiClient | None = None) -> None:
        self._gemini_client = gemini_client

    def generate(
        self,
        *,
        client: Client,
        analysis: ChurnAnalysis,
        context_interpretation: ContextInterpretation,
        interactions: list[Interaction],
    ) -> GeneratedMessageResult:
        """Generate a personalized message, falling back locally on failure."""
        prompt = build_message_generator_prompt(
            client=client,
            analysis=analysis,
            context_interpretation=context_interpretation,
            interactions=interactions,
        )

        try:
            raw_message = self._get_gemini_client().generate_text(
                prompt=prompt,
                system_prompt=MESSAGE_GENERATOR_SYSTEM_PROMPT,
                temperature=0.35,
            )
            return GeneratedMessageResult(
                message=_sanitize_message(raw_message),
                source=InterpretationSource.AI,
                used_ai=True,
                used_fallback=False,
            )
        except (GeminiClientConfigError, GeminiGenerationError, ValueError) as exc:
            return GeneratedMessageResult(
                message=self._fallback_message(
                    client=client,
                    analysis=analysis,
                    context_interpretation=context_interpretation,
                ),
                source=InterpretationSource.FALLBACK,
                used_ai=False,
                used_fallback=True,
                warning=str(exc),
            )

    def _get_gemini_client(self) -> GeminiClient:
        """Lazily create the Gemini client to preserve graceful fallback."""
        if self._gemini_client is None:
            self._gemini_client = GeminiClient()

        return self._gemini_client

    @staticmethod
    def _fallback_message(
        *,
        client: Client,
        analysis: ChurnAnalysis,
        context_interpretation: ContextInterpretation,
    ) -> str:
        """Create a safe local fallback message."""
        opening = f"Oi {client.name}, tudo bem?"
        bridge = "Queria compartilhar uma recomendacao objetiva e seguir ao seu lado neste momento."

        if context_interpretation.life_event_detected:
            context_line = (
                "Considerando o momento recente que voce sinalizou, faz sentido revisarmos seus proximos passos com calma."
            )
        elif context_interpretation.financial_insecurity_detected:
            context_line = (
                "Percebi um contexto mais cauteloso recentemente, entao vale uma conversa breve para alinharmos prioridades."
            )
        elif analysis.suggested_action == "revisar carteira":
            context_line = (
                "Preparei uma revisao objetiva da sua carteira para avaliarmos o que faz mais sentido agora."
            )
        elif analysis.suggested_action == "ligar hoje":
            context_line = (
                "Gostaria de falar com voce ainda hoje para alinharmos os proximos passos com tranquilidade."
            )
        elif analysis.suggested_action == "fazer follow-up leve":
            context_line = "Queria fazer um acompanhamento rapido e manter nosso alinhamento em dia."
        else:
            context_line = "Separei um ponto breve para conversarmos de forma consultiva e pragmatica."

        closing = _closing_by_channel(analysis)
        return _sanitize_message(f"{opening} {bridge} {context_line} {closing}")


def _sanitize_message(message: str) -> str:
    """Normalize plain text and reject unusable outputs."""
    cleaned = " ".join(message.replace("\n", " ").replace("\r", " ").split()).strip()
    cleaned = cleaned.strip("`").strip()

    if not cleaned:
        raise ValueError("Mensagem vazia retornada pelo gerador.")

    if len(cleaned) < 20:
        raise ValueError("Mensagem muito curta para uso consultivo.")

    return cleaned[:600]


def _closing_by_channel(analysis: ChurnAnalysis) -> str:
    """Tailor the closing line to the suggested channel."""
    if analysis.suggested_channel.value == "phone":
        return "Se fizer sentido para voce, posso te ligar e conduzimos isso de forma bem objetiva."
    if analysis.suggested_channel.value == "whatsapp":
        return "Se preferir, seguimos por aqui e eu te envio isso de maneira bem objetiva."
    return "Se preferir, eu organizo isso por escrito e te envio de forma objetiva."
