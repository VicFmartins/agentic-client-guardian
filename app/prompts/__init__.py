"""Prompt templates package."""

from app.prompts.context_interpreter_prompt import (
    CONTEXT_INTERPRETATION_RESPONSE_SCHEMA,
    CONTEXT_INTERPRETER_SYSTEM_PROMPT,
    build_context_interpreter_prompt,
)
from app.prompts.message_generator_prompt import (
    MESSAGE_GENERATOR_SYSTEM_PROMPT,
    build_message_generator_prompt,
)
from app.prompts.retention_prompt import RETENTION_SYSTEM_PROMPT

__all__ = [
    "build_context_interpreter_prompt",
    "build_message_generator_prompt",
    "CONTEXT_INTERPRETATION_RESPONSE_SCHEMA",
    "CONTEXT_INTERPRETER_SYSTEM_PROMPT",
    "MESSAGE_GENERATOR_SYSTEM_PROMPT",
    "RETENTION_SYSTEM_PROMPT",
]
