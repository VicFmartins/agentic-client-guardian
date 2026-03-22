"""Schemas for prioritized daily operation views."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Channel, ChurnLevel, PriorityLevel
from app.schemas.context_interpretation import InterpretationSource


class DailyPriorityItem(BaseModel):
    """Compact priority item for the daily follow-up queue."""

    client_id: str
    client_name: str
    priority_score: int = Field(..., ge=0, le=100)
    priority_level: PriorityLevel
    churn_score: int = Field(..., ge=0, le=100)
    churn_level: ChurnLevel
    suggested_action: str
    suggested_channel: Channel
    main_reason: str
    interpretation_source: InterpretationSource
    used_ai: bool
    used_fallback: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "client_id": "client-001",
                "client_name": "Helena Prado",
                "priority_score": 69,
                "priority_level": "high",
                "churn_score": 25,
                "churn_level": "low",
                "suggested_action": "revisar carteira",
                "suggested_channel": "phone",
                "main_reason": "Vencimento proximo aumenta a necessidade de contato consultivo.",
                "interpretation_source": "ai",
                "used_ai": True,
                "used_fallback": False,
            }
        }
    )
