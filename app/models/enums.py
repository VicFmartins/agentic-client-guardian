"""Shared enumerations for the retention domain."""

from enum import StrEnum


class RiskProfile(StrEnum):
    """Supported investor risk profiles."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class ChurnLevel(StrEnum):
    """Normalized churn-risk bands."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PriorityLevel(StrEnum):
    """Operational urgency levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Channel(StrEnum):
    """Available contact channels."""

    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PHONE = "phone"
    IN_PERSON = "in_person"
