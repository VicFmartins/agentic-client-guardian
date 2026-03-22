"""Schemas for client-context interpretation produced by the AI layer."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DetectedSentiment(StrEnum):
    """Normalized sentiment classes returned by the interpreter."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class InterpretationSource(StrEnum):
    """Indicates whether the interpretation came from Gemini or local fallback."""

    AI = "ai"
    FALLBACK = "fallback"


class ContextInterpretation(BaseModel):
    """Structured output expected from Gemini or the local fallback."""

    detected_sentiment: DetectedSentiment = Field(
        ...,
        description="Overall sentiment inferred from client notes and recent interactions.",
    )
    life_event_detected: bool = Field(
        ...,
        description="Whether the text suggests a relevant life event.",
    )
    life_event_confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence score for the detected life event.",
    )
    financial_insecurity_detected: bool = Field(
        ...,
        description="Whether the text suggests financial fear or instability.",
    )
    short_summary: str = Field(
        ...,
        min_length=10,
        max_length=280,
        description="Short Portuguese summary ready for downstream business logic.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detected_sentiment": "negative",
                "life_event_detected": True,
                "life_event_confidence": 0.82,
                "financial_insecurity_detected": False,
                "short_summary": "Cliente menciona chegada de filho e pede revisao do planejamento com tom cauteloso.",
            }
        }
    )

    @model_validator(mode="after")
    def validate_life_event_consistency(self) -> "ContextInterpretation":
        """Keep life-event confidence aligned with the detection flag."""
        if not self.life_event_detected and self.life_event_confidence > 0:
            raise ValueError(
                "life_event_confidence must be 0 when life_event_detected is False."
            )

        if self.life_event_detected and self.life_event_confidence == 0:
            raise ValueError(
                "life_event_confidence must be greater than 0 when life_event_detected is True."
            )

        return self


class ContextInterpretationResult(BaseModel):
    """Interpretation payload plus execution metadata for observability."""

    interpretation: ContextInterpretation
    source: InterpretationSource
    used_ai: bool
    used_fallback: bool
    warning: str | None = Field(
        default=None,
        description="Friendly warning when the interpreter had to fall back.",
    )
