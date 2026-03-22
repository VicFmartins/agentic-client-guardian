"""API schemas for churn analyses."""

from pydantic import ConfigDict

from app.models.churn_analysis import ChurnAnalysis


class ChurnAnalysisSchema(ChurnAnalysis):
    """Churn analysis payload exposed by the API."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "client_id": "client-001",
                "churn_score": 78,
                "priority_score": 88,
                "churn_level": "high",
                "priority_level": "urgent",
                "main_reason": "Longo periodo sem contato combinado com queda nas contribuicoes recentes.",
                "suggested_action": "Agendar uma chamada consultiva para revisar carteira e objetivos.",
                "suggested_channel": "phone",
                "generated_message": "Oi Mariana, percebi movimentos recentes na sua carteira e gostaria de revisar oportunidades com voce ainda esta semana.",
            }
        }
    )
