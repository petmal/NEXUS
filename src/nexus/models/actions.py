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


class ConfigureAction(ActionBase):
    type: Literal["configure"] = "configure"
    machine: str
    settings: tuple[Annotated[int, Field(strict=True, ge=0, le=16)], ...] = Field(min_length=1, max_length=9)


Action = Annotated[
    ObserveAction
    | MoveAction
    | TakeAction
    | DropAction
    | OperateAction
    | ProbeAction
    | WaitAction
    | FinishAction
    | ConfigureAction,
    Field(discriminator="type"),
]
ACTION_ADAPTER = TypeAdapter(Action)


ACTION_REFERENCE: tuple[dict[str, object], ...] = (
    {
        "type": "observe",
        "description": "Refresh the current observation. Does not consume an environment action.",
        "example": {"type": "observe"},
    },
    {
        "type": "move",
        "description": "Move the agent to an adjacent room. Carried artifacts move with the agent.",
        "example": {"type": "move", "target": "R1"},
    },
    {
        "type": "take",
        "description": "Pick up an artifact located in the current room and carry it in inventory.",
        "example": {"type": "take", "artifact": "A1"},
    },
    {
        "type": "drop",
        "description": "Place a carried artifact into the current room.",
        "example": {"type": "drop", "artifact": "A1"},
    },
    {
        "type": "operate",
        "description": (
            "Apply a machine in the current room to a carried artifact. "
            "This changes the artifact according to the machine's hidden law and consumes a machine use."
        ),
        "example": {"type": "operate", "machine": "M1", "artifact": "A1"},
    },
    {
        "type": "probe",
        "description": (
            "Test a machine in the current room on a carried artifact without changing the real artifact "
            "or consuming a machine use. The returned event reports the hypothetical transformed state. "
            "Probe consumes an environment action."
        ),
        "example": {"type": "probe", "machine": "M1", "artifact": "A1"},
    },
    {
        "type": "wait",
        "description": "Advance the facility phase by one modulo the episode phase cycle.",
        "example": {"type": "wait"},
    },
    {
        "type": "finish",
        "description": (
            "Commit the current state for victory checking. A victory code is returned only when the "
            "goal predicate is currently satisfied."
        ),
        "example": {"type": "finish"},
    },
)


def action_contract(*, scientific: bool = False, resonant: bool = False) -> dict[str, object]:
    """Player-safe description of the stable interaction contract."""
    if scientific:
        reference = tuple(dict(item) for item in ACTION_REFERENCE) + ({
            "type": "configure", "description": "Store the complete controller settings; no correctness feedback until finish.",
            "example": {"type": "configure", "machine": "controller", "settings": [0, 1, 2, 3, 4]},
        },)
        for item in reference:
            if item["type"] == "configure" and resonant:
                item["description"] = "Configure meter with [z], z in 0..6, or controller with its full five-value vector. Neither gives correctness feedback. See manual for the resonance law."
            elif item["type"] == "take":
                item["description"] = "Take an individual artifact, or obtain one identical specimen from a designated stock. Only stocks create copies."
            elif item["type"] == "operate":
                item["description"] = "Apply the named apparatus to a carried specimen; writes a reading or advances preparation as documented. Uses are unlimited when null."
            elif item["type"] == "probe":
                item["description"] = "Preview the named apparatus on a carried specimen, without changing it or consuming a machine use. Advances the action turn. See manual for apparatus ranges."
        return {"schema": ACTION_ADAPTER.json_schema(), "reference": reference}
    # Keep legacy player contracts byte-compatible, including their action union.
    legacy = Annotated[ObserveAction | MoveAction | TakeAction | DropAction | OperateAction
                       | ProbeAction | WaitAction | FinishAction, Field(discriminator="type")]
    return {"schema": TypeAdapter(legacy).json_schema(), "reference": ACTION_REFERENCE}
