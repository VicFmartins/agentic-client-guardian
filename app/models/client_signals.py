"""Domain model for churn-related client signals."""

from pydantic import BaseModel, Field, model_validator

from app.models.client import Identifier


class ClientSignals(BaseModel):
    """Aggregated operational and behavioral signals used by the retention engine."""

    client_id: Identifier = Field(..., description="Reference to the analyzed client.")
    days_without_contact: int = Field(
        ...,
        ge=0,
        le=3650,
        description="Days since the last relevant contact happened.",
    )
    contribution_drop_pct: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage drop in recent contributions.",
    )
    maturity_days: int = Field(
        ...,
        ge=0,
        le=36500,
        description="Days remaining to an important product maturity.",
    )
    negative_sentiment_detected: bool = Field(
        ...,
        description="Whether recent interactions suggest negative sentiment.",
    )
    life_event_detected: bool = Field(
        ...,
        description="Whether the system detected a possible life event.",
    )
    life_event_confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence score for the detected life event.",
    )
    financial_insecurity_detected: bool = Field(
        ...,
        description="Whether signs of financial insecurity were found.",
    )

    @model_validator(mode="after")
    def validate_life_event_consistency(self) -> "ClientSignals":
        """Keep life-event flags and confidence aligned."""
        if not self.life_event_detected and self.life_event_confidence > 0:
            raise ValueError(
                "life_event_confidence must be 0 when life_event_detected is False."
            )

        if self.life_event_detected and self.life_event_confidence == 0:
            raise ValueError(
                "life_event_confidence must be greater than 0 when life_event_detected is True."
            )

        return self
