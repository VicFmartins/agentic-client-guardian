"""Routes for daily operational priorities."""

import time
from threading import Lock

from fastapi import APIRouter, HTTPException, status

from app.db.repositories import build_initial_signals, list_clients
from app.schemas.daily_priority import DailyPriorityItem
from app.schemas.context_interpretation import InterpretationSource
from app.schemas.error import ErrorResponse
from app.services.scoring import analyze_client_signals

router = APIRouter(tags=["priorities"])

# Simple TTL cache for the demo's static fake data.
_CACHE_TTL_SECONDS = 60
_cache: list[DailyPriorityItem] = []
_cache_ts: float = 0.0
_cache_lock = Lock()


@router.get(
    "/daily-priorities",
    response_model=list[DailyPriorityItem],
    summary="List daily priorities",
    description=(
        "Retorna os clientes ordenados por prioridade operacional decrescente. "
        "Para o cenário atual com dados simulados, a fila e calculada apenas com "
        "sinais fake e scoring local, sem depender do Gemini."
    ),
    responses={500: {"model": ErrorResponse, "description": "Erro interno ao gerar prioridades."}},
)
def get_daily_priorities() -> list[DailyPriorityItem]:
    """Build the daily ordered queue using the full analysis flow."""
    global _cache, _cache_ts

    with _cache_lock:
        if _cache and (time.monotonic() - _cache_ts) < _CACHE_TTL_SECONDS:
            return [item.model_copy(deep=True) for item in _cache]

    try:
        result = []
        for client in list_clients():
            signals = build_initial_signals(client.id)
            if signals is None:
                raise RuntimeError(
                    f"Nao foi possivel montar sinais iniciais para o cliente '{client.id}'."
                )

            analysis = analyze_client_signals(client, signals)
            result.append(
                DailyPriorityItem(
                    client_id=client.id,
                    client_name=client.name,
                    priority_score=analysis.priority_score,
                    priority_level=analysis.priority_level,
                    churn_score=analysis.churn_score,
                    churn_level=analysis.churn_level,
                    suggested_action=analysis.suggested_action,
                    suggested_channel=analysis.suggested_channel,
                    main_reason=analysis.main_reason,
                    interpretation_source=InterpretationSource.FALLBACK,
                    used_ai=False,
                    used_fallback=True,
                )
            )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar prioridades.",
        ) from exc

    ordered_result = sorted(
        result,
        key=lambda item: (
            item.priority_score,
            item.churn_score,
            item.client_name,
        ),
        reverse=True,
    )

    with _cache_lock:
        _cache = [item.model_copy(deep=True) for item in ordered_result]
        _cache_ts = time.monotonic()

    return ordered_result
