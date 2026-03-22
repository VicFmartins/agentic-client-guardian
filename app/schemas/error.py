"""Shared error response schemas for the API layer."""

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    """Standard API error payload."""

    detail: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Cliente 'client-999' nao encontrado.",
            }
        }
    )
