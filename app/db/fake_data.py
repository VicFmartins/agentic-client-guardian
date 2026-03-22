"""Deterministic in-memory fixtures for MVP exploration."""

from datetime import UTC, datetime, timedelta

from app.models.client import Client
from app.models.enums import Channel, RiskProfile
from app.models.interaction import Interaction

REFERENCE_DATETIME = datetime(2026, 3, 22, 12, 0, tzinfo=UTC)


def _days_ago(days: int, hour: int = 10, minute: int = 0) -> datetime:
    """Create deterministic timestamps relative to the shared reference date."""
    base = REFERENCE_DATETIME - timedelta(days=days)
    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


FAKE_CLIENTS: tuple[Client, ...] = (
    Client(
        id="client-001",
        name="Helena Prado",
        risk_profile=RiskProfile.CONSERVATIVE,
        segment="private_banking",
        simulated_assets=4_250_000.0,
        last_contact_days=9,
        notes="Possui CDB relevante com vencimento nos proximos 7 dias.",
    ),
    Client(
        id="client-002",
        name="Bruno Lima",
        risk_profile=RiskProfile.MODERATE,
        segment="emerging_affluent",
        simulated_assets=380_000.0,
        last_contact_days=31,
        notes="Aportes mensais cairam de forma consistente no ultimo trimestre.",
    ),
    Client(
        id="client-003",
        name="Carla Menezes",
        risk_profile=RiskProfile.CONSERVATIVE,
        segment="retail_plus",
        simulated_assets=190_000.0,
        last_contact_days=96,
        notes="Cliente discreta, historico de pouco retorno a mensagens recentes.",
    ),
    Client(
        id="client-004",
        name="Diego Martins",
        risk_profile=RiskProfile.MODERATE,
        segment="family_office_light",
        simulated_assets=920_000.0,
        last_contact_days=12,
        notes="Comentou que teve filho recente e deseja revisar reserva familiar.",
    ),
    Client(
        id="client-005",
        name="Fernanda Costa",
        risk_profile=RiskProfile.AGGRESSIVE,
        segment="affluent",
        simulated_assets=610_000.0,
        last_contact_days=24,
        notes="Mostra inseguranca com mercado e receio de novas quedas na bolsa.",
    ),
    Client(
        id="client-006",
        name="Gustavo Rocha",
        risk_profile=RiskProfile.CONSERVATIVE,
        segment="pension_focus",
        simulated_assets=740_000.0,
        last_contact_days=4,
        notes="Cliente muito engajado, segue aportando e responde rapidamente.",
    ),
    Client(
        id="client-007",
        name="Isabela Nunes",
        risk_profile=RiskProfile.MODERATE,
        segment="business_owner",
        simulated_assets=1_180_000.0,
        last_contact_days=43,
        notes="Demonstrou frustracao com performance e pediu revisao objetiva.",
    ),
    Client(
        id="client-008",
        name="Joao Pedro Alves",
        risk_profile=RiskProfile.AGGRESSIVE,
        segment="digital_affluent",
        simulated_assets=455_000.0,
        last_contact_days=2,
        notes="Cliente ativo, engajado e aberto a novas recomendacoes.",
    ),
    Client(
        id="client-009",
        name="Larissa Teixeira",
        risk_profile=RiskProfile.CONSERVATIVE,
        segment="retirees",
        simulated_assets=270_000.0,
        last_contact_days=121,
        notes="Sem interacoes relevantes recentes e menor atividade de conta.",
    ),
    Client(
        id="client-010",
        name="Marcelo Barros",
        risk_profile=RiskProfile.MODERATE,
        segment="insurance_cross_sell",
        simulated_assets=340_000.0,
        last_contact_days=34,
        notes="Citou divorcio em andamento e necessidade de reorganizar liquidez.",
    ),
    Client(
        id="client-011",
        name="Natalia Ribeiro",
        risk_profile=RiskProfile.AGGRESSIVE,
        segment="startup_founder",
        simulated_assets=2_050_000.0,
        last_contact_days=19,
        notes="Debenture relevante vence em 15 dias e cliente quer reinvestir rapido.",
    ),
    Client(
        id="client-012",
        name="Paulo Henrique",
        risk_profile=RiskProfile.CONSERVATIVE,
        segment="salary_portability",
        simulated_assets=130_000.0,
        last_contact_days=62,
        notes="Receoso com mercado e preocupado com estabilidade da renda familiar.",
    ),
)

