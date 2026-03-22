"""Deterministic scoring engine for the retention MVP."""

from dataclasses import dataclass

from app.models.churn_analysis import ChurnAnalysis
from app.models.client import Client
from app.models.client_signals import ClientSignals
from app.models.enums import Channel, ChurnLevel, PriorityLevel, RiskProfile


@dataclass(frozen=True)
class ScoreComponent:
    """One explicit rule contribution used in the final decision."""

    key: str
    churn_points: int
    priority_points: int

    @property
    def total_impact(self) -> int:
        """Return the combined impact across churn and priority dimensions."""
        return self.churn_points + self.priority_points


def analyze_client_signals(client: Client, signals: ClientSignals) -> ChurnAnalysis:
    """
    Analyze client retention risk using transparent business rules.

    The engine is intentionally deterministic and explainable so the team can
    inspect each contribution before introducing any LLM-based behavior.
    """
    components = _build_score_components(client, signals)
    churn_score = _bounded_score(sum(component.churn_points for component in components))
    priority_score = _bounded_score(sum(component.priority_points for component in components))
    churn_level = _churn_level_from_score(churn_score)
    priority_level = _priority_level_from_score(priority_score)
    main_reason = _main_reason_from_components(client, signals, components)
    suggested_action = _suggest_action(
        client=client,
        signals=signals,
        churn_score=churn_score,
        priority_score=priority_score,
        churn_level=churn_level,
        priority_level=priority_level,
    )
    suggested_channel = _suggest_channel(
        client=client,
        signals=signals,
        suggested_action=suggested_action,
        priority_level=priority_level,
    )

    return ChurnAnalysis(
        client_id=signals.client_id,
        churn_score=churn_score,
        priority_score=priority_score,
        churn_level=churn_level,
        priority_level=priority_level,
        main_reason=main_reason,
        suggested_action=suggested_action,
        suggested_channel=suggested_channel,
    )


def _build_score_components(client: Client, signals: ClientSignals) -> list[ScoreComponent]:
    """Translate each business rule into explicit score components."""
    components = [
        _contact_component(signals.days_without_contact),
        _contribution_component(signals.contribution_drop_pct),
        _maturity_component(signals.maturity_days),
        _negative_sentiment_component(signals.negative_sentiment_detected),
        _life_event_component(signals.life_event_detected, signals.life_event_confidence),
        _financial_insecurity_component(signals.financial_insecurity_detected),
        _assets_component(client.simulated_assets),
        _risk_profile_component(client.risk_profile),
        _maturity_assets_synergy_component(
            maturity_days=signals.maturity_days,
            simulated_assets=client.simulated_assets,
        ),
        _disengagement_stress_component(
            days_without_contact=signals.days_without_contact,
            negative_sentiment_detected=signals.negative_sentiment_detected,
            financial_insecurity_detected=signals.financial_insecurity_detected,
        ),
    ]
    return [component for component in components if component.total_impact > 0]


def _contact_component(days_without_contact: int) -> ScoreComponent:
    """Score disengagement based on recency of advisor contact."""
    if days_without_contact >= 120:
        return ScoreComponent("no_contact", churn_points=34, priority_points=24)
    if days_without_contact >= 90:
        return ScoreComponent("no_contact", churn_points=30, priority_points=20)
    if days_without_contact >= 60:
        return ScoreComponent("no_contact", churn_points=18, priority_points=12)
    if days_without_contact >= 30:
        return ScoreComponent("no_contact", churn_points=10, priority_points=7)
    if days_without_contact >= 14:
        return ScoreComponent("no_contact", churn_points=4, priority_points=3)
    return ScoreComponent("no_contact", churn_points=0, priority_points=0)


def _contribution_component(contribution_drop_pct: float) -> ScoreComponent:
    """Score the deterioration of contribution behavior."""
    if contribution_drop_pct >= 50:
        return ScoreComponent("contribution_drop", churn_points=24, priority_points=14)
    if contribution_drop_pct >= 30:
        return ScoreComponent("contribution_drop", churn_points=18, priority_points=10)
    if contribution_drop_pct >= 15:
        return ScoreComponent("contribution_drop", churn_points=10, priority_points=6)
    if contribution_drop_pct >= 5:
        return ScoreComponent("contribution_drop", churn_points=4, priority_points=2)
    return ScoreComponent("contribution_drop", churn_points=0, priority_points=0)


