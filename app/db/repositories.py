"""Simple in-memory repositories backed by deterministic fake data."""

from collections import defaultdict
from collections.abc import Iterable
from typing import Protocol

from app.db.fake_data import (
    CONTRIBUTION_DROP_PCT_BY_CLIENT_ID,
    FAKE_CLIENTS,
    FAKE_INTERACTIONS,
    MATURITY_DAYS_BY_CLIENT_ID,
)
from app.models.client import Client
from app.models.client_signals import ClientSignals
from app.models.interaction import Interaction

_LIFE_EVENT_KEYWORDS = (
    "filho",
    "bebe",
    "casamento",
    "divorcio",
    "gravidez",
    "aposentadoria",
    "mudanca",
)
_FINANCIAL_INSECURITY_KEYWORDS = (
    "insegur",
    "medo",
    "receio",
    "liquidez",
    "renda",
    "despesas",
    "perdas",
)
_NEGATIVE_TONE_KEYWORDS = (
    "frustr",
    "preocupa",
    "insegur",
    "medo",
    "queda",
    "perdas",
)


class ClientRepository(Protocol):
    """Interface for reading client data."""

    def list_clients(self) -> list[Client]:
        """Return every available client."""

    def get_client_by_id(self, client_id: str) -> Client | None:
        """Return one client by identifier."""


class InteractionRepository(Protocol):
    """Interface for reading client interactions."""

    def list_interactions_by_client_id(self, client_id: str) -> list[Interaction]:
        """Return all interactions for a specific client."""


class ClientSignalsRepository(Protocol):
    """Interface for computing initial client signals."""

    def build_initial_signals(self, client_id: str) -> ClientSignals | None:
        """Build one deterministic signals snapshot for a client."""


class InMemoryClientRepository:
    """Client repository backed by an in-memory fixture collection."""

    def __init__(self, clients: Iterable[Client]) -> None:
        self._clients = {client.id: client.model_copy(deep=True) for client in clients}

    def list_clients(self) -> list[Client]:
        """Return a deep-copied list of all fixture clients."""
        return [client.model_copy(deep=True) for client in self._clients.values()]

    def get_client_by_id(self, client_id: str) -> Client | None:
        """Return one client fixture by id."""
        client = self._clients.get(client_id)
        return client.model_copy(deep=True) if client else None


class InMemoryInteractionRepository:
    """Interaction repository backed by in-memory fixture data."""

    def __init__(self, interactions: Iterable[Interaction]) -> None:
        grouped: dict[str, list[Interaction]] = defaultdict(list)

        for interaction in interactions:
            grouped[interaction.client_id].append(interaction.model_copy(deep=True))

        self._interactions_by_client = {
            client_id: sorted(
                items,
                key=lambda item: item.created_at,
                reverse=True,
            )
            for client_id, items in grouped.items()
        }

    def list_interactions_by_client_id(self, client_id: str) -> list[Interaction]:
        """Return deep-copied interactions for a client, newest first."""
        interactions = self._interactions_by_client.get(client_id, [])
        return [interaction.model_copy(deep=True) for interaction in interactions]


class InMemoryClientSignalsRepository:
    """Signals repository that derives flags and metrics from deterministic fixtures."""

    def __init__(
        self,
        client_repository: ClientRepository,
        interaction_repository: InteractionRepository,
    ) -> None:
        self._client_repository = client_repository
        self._interaction_repository = interaction_repository

    def build_initial_signals(self, client_id: str) -> ClientSignals | None:
        """Build deterministic initial signals for a given client."""
        client = self._client_repository.get_client_by_id(client_id)
        if client is None:
            return None

        interactions = self._interaction_repository.list_interactions_by_client_id(client_id)
        text_sources = self._collect_text_sources(client, interactions)
        life_event_matches = self._keyword_matches(text_sources, _LIFE_EVENT_KEYWORDS)
        life_event_detected = life_event_matches > 0

        return ClientSignals(
            client_id=client.id,
            days_without_contact=client.last_contact_days,
            contribution_drop_pct=CONTRIBUTION_DROP_PCT_BY_CLIENT_ID.get(client.id, 0.0),
            maturity_days=MATURITY_DAYS_BY_CLIENT_ID.get(client.id, 365),
            negative_sentiment_detected=self._detect_negative_sentiment(interactions, text_sources),
            life_event_detected=life_event_detected,
            life_event_confidence=self._life_event_confidence(life_event_matches, client.notes),
            financial_insecurity_detected=self._contains_keywords(
                text_sources,
                _FINANCIAL_INSECURITY_KEYWORDS,
            ),
        )

    @staticmethod
    def _collect_text_sources(client: Client, interactions: list[Interaction]) -> list[str]:
        """Aggregate text fields that may contain relevant business signals."""
        texts = [client.notes or ""]
        texts.extend(interaction.content for interaction in interactions)
        texts.extend(interaction.sentiment or "" for interaction in interactions)
        return texts

    @staticmethod
    def _contains_keywords(texts: list[str], keywords: tuple[str, ...]) -> bool:
        """Check whether any keyword appears in the provided texts."""
        return InMemoryClientSignalsRepository._keyword_matches(texts, keywords) > 0

    @staticmethod
    def _keyword_matches(texts: list[str], keywords: tuple[str, ...]) -> int:
        """Count how many different keywords appear across the text sources."""
        combined_text = " ".join(texts).lower()
        return sum(1 for keyword in keywords if keyword in combined_text)

    @staticmethod
    def _detect_negative_sentiment(
        interactions: list[Interaction],
        text_sources: list[str],
    ) -> bool:
        """Infer negative sentiment from fixture sentiment labels and content."""
        if any((interaction.sentiment or "").lower() == "negative" for interaction in interactions):
            return True

        return InMemoryClientSignalsRepository._contains_keywords(
            text_sources,
            _NEGATIVE_TONE_KEYWORDS,
        )

    @staticmethod
    def _life_event_confidence(matches: int, notes: str | None) -> float:
        """Convert keyword evidence into a deterministic confidence score."""
        if matches == 0:
            return 0.0

        note_bonus = 0.1 if notes else 0.0
        return min(0.95, round(0.55 + (matches * 0.1) + note_bonus, 2))


_client_repository = InMemoryClientRepository(FAKE_CLIENTS)
_interaction_repository = InMemoryInteractionRepository(FAKE_INTERACTIONS)
_signals_repository = InMemoryClientSignalsRepository(
    client_repository=_client_repository,
    interaction_repository=_interaction_repository,
)


def list_clients() -> list[Client]:
    """List all fake clients available for the MVP."""
    return _client_repository.list_clients()


def get_client_by_id(client_id: str) -> Client | None:
    """Fetch one fake client by id."""
    return _client_repository.get_client_by_id(client_id)


def list_interactions_by_client_id(client_id: str) -> list[Interaction]:
    """List fake interactions for a given client."""
    return _interaction_repository.list_interactions_by_client_id(client_id)


def build_initial_signals(client_id: str) -> ClientSignals | None:
    """Build deterministic initial signals from the fake fixtures."""
    return _signals_repository.build_initial_signals(client_id)
