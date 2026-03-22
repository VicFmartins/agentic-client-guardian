"""Schemas for health-related responses."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Default response schema for service availability checks."""

    status: str