FAKE_INTERACTIONS: tuple[Interaction, ...] = (
    Interaction(
        client_id="client-001",
        channel=Channel.PHONE,
        content="Falamos sobre o vencimento proximo do CDB e opcoes de reinvestimento.",
        sentiment="neutral",
        created_at=_days_ago(9, 11, 15),
    ),
    Interaction(
        client_id="client-001",
        channel=Channel.EMAIL,
        content="Envio de resumo com alternativas conservadoras para caixa de curto prazo.",
        sentiment="positive",
        created_at=_days_ago(23, 8, 30),
    ),
    Interaction(
        client_id="client-002",
        channel=Channel.WHATSAPP,
        content="Cliente informou que reduziu aportes por priorizar despesas da empresa.",
        sentiment="negative",
        created_at=_days_ago(31, 9, 20),
    ),
    Interaction(
        client_id="client-002",
        channel=Channel.EMAIL,
        content="Compartilhado comparativo de alocacao e impacto de menores contribuicoes.",
        sentiment="neutral",
        created_at=_days_ago(58, 16, 0),
    ),
    Interaction(
        client_id="client-003",
        channel=Channel.EMAIL,
        content="Follow-up sem resposta sobre revisao semestral da carteira.",
        sentiment="neutral",
        created_at=_days_ago(96, 10, 0),
    ),
    Interaction(
        client_id="client-004",
        channel=Channel.WHATSAPP,
        content="Cliente comentou chegada do filho e interesse em reforcar reserva.",
        sentiment="positive",
        created_at=_days_ago(12, 13, 10),
    ),
    Interaction(
        client_id="client-004",
        channel=Channel.PHONE,
        content="Agendada conversa para revisar protecao familiar e liquidez.",
        sentiment="positive",
        created_at=_days_ago(28, 15, 0),
    ),
    Interaction(
        client_id="client-005",
        channel=Channel.PHONE,
        content="Cliente disse estar insegura com o mercado e com medo de novas perdas.",
        sentiment="negative",
        created_at=_days_ago(24, 14, 45),
    ),
    Interaction(
        client_id="client-005",
        channel=Channel.WHATSAPP,
        content="Enviado material de educacao sobre volatilidade e horizonte de investimento.",
        sentiment="neutral",
        created_at=_days_ago(40, 10, 5),
    ),
    Interaction(
        client_id="client-006",
        channel=Channel.WHATSAPP,
        content="Cliente confirmou novo aporte e agradeceu o acompanhamento.",
        sentiment="positive",
        created_at=_days_ago(4, 9, 50),
    ),
    Interaction(
        client_id="client-006",
        channel=Channel.EMAIL,
        content="Resumo mensal enviado com rentabilidade e proximos passos.",
        sentiment="positive",
        created_at=_days_ago(18, 8, 15),
    ),
    Interaction(
        client_id="client-007",
        channel=Channel.PHONE,
        content="Cliente demonstrou frustracao com performance e pediu explicacoes claras.",
        sentiment="negative",
        created_at=_days_ago(43, 17, 20),
    ),
    Interaction(
        client_id="client-008",
        channel=Channel.WHATSAPP,
        content="Cliente respondeu rapidamente e pediu simulacao de novos aportes.",
        sentiment="positive",
        created_at=_days_ago(2, 11, 40),
    ),
    Interaction(
        client_id="client-008",
        channel=Channel.EMAIL,
        content="Compartilhadas oportunidades aderentes ao perfil agressivo.",
        sentiment="positive",
        created_at=_days_ago(16, 9, 0),
    ),
    Interaction(
        client_id="client-009",
        channel=Channel.EMAIL,
        content="Ultimo contato foi um resumo trimestral sem retorno da cliente.",
        sentiment="neutral",
        created_at=_days_ago(121, 8, 45),
    ),
    Interaction(
        client_id="client-010",
        channel=Channel.PHONE,
        content="Cliente mencionou divorcio e necessidade de maior liquidez no curto prazo.",
        sentiment="negative",
        created_at=_days_ago(34, 10, 25),
    ),
    Interaction(
        client_id="client-011",
        channel=Channel.IN_PERSON,
        content="Reuniao sobre reinvestimento de debenture com vencimento proximo.",
        sentiment="positive",
        created_at=_days_ago(19, 15, 30),
    ),
    Interaction(
        client_id="client-011",
        channel=Channel.EMAIL,
        content="Enviadas opcoes para reinvestimento do caixa apos vencimento.",
        sentiment="neutral",
        created_at=_days_ago(32, 9, 10),
    ),
    Interaction(
        client_id="client-012",
        channel=Channel.WHATSAPP,
        content="Cliente relatou receio com mercado e preocupacao com renda da familia.",
        sentiment="negative",
        created_at=_days_ago(62, 18, 0),
    ),
    Interaction(
        client_id="client-012",
        channel=Channel.EMAIL,
        content="Compartilhado conteudo sobre reserva de emergencia e estabilidade financeira.",
        sentiment="neutral",
        created_at=_days_ago(89, 7, 45),
    ),
)

CONTRIBUTION_DROP_PCT_BY_CLIENT_ID: dict[str, float] = {
    "client-001": 0.0,
    "client-002": 42.0,
    "client-003": 8.0,
    "client-004": 5.0,
    "client-005": 18.0,
    "client-006": 0.0,
    "client-007": 22.0,
    "client-008": 0.0,
    "client-009": 55.0,
    "client-010": 28.0,
    "client-011": 10.0,
    "client-012": 15.0,
}

MATURITY_DAYS_BY_CLIENT_ID: dict[str, int] = {
    "client-001": 7,
    "client-002": 90,
    "client-003": 240,
    "client-004": 180,
    "client-005": 60,
    "client-006": 365,
    "client-007": 120,
    "client-008": 210,
    "client-009": 45,
    "client-010": 30,
    "client-011": 15,
    "client-012": 75,
}
