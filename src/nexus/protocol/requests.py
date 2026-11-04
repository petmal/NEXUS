"""Shared action-envelope validation for HTTP and JSONL transports."""

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from nexus.models.actions import Action


class ActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_turn: StrictInt = Field(ge=0)
    action: Action
