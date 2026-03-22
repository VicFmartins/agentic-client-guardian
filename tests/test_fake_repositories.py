"""Tests for deterministic in-memory repositories."""

from app.db.repositories import (
    build_initial_signals,
    get_client_by_id,
    list_clients,
    list_interactions_by_client_id,
)


def test_list_clients_returns_expected_fixture_volume() -> None:
    """The MVP should expose a sufficiently varied fake client base."""
    clients = list_clients()

    assert len(clients) >= 12
    assert clients[0].id == "client-001"


def test_get_client_by_id_returns_none_for_unknown_client() -> None:
    """Unknown client ids should be handled without exceptions."""
    assert get_client_by_id("missing-client") is None


def test_list_interactions_are_sorted_newest_first() -> None:
    """Interaction ordering should stay deterministic for downstream consumers."""
    interactions = list_interactions_by_client_id("client-006")

    assert len(interactions) == 2
    assert interactions[0].created_at > interactions[1].created_at


def test_build_initial_signals_handles_maturity_and_life_events() -> None:
    """Signals should reflect deterministic scenario fixtures."""
    maturity_case = build_initial_signals("client-001")
    life_event_case = build_initial_signals("client-004")

    assert maturity_case is not None
    assert maturity_case.maturity_days == 7
    assert life_event_case is not None
    assert life_event_case.life_event_detected is True
    assert life_event_case.life_event_confidence > 0


def test_build_initial_signals_handles_insecurity_and_healthy_clients() -> None:
    """Signals should distinguish risk scenarios from healthy engagement."""
    insecurity_case = build_initial_signals("client-005")
    healthy_case = build_initial_signals("client-006")

    assert insecurity_case is not None
    assert insecurity_case.financial_insecurity_detected is True
    assert insecurity_case.negative_sentiment_detected is True
    assert healthy_case is not None
    assert healthy_case.financial_insecurity_detected is False
    assert healthy_case.negative_sentiment_detected is False
    assert healthy_case.contribution_drop_pct == 0.0
