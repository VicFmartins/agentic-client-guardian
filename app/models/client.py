"""Domain model for advisory clients."""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.models.enums import RiskProfile

Identifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
Segment = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=80)]
Notes = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1500)]


class Client(BaseModel):
    """Core entity that represents a financial advisory client."""

    id: Identifier = Field(..., description="Unique client identifier.")
    name: Name = Field(..., description="Client full name.")
    risk_profile: RiskProfile = Field(..., description="Investor risk profile.")
    segment: Segment = Field(..., description="Business segment used for operations.")
    simulated_assets: float = Field(
        ...,
        ge=0,
        description="Simulated assets under advisory, expressed in local currency.",
    )
    last_contact_days: int = Field(
        ...,
        ge=0,
        le=3650,
        description="Days since the last meaningful advisor interaction.",
    )
    notes: Notes | None = Field(
        default=None,
        description="Optional advisor notes that enrich client context.",
    )
