"""Reusable FastAPI dependencies for the API layer."""

from app.services.analysis_service import AnalysisService


def get_analysis_service() -> AnalysisService:
    """Return the default analysis service instance."""
    return AnalysisService()
