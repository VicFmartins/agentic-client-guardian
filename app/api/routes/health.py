"""Health-check endpoints."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check() -> HealthResponse:
    """Return a minimal status payload for uptime checks."""
    return HealthResponse(status="ok")
