"""Tests for the health endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    """The API should expose a simple readiness endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
