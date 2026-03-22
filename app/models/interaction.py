"""Domain model for client interactions."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.models.client import Identifier
from app.models.enums import Channel

Content = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=4000)]
Sentiment = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=30)]


class Interaction(BaseModel):
    """Represents one interaction between advisor and client."""

    client_id: Identifier = Field(..., description="Reference to the related client.")
    channel: Channel = Field(..., description="Channel used in the interaction.")
    content: Content = Field(..., description="Conversation summary or message body.")
    sentiment: Sentiment | None = Field(
        default=None,
        description="Optional sentiment classification such as positive or negative.",
    )
    created_at: datetime = Field(..., description="Timestamp of when the interaction happened.")
