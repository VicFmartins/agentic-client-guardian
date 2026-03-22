"""Routes for fake clients, interactions and full analysis."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_analysis_service
from app.db.repositories import get_client_by_id, list_clients, list_interactions_by_client_id
from app.schemas.client import ClientSchema
from app.schemas.error import ErrorResponse
from app.schemas.full_client_analysis import FullClientAnalysisResponse
from app.schemas.interaction import InteractionSchema
from app.services.analysis_service import (
    AnalysisService,
    AnalysisServiceError,
    ClientNotFoundError,
)

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get(
    "",
    response_model=list[ClientSchema],
    summary="List fake clients",
    description="Retorna a lista de clientes simulados disponiveis no MVP.",
)
def list_fake_clients() -> list[ClientSchema]:
    """List all available fake clients."""
    return [ClientSchema.model_validate(client) for client in list_clients()]


@router.get(
    "/{client_id}",
    response_model=ClientSchema,
    summary="Get one client",
    description="Busca um cliente fake pelo identificador.",
    responses={404: {"model": ErrorResponse, "description": "Cliente nao encontrado."}},
)
def get_fake_client(client_id: str) -> ClientSchema:
    """Fetch one fake client by id."""
    client = get_client_by_id(client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente '{client_id}' nao encontrado.",
        )

    return ClientSchema.model_validate(client)


@router.get(
    "/{client_id}/interactions",
    response_model=list[InteractionSchema],
    summary="List client interactions",
    description="Lista as interacoes simuladas de um cliente.",
    responses={404: {"model": ErrorResponse, "description": "Cliente nao encontrado."}},
)
def get_client_interactions(client_id: str) -> list[InteractionSchema]:
    """List deterministic interactions for a given client."""
    client = get_client_by_id(client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente '{client_id}' nao encontrado.",
        )

    interactions = list_interactions_by_client_id(client_id)
    return [InteractionSchema.model_validate(interaction) for interaction in interactions]


@router.post(
    "/{client_id}/analyze",
    response_model=FullClientAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Run full client analysis",
    description=(
        "Executa a analise completa do cliente combinando dados fake, contexto textual, "
        "interpretacao via Gemini com fallback local e engine de scoring."
    ),
    responses={
        404: {"model": ErrorResponse, "description": "Cliente nao encontrado."},
        500: {"model": ErrorResponse, "description": "Erro interno ao analisar o cliente."},
    },
)
def analyze_client(
    client_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service),
) -> FullClientAnalysisResponse:
    """Run the complete analysis flow for a client."""
    try:
        result = analysis_service.run_full_client_analysis(client_id)
    except ClientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except AnalysisServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao analisar o cliente.",
        ) from exc

    return FullClientAnalysisResponse.model_validate(result)
