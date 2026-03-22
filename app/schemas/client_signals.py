"""API schemas for client signals."""

from pydantic import ConfigDict

from app.models.client_signals import ClientSignals


class ClientSignalsSchema(ClientSignals):
    """Signal payload exposed by the API."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "client_id": "client-001",
                "days_without_contact": 42,
                "contribution_drop_pct": 37.5,
                "maturity_days": 12,
                "negative_sentiment_detected": True,
                "life_event_detected": True,
                "life_event_confidence": 0.81,
                "financial_insecurity_detected": False,
            }
        }
    )
