"""Schemas for end-to-end client analysis responses."""

from pydantic import ConfigDict

from app.models.full_client_analysis import FullClientAnalysis


class FullClientAnalysisResponse(FullClientAnalysis):
    """API response schema for the complete client analysis flow."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "client": {
                    "id": "client-004",
                    "name": "Diego Martins",
                    "risk_profile": "moderate",
                    "segment": "family_office_light",
                    "simulated_assets": 920000.0,
                    "last_contact_days": 12,
                    "notes": "Comentou que teve filho recente e deseja revisar reserva familiar.",
                },
                "interactions": [
                    {
                        "client_id": "client-004",
                        "channel": "whatsapp",
                        "content": "Cliente comentou chegada do filho e interesse em reforcar reserva.",
                        "sentiment": "positive",
                        "created_at": "2026-03-10T13:10:00Z",
                    }
                ],
                "context_interpretation": {
                    "detected_sentiment": "neutral",
                    "life_event_detected": True,
                    "life_event_confidence": 0.88,
                    "financial_insecurity_detected": False,
                    "short_summary": "Cliente menciona filho recente e quer rever o planejamento.",
                },
                "consolidated_signals": {
                    "client_id": "client-004",
                    "days_without_contact": 12,
                    "contribution_drop_pct": 5.0,
                    "maturity_days": 180,
                    "negative_sentiment_detected": False,
                    "life_event_detected": True,
                    "life_event_confidence": 0.88,
                    "financial_insecurity_detected": False,
                },
                "churn_analysis": {
                    "client_id": "client-004",
                    "churn_score": 21,
                    "priority_score": 26,
                    "churn_level": "low",
                    "priority_level": "low",
                    "main_reason": "Possivel evento de vida pode exigir ajuste no planejamento.",
                    "suggested_action": "enviar mensagem consultiva",
                    "suggested_channel": "whatsapp",
                    "generated_message": "Oi Diego Martins, queria te enviar uma orientacao consultiva personalizada.",
                },
                "interpretation_source": "ai",
                "used_ai": True,
                "used_fallback": False,
                "warning": None,
            }
        }
    )
