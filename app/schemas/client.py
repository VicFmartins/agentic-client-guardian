"""API schemas for clients."""

from pydantic import ConfigDict

from app.models.client import Client


class ClientSchema(Client):
    """Client payload exposed by the API."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "client-001",
                "name": "Mariana Souza",
                "risk_profile": "moderate",
                "segment": "high_net_worth",
                "simulated_assets": 850000.0,
                "last_contact_days": 18,
                "notes": "Cliente demonstrou interesse em revisar estrategia para aposentadoria.",
            }
        }
    )