def _maturity_component(maturity_days: int) -> ScoreComponent:
    """Score urgency caused by upcoming maturity events."""
    if maturity_days <= 15:
        return ScoreComponent("maturity", churn_points=16, priority_points=28)
    if maturity_days <= 30:
        return ScoreComponent("maturity", churn_points=10, priority_points=18)
    if maturity_days <= 60:
        return ScoreComponent("maturity", churn_points=5, priority_points=10)
    return ScoreComponent("maturity", churn_points=0, priority_points=0)


def _negative_sentiment_component(negative_sentiment_detected: bool) -> ScoreComponent:
    """Score relationship stress inferred from recent interactions."""
    if not negative_sentiment_detected:
        return ScoreComponent("negative_sentiment", churn_points=0, priority_points=0)

    return ScoreComponent("negative_sentiment", churn_points=18, priority_points=16)


def _life_event_component(
    life_event_detected: bool,
    life_event_confidence: float,
) -> ScoreComponent:
    """Score the need for proactive advisory support after a life event."""
    if not life_event_detected:
        return ScoreComponent("life_event", churn_points=0, priority_points=0)

    churn_points = round(6 + (life_event_confidence * 8))
    priority_points = round(8 + (life_event_confidence * 10))
    return ScoreComponent(
        "life_event",
        churn_points=churn_points,
        priority_points=priority_points,
    )


def _financial_insecurity_component(financial_insecurity_detected: bool) -> ScoreComponent:
    """Score when the client shows fear or financial stress."""
    if not financial_insecurity_detected:
        return ScoreComponent("financial_insecurity", churn_points=0, priority_points=0)

    return ScoreComponent("financial_insecurity", churn_points=16, priority_points=16)


def _assets_component(simulated_assets: float) -> ScoreComponent:
    """Score operational relevance based on assets under advisory."""
    if simulated_assets >= 2_000_000:
        return ScoreComponent("assets", churn_points=4, priority_points=22)
    if simulated_assets >= 1_000_000:
        return ScoreComponent("assets", churn_points=3, priority_points=16)
    if simulated_assets >= 500_000:
        return ScoreComponent("assets", churn_points=2, priority_points=10)
    if simulated_assets >= 250_000:
        return ScoreComponent("assets", churn_points=1, priority_points=4)
    return ScoreComponent("assets", churn_points=0, priority_points=0)


def _risk_profile_component(risk_profile: RiskProfile) -> ScoreComponent:
    """Slightly increase sensitivity for more volatile investor profiles."""
    if risk_profile == RiskProfile.AGGRESSIVE:
        return ScoreComponent("risk_profile", churn_points=6, priority_points=5)
    if risk_profile == RiskProfile.MODERATE:
        return ScoreComponent("risk_profile", churn_points=3, priority_points=3)
    return ScoreComponent("risk_profile", churn_points=1, priority_points=1)


def _maturity_assets_synergy_component(
    maturity_days: int,
    simulated_assets: float,
) -> ScoreComponent:
    """Boost priority when large assets are close to maturity."""
    if maturity_days <= 15 and simulated_assets >= 1_000_000:
        return ScoreComponent("maturity_assets_synergy", churn_points=4, priority_points=18)
    return ScoreComponent("maturity_assets_synergy", churn_points=0, priority_points=0)


def _disengagement_stress_component(
    days_without_contact: int,
    negative_sentiment_detected: bool,
    financial_insecurity_detected: bool,
) -> ScoreComponent:
    """Boost risk when silence combines with stress or dissatisfaction."""
    if days_without_contact >= 60 and (
        negative_sentiment_detected or financial_insecurity_detected
    ):
        return ScoreComponent("disengagement_stress", churn_points=8, priority_points=10)
    return ScoreComponent("disengagement_stress", churn_points=0, priority_points=0)


def _bounded_score(score: int) -> int:
    """Clip scores to the 0-100 range."""
    return max(0, min(100, score))


def _churn_level_from_score(score: int) -> ChurnLevel:
    """Map churn score to a normalized churn level."""
    if score >= 85:
        return ChurnLevel.CRITICAL
    if score >= 65:
        return ChurnLevel.HIGH
    if score >= 35:
        return ChurnLevel.MEDIUM
    return ChurnLevel.LOW


