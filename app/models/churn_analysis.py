"""Domain model for retention-engine results."""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, model_validator

from app.models.client import Identifier
from app.models.enums import Channel, ChurnLevel, PriorityLevel

ReasonText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)]
ActionText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)]
MessageText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=2000)]


class ChurnAnalysis(BaseModel):
    """Structured retention recommendation generated for a client."""

    client_id: Identifier = Field(..., description="Reference to the analyzed client.")
    churn_score: int = Field(..., ge=0, le=100, description="Churn score from 0 to 100.")
    priority_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Operational priority score from 0 to 100.",
    )
    churn_level: ChurnLevel = Field(..., description="Risk band derived from churn_score.")
    priority_level: PriorityLevel = Field(
        ...,
        description="Operational urgency derived from priority_score.",
    )
    main_reason: ReasonText = Field(..., description="Main reason behind the churn analysis.")
    suggested_action: ActionText = Field(
        ...,
        description="Recommended next best action for the advisor.",
    )
    suggested_channel: Channel = Field(
        ...,
        description="Preferred channel to execute the suggested action.",
    )
    generated_message: MessageText | None = Field(
        default=None,
        description="Optional ready-to-send personalized message.",
    )

    @model_validator(mode="after")
    def validate_level_consistency(self) -> "ChurnAnalysis":
        """Ensure the categorical levels match the numeric scores."""
        if self.churn_level != self._expected_churn_level(self.churn_score):
            raise ValueError("churn_level is inconsistent with churn_score.")

        if self.priority_level != self._expected_priority_level(self.priority_score):
            raise ValueError("priority_level is inconsistent with priority_score.")

        return self

    @staticmethod
    def _expected_churn_level(score: int) -> ChurnLevel:
        if score >= 85:
            return ChurnLevel.CRITICAL
        if score >= 65:
            return ChurnLevel.HIGH
        if score >= 35:
            return ChurnLevel.MEDIUM
        return ChurnLevel.LOW

    @staticmethod
    def _expected_priority_level(score: int) -> PriorityLevel:
        if score >= 85:
            return PriorityLevel.URGENT
        if score >= 65:
            return PriorityLevel.HIGH
        if score >= 35:
            return PriorityLevel.MEDIUM
        return PriorityLevel.LOW
