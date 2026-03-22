"""Validation tests for the retention domain models."""

import pytest
from pydantic import ValidationError

from app.models.churn_analysis import ChurnAnalysis
from app.models.client_signals import ClientSignals
from app.models.enums import Channel, ChurnLevel, PriorityLevel, RiskProfile
from app.schemas.churn_analysis import ChurnAnalysisSchema
from app.schemas.client import ClientSchema
from app.schemas.client_signals import ClientSignalsSchema
from app.schemas.interaction import InteractionSchema


def test_client_schema_accepts_valid_payload() -> None:
    """The client schema should validate a complete MVP payload."""
    payload = ClientSchema(
        id="client-001",
        name="Mariana Souza",
        risk_profile=RiskProfile.MODERATE,
        segment="high_net_worth",
        simulated_assets=850000.0,
        last_contact_days=18,
        notes="Perfil interessado em planejamento de longo prazo.",
    )

    assert payload.risk_profile == RiskProfile.MODERATE


def test_interaction_schema_exposes_openapi_example() -> None:
    """Interaction schema should include an example for Swagger."""
    schema = InteractionSchema.model_json_schema()

    assert schema["example"]["channel"] == "whatsapp"


def test_client_signals_reject_confidence_without_detected_event() -> None:
    """Life-event confidence should be consistent with the detection flag."""
    with pytest.raises(ValidationError):
        ClientSignals(
            client_id="client-001",
            days_without_contact=30,
            contribution_drop_pct=20,
            maturity_days=10,
            negative_sentiment_detected=False,
            life_event_detected=False,
            life_event_confidence=0.4,
            financial_insecurity_detected=False,
        )


def test_churn_analysis_rejects_inconsistent_levels() -> None:
    """Categorical levels must reflect the numeric score bands."""
    with pytest.raises(ValidationError):
        ChurnAnalysis(
            client_id="client-001",
            churn_score=90,
            priority_score=20,
            churn_level=ChurnLevel.HIGH,
            priority_level=PriorityLevel.LOW,
            main_reason="Sinais combinados de insatisfacao e distancia operacional.",
            suggested_action="Agendar revisao estrategica.",
            suggested_channel=Channel.PHONE,
        )


def test_schema_examples_are_available_for_api_docs() -> None:
    """Schemas should expose examples to improve API documentation."""
    assert ClientSignalsSchema.model_json_schema()["example"]["life_event_detected"] is True
    assert ChurnAnalysisSchema.model_json_schema()["example"]["priority_level"] == "urgent"