def _priority_level_from_score(score: int) -> PriorityLevel:
    """Map priority score to an operational urgency level."""
    if score >= 85:
        return PriorityLevel.URGENT
    if score >= 65:
        return PriorityLevel.HIGH
    if score >= 35:
        return PriorityLevel.MEDIUM
    return PriorityLevel.LOW


def _main_reason_from_components(
    client: Client,
    signals: ClientSignals,
    components: list[ScoreComponent],
) -> str:
    """Return a short and human-readable explanation for the dominant driver."""
    if (
        signals.life_event_detected
        and signals.life_event_confidence >= 0.7
        and not signals.negative_sentiment_detected
    ):
        return "Possivel evento de vida pode exigir ajuste no planejamento."

    dominant_component = max(
        components,
        key=lambda component: (component.total_impact, component.priority_points),
    )

    if dominant_component.key == "maturity_assets_synergy":
        return "Patrimonio alto com vencimento proximo pede revisao imediata."
    if dominant_component.key == "maturity":
        return "Vencimento proximo aumenta a necessidade de contato consultivo."
    if dominant_component.key == "no_contact":
        return "Cliente esta ha muito tempo sem contato relevante."
    if dominant_component.key == "contribution_drop":
        return "Queda recente de aportes sinaliza risco de afastamento."
    if dominant_component.key == "negative_sentiment":
        return "Interacoes recentes indicam insatisfacao do cliente."
    if dominant_component.key == "life_event":
        return "Possivel evento de vida pode exigir ajuste no planejamento."
    if dominant_component.key == "financial_insecurity":
        return "Sinais de inseguranca financeira elevam o risco de churn."
    if dominant_component.key == "disengagement_stress":
        return "Longo silencio combinado com estresse financeiro pede acao rapida."
    if dominant_component.key == "assets":
        return (
            "Volume relevante de patrimonio justifica acompanhamento mais proximo."
            if client.simulated_assets >= 1_000_000
            else "Patrimonio relevante merece acompanhamento preventivo."
        )

    return (
        "Perfil mais sensivel a volatilidade pede acompanhamento proativo."
        if client.risk_profile == RiskProfile.AGGRESSIVE
        else "Cenario geral sugere monitoramento regular."
    )


def _suggest_action(
    *,
    client: Client,
    signals: ClientSignals,
    churn_score: int,
    priority_score: int,
    churn_level: ChurnLevel,
    priority_level: PriorityLevel,
) -> str:
    """Recommend the next best action using simple deterministic rules."""
    if (
        priority_level == PriorityLevel.URGENT
        or (churn_level == ChurnLevel.HIGH and signals.days_without_contact >= 90)
        or (
            priority_score >= 65
            and (
                signals.days_without_contact >= 90
                or signals.negative_sentiment_detected
                or signals.financial_insecurity_detected
            )
        )
    ):
        return "ligar hoje"

    if signals.maturity_days <= 30 or (
        signals.maturity_days <= 60 and client.simulated_assets >= 1_000_000
    ):
        return "revisar carteira"

    if (
        signals.life_event_detected
        or signals.financial_insecurity_detected
        or signals.contribution_drop_pct >= 20
    ):
        return "enviar mensagem consultiva"

    if churn_level in {ChurnLevel.MEDIUM, ChurnLevel.HIGH} or signals.days_without_contact >= 30:
        return "fazer follow-up leve"

    return "sem acao urgente"


def _suggest_channel(
    *,
    client: Client,
    signals: ClientSignals,
    suggested_action: str,
    priority_level: PriorityLevel,
) -> Channel:
    """Choose the contact channel based on urgency and context."""
    if suggested_action == "ligar hoje":
        return Channel.PHONE

    if suggested_action == "revisar carteira":
        if client.simulated_assets >= 1_000_000 or signals.maturity_days <= 15:
            return Channel.PHONE
        return Channel.EMAIL

    if suggested_action == "enviar mensagem consultiva":
        if priority_level == PriorityLevel.HIGH and signals.financial_insecurity_detected:
            return Channel.PHONE
        return Channel.WHATSAPP

    if suggested_action == "fazer follow-up leve":
        if signals.days_without_contact >= 60:
            return Channel.WHATSAPP
        return Channel.EMAIL

    return Channel.EMAIL
