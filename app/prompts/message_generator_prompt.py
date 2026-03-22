"""Prompt builders for personalized advisor messages."""

from collections.abc import Sequence

from app.models.churn_analysis import ChurnAnalysis
from app.models.client import Client
from app.models.interaction import Interaction
from app.schemas.context_interpretation import ContextInterpretation


MESSAGE_GENERATOR_SYSTEM_PROMPT = """
Voce escreve mensagens curtas para assessores financeiros enviarem a clientes.
Escreva em portugues do Brasil, com tom humano, elegante, consultivo e profissional.

Regras obrigatorias:
- Retorne somente texto simples.
- Nao use markdown, listas, emojis ou aspas extras.
- Nao faca promessas de retorno, ganho ou performance.
- Nao use linguagem invasiva, alarmista ou manipulativa.
- Seja caloroso sem parecer informal demais.
- Mencione contexto apenas de forma sensivel e respeitosa.
- A mensagem deve soar pronta para envio pelo assessor.
- Mantenha a mensagem curta, preferencialmente entre 2 e 4 frases.
""".strip()


def build_message_generator_prompt(
    *,
    client: Client,
    analysis: ChurnAnalysis,
    context_interpretation: ContextInterpretation,
    interactions: Sequence[Interaction],
) -> str:
    """Build the user prompt for generating a personalized advisor message."""
    recent_context = _build_recent_context(interactions)
    client_notes = client.notes or "Sem notas adicionais."

    return f"""
Crie uma mensagem personalizada para o assessor enviar ao cliente.

Dados do cliente:
- Nome: {client.name}
- Perfil de risco: {client.risk_profile.value}
- Segmento: {client.segment}
- Patrimonio simulado: {client.simulated_assets:.2f}

Resultado da analise:
- Churn score: {analysis.churn_score}
- Priority score: {analysis.priority_score}
- Churn level: {analysis.churn_level.value}
- Priority level: {analysis.priority_level.value}
- Motivo principal: {analysis.main_reason}
- Acao sugerida: {analysis.suggested_action}
- Canal sugerido: {analysis.suggested_channel.value}

Interpretacao de contexto:
- Sentimento detectado: {context_interpretation.detected_sentiment.value}
- Evento de vida detectado: {"sim" if context_interpretation.life_event_detected else "nao"}
- Confianca do evento de vida: {context_interpretation.life_event_confidence}
- Inseguranca financeira detectada: {"sim" if context_interpretation.financial_insecurity_detected else "nao"}
- Resumo curto: {context_interpretation.short_summary}

Notas internas:
{client_notes}

Contexto recente:
{recent_context}

Objetivo:
- produzir uma mensagem curta, natural e personalizada
- estimular uma conversa consultiva
- respeitar o canal sugerido e o momento do cliente
- nao soar mecanico nem invasivo
""".strip()


def _build_recent_context(interactions: Sequence[Interaction]) -> str:
    """Summarize recent interactions for the generation prompt."""
    if not interactions:
        return "Nenhuma interacao recente."

    return "\n".join(
        f"- {interaction.channel.value}: {interaction.content}"
        for interaction in interactions[:3]
    )
