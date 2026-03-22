"""Tests for the deterministic scoring engine."""

from app.db.repositories import build_initial_signals, get_client_by_id
from app.models.enums import Channel, ChurnLevel, PriorityLevel
from app.services.scoring import analyze_client_signals


def test_scoring_prioritizes_high_assets_with_near_maturity() -> None:
    """High-value clients with upcoming maturity should trigger a review-oriented action."""
    client = get_client_by_id("client-001")
    signals = build_initial_signals("client-001")

    assert client is not None
    assert signals is not None

    analysis = analyze_client_signals(client, signals)

    assert analysis.priority_level == PriorityLevel.HIGH
    assert analysis.suggested_action == "revisar carteira"
    assert analysis.suggested_channel == Channel.PHONE
    assert "vencimento" in analysis.main_reason.lower()


def test_scoring_escalates_disengaged_and_declining_client() -> None:
    """Long silence with clear deterioration should create a high-risk recommendation."""
    client = get_client_by_id("client-009")
    signals = build_initial_signals("client-009")

    assert client is not None
    assert signals is not None

    analysis = analyze_client_signals(client, signals)

    assert analysis.churn_level == ChurnLevel.HIGH
    assert analysis.suggested_action == "ligar hoje"
    assert analysis.suggested_channel == Channel.PHONE


def test_scoring_uses_consultive_message_for_life_event_case() -> None:
    """Life events should lead to a supportive consultive outreach."""
    client = get_client_by_id("client-004")
    signals = build_initial_signals("client-004")

    assert client is not None
    assert signals is not None

    analysis = analyze_client_signals(client, signals)

    assert analysis.suggested_action == "enviar mensagem consultiva"
    assert analysis.suggested_channel == Channel.WHATSAPP
    assert "evento de vida" in analysis.main_reason.lower()


def test_scoring_leaves_healthy_client_without_urgent_action() -> None:
    """Healthy and engaged clients should remain low urgency."""
    client = get_client_by_id("client-006")
    signals = build_initial_signals("client-006")

    assert client is not None
    assert signals is not None

    analysis = analyze_client_signals(client, signals)

    assert analysis.churn_level == ChurnLevel.LOW
    assert analysis.priority_level == PriorityLevel.LOW
    assert analysis.suggested_action == "sem acao urgente"
    assert analysis.suggested_channel == Channel.EMAIL
