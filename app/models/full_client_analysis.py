"""Typed result returned by the end-to-end analysis service."""

from pydantic import BaseModel, Field

from app.models.churn_analysis import ChurnAnalysis
from app.models.client import Client
from app.models.client_signals import ClientSignals
from app.models.interaction import Interaction
from app.schemas.context_interpretation import (
    ContextInterpretation,
    InterpretationSource,
)


class FullClientAnalysis(BaseModel):
    """Complete output of the MVP analysis flow for one client."""

    client: Client
    interactions: list[Interaction] = Field(default_factory=list)
    context_interpretation: ContextInterpretation
    consolidated_signals: ClientSignals
    churn_analysis: ChurnAnalysis
    interpretation_source: InterpretationSource
    used_ai: bool
    used_fallback: bool
    warning: str | None = None
