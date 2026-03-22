"""HTTP tests for the FastAPI MVP endpoints."""

import time
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_analysis_service
from app.main import app
from app.api.routes import priorities as priorities_route
from app.services import gemini_client as gemini_client_module
from app.services.analysis_service import AnalysisService
from app.services.message_generator import GeneratedMessageResult


class FakeAPIInterpreter:
    """Deterministic interpreter used to avoid external Gemini calls in API tests."""

    def interpret_with_metadata(self, *, client_notes: str | None, latest_interactions: list[str]):
        from app.schemas.context_interpretation import (
            ContextInterpretation,
            ContextInterpretationResult,
            DetectedSentiment,
            InterpretationSource,
        )

        return ContextInterpretationResult(
            interpretation=ContextInterpretation(
                detected_sentiment=DetectedSentiment.NEGATIVE,
                life_event_detected="filho" in (client_notes or "").lower(),
                life_event_confidence=0.82 if "filho" in (client_notes or "").lower() else 0.0,
                financial_insecurity_detected="mercado" in " ".join(latest_interactions).lower(),
                short_summary="Resumo deterministico para testes da API.",
            ),
            source=InterpretationSource.FALLBACK,
            used_ai=False,
            used_fallback=True,
            warning="Teste com interpretacao fake.",
        )


class FakeAPIMessageGenerator:
    """Deterministic message generator for API tests."""

    def generate(self, *, client, analysis, context_interpretation, interactions):
        from app.schemas.context_interpretation import InterpretationSource

        return GeneratedMessageResult(
            message=f"Mensagem fake para {client.name}.",
            source=InterpretationSource.FALLBACK,
            used_ai=False,
            used_fallback=True,
            warning="Teste com gerador fake.",
        )


def _override_analysis_service() -> AnalysisService:
    """Provide a deterministic analysis service for API tests."""
    return AnalysisService(
        context_interpreter=FakeAPIInterpreter(),
        message_generator=FakeAPIMessageGenerator(),
    )


client = TestClient(app)


def setup_module() -> None:
    """Register dependency overrides before the API tests run."""
    app.dependency_overrides[get_analysis_service] = _override_analysis_service


def teardown_module() -> None:
    """Clear dependency overrides after the API tests run."""
    app.dependency_overrides.clear()


def test_health_endpoint_still_returns_ok() -> None:
    """The original health endpoint should remain stable."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_clients_endpoint_returns_fake_clients() -> None:
    """The API should expose the fake client catalog."""
    response = client.get("/clients")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 12
    assert payload[0]["id"] == "client-001"


def test_get_client_endpoint_returns_404_for_unknown_client() -> None:
    """Unknown client ids should produce a proper 404 response."""
    response = client.get("/clients/client-999")

    assert response.status_code == 404
    assert "nao encontrado" in response.json()["detail"].lower()


def test_analyze_endpoint_returns_404_for_unknown_client() -> None:
    """Unknown clients should also fail correctly on the analyze endpoint."""
    response = client.post("/clients/invalid-id/analyze")

    assert response.status_code == 404
    assert "nao encontrado" in response.json()["detail"].lower()


def test_get_client_interactions_endpoint_returns_client_history() -> None:
    """The interactions endpoint should return deterministic interaction data."""
    response = client.get("/clients/client-001/interactions")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    assert payload[0]["client_id"] == "client-001"


def test_analyze_endpoint_returns_full_typed_analysis() -> None:
    """The analyze endpoint should execute the end-to-end flow."""
    response = client.post("/clients/client-004/analyze")

    assert response.status_code == 200
    payload = response.json()
    assert payload["client"]["id"] == "client-004"
    assert payload["churn_analysis"]["client_id"] == "client-004"
    assert payload["used_fallback"] is True
    assert payload["context_interpretation"]["short_summary"]
    assert payload["churn_analysis"]["generated_message"].startswith("Mensagem fake")


def test_full_analysis_falls_back_without_gemini_key_and_returns_valid_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The real service should still answer when Gemini configuration is missing."""
    app.dependency_overrides.clear()
    monkeypatch.setattr(
        gemini_client_module,
        "get_settings",
        lambda: SimpleNamespace(
            gemini_api_key=None,
            gemini_model="gemini-2.5-flash",
        ),
    )

    response = client.post("/clients/client-004/analyze")

    assert response.status_code == 200
    payload = response.json()
    assert payload["used_fallback"] is True
    assert payload["churn_analysis"]["generated_message"]
    assert payload["churn_analysis"]["churn_score"] >= 0
    assert payload["churn_analysis"]["priority_score"] >= 0

    app.dependency_overrides[get_analysis_service] = _override_analysis_service


def test_full_analysis_integration_returns_consistent_non_null_fields() -> None:
    """A full analysis should return coherent and populated business fields."""
    response = client.post("/clients/client-005/analyze")

    assert response.status_code == 200
    payload = response.json()
    analysis = payload["churn_analysis"]
    assert analysis["churn_score"] >= 0
    assert analysis["priority_score"] >= 0
    assert analysis["suggested_action"] is not None
    assert analysis["suggested_channel"] is not None
    assert analysis["generated_message"] is not None
    assert payload["context_interpretation"]["short_summary"] is not None


def test_daily_priorities_returns_descending_priority_scores() -> None:
    """The priorities endpoint should return clients ordered by descending priority."""
    response = client.get("/daily-priorities")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 12
    scores = [item["priority_score"] for item in payload]
    assert scores == sorted(scores, reverse=True)


def test_daily_priorities_cache_makes_second_call_faster(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The second call should benefit from the in-process TTL cache."""
    original_builder = priorities_route.build_initial_signals
    priorities_route._cache = []
    priorities_route._cache_ts = 0.0

    def slow_builder(client_id: str):
        time.sleep(0.01)
        return original_builder(client_id)

    monkeypatch.setattr(priorities_route, "build_initial_signals", slow_builder)

    start_first = time.perf_counter()
    first_response = client.get("/daily-priorities")
    first_duration = time.perf_counter() - start_first

    start_second = time.perf_counter()
    second_response = client.get("/daily-priorities")
    second_duration = time.perf_counter() - start_second

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json() == first_response.json()
    assert second_duration < first_duration
