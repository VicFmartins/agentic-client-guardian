"""API schemas for interactions."""

from pydantic import ConfigDict

from app.models.interaction import Interaction


class InteractionSchema(Interaction):
    """Interaction payload exposed by the API."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "client_id": "client-001",
                "channel": "whatsapp",
                "content": "Cliente comentou preocupacao com volatilidade e pediu revisao de alocacao.",
                "sentiment": "negative",
                "created_at": "2026-03-20T14:30:00Z",
            }
        }
    )
