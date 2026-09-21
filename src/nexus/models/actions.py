from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class ActionBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ObserveAction(ActionBase):
    type: Literal["observe"] = "observe"


class MoveAction(ActionBase):
    type: Literal["move"] = "move"
    target: str


class TakeAction(ActionBase):
    type: Literal["take"] = "take"
    artifact: str


class DropAction(ActionBase):
    type: Literal["drop"] = "drop"
    artifact: str


class OperateAction(ActionBase):
    type: Literal["operate"] = "operate"
    machine: str
    artifact: str


class ProbeAction(ActionBase):
    type: Literal["probe"] = "probe"
    machine: str
    artifact: str


class WaitAction(ActionBase):
    type: Literal["wait"] = "wait"


class FinishAction(ActionBase):
    type: Literal["finish"] = "finish"


Action = Annotated[
    ObserveAction | MoveAction | TakeAction | DropAction | OperateAction | ProbeAction | WaitAction | FinishAction,
    Field(discriminator="type"),
]
ACTION_ADAPTER = TypeAdapter(Action)
