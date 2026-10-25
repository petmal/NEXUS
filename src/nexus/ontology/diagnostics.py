"""Truth-free optional witness payloads for private operator reports."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class WitnessModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ObservationContradiction(WitnessModel):
    kind: Literal["observation_contradiction"] = "observation_contradiction"
    source: Literal["archive", "reading", "disclosed_construction"]
    source_turn: int
    query: tuple[int, ...]
    observed: tuple[int, ...]
    predicted: tuple[int, ...]


class RejectionContradiction(WitnessModel):
    kind: Literal["rejection_contradiction"] = "rejection_contradiction"
    source_turn: int
    rejected_build: tuple[int, ...]


class UnresolvedAlternative(WitnessModel):
    kind: Literal["unresolved_alternative"] = "unresolved_alternative"
    alternative: tuple[int, ...]
    query: tuple[int, ...]
    attempted_prediction: tuple[int, ...]
    alternative_prediction: tuple[int, ...]
    scope: Literal["one_conflicting_survivor_not_selected_truth"] = (
        "one_conflicting_survivor_not_selected_truth"
    )


DecisionWitness = Annotated[
    ObservationContradiction | RejectionContradiction | UnresolvedAlternative,
    Field(discriminator="kind"),
]


class SubmissionWitness(WitnessModel):
    turn: int
    classification: Literal["guaranteed", "compatible", "contradicted", "ineligible"]
    build: tuple[int, ...] | None
    repeated_build: bool
    previous_rejected_equivalent_turn: int | None = None
    witness: DecisionWitness | None


class SupportedDecisionPoint(WitnessModel):
    turn: int
    state_sha256: str
    decision: tuple[int, ...]
    scope: Literal["first_available_supported_decision_not_a_persistence_claim"] = (
        "first_available_supported_decision_not_a_persistence_claim"
    )


class EvidenceWitnessReport(WitnessModel):
    version: Literal["evidence-witnesses-v2"] = "evidence-witnesses-v2"
    decision_equivalence_available: bool = False
    submissions: tuple[SubmissionWitness, ...]
    first_supported_decision: SupportedDecisionPoint | None = None


__all__ = [
    "DecisionWitness",
    "EvidenceWitnessReport",
    "ObservationContradiction",
    "RejectionContradiction",
    "SubmissionWitness",
    "SupportedDecisionPoint",
    "UnresolvedAlternative",
]
