"""Prompt builders for the Gemini-based context interpreter."""

from typing import Any
from collections.abc import Sequence


CONTEXT_INTERPRETER_SYSTEM_PROMPT = """
Voce atua em uma assessoria financeira e precisa interpretar texto livre de clientes.
Seu trabalho e extrair sinais de contexto de forma conservadora, objetiva e util para negocio.

Regras obrigatorias:
- Responda somente com JSON valido.
- Nunca inclua markdown, comentarios, cercas de codigo ou texto fora do JSON.
- Use portugues no campo short_summary.
- Seja conservador: so marque life_event_detected como true quando houver indicio razoavel.
- financial_insecurity_detected deve ser true apenas quando houver medo, inseguranca, perda de renda,
  necessidade de liquidez, dificuldade financeira ou preocupacao forte com mercado.
- detected_sentiment deve ser exatamente um destes valores: positive, neutral, negative.
- short_summary deve ter no maximo 280 caracteres.
""".strip()

CONTEXT_INTERPRETATION_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "detected_sentiment": {
            "type": "string",
            "enum": ["positive", "neutral", "negative"],
            "description": "Sentimento geral identificado no contexto textual.",
        },
        "life_event_detected": {
            "type": "boolean",
            "description": "Indica se ha sinal razoavel de evento de vida relevante.",
        },
        "life_event_confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Confianca do sinal de evento de vida.",
        },
        "financial_insecurity_detected": {
            "type": "boolean",
            "description": "Indica medo financeiro, inseguranca ou necessidade de liquidez.",
        },
        "short_summary": {
            "type": "string",
            "minLength": 10,
            "maxLength": 280,
            "description": "Resumo curto em portugues.",
        },
    },
    "required": [
        "detected_sentiment",
        "life_event_detected",
        "life_event_confidence",
        "financial_insecurity_detected",
        "short_summary",
    ],
}


def build_context_interpreter_prompt(
    *,
    client_notes: str | None,
    latest_interactions: Sequence[str],
) -> str:
    """Build the user prompt that summarizes the available client text."""
    notes_block = client_notes.strip() if client_notes else "Sem notas adicionais."

    if latest_interactions:
        interactions_block = "\n".join(
            f"{index}. {interaction.strip()}"
            for index, interaction in enumerate(latest_interactions, start=1)
            if interaction.strip()
        )
    else:
        interactions_block = "Nenhuma interacao textual recente."

    return f"""
Analise o contexto abaixo e retorne apenas o JSON solicitado.

Campos esperados:
- detected_sentiment: positive | neutral | negative
- life_event_detected: boolean
- life_event_confidence: numero entre 0 e 1
- financial_insecurity_detected: boolean
- short_summary: string curta em portugues

Notas do cliente:
{notes_block}

Ultimas interacoes textuais:
{interactions_block}
""".strip()
