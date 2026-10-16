"""Post-run evidence classifications, separate from physical success and receipt checks."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

EvidenceClass = Literal["guaranteed", "compatible", "contradicted", "ineligible"]


class EvidenceAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    remaining_worlds: int
    winning_set_signatures: int
    common_repairs: int
    accepting_worlds: int | None
    classification: EvidenceClass


class SubmissionAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    turn: int
    won: bool
    evidence: EvidenceAssessment


class ReadingAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    turn: int
    ordinal: int
    context: int | None
    intervention: bool | None
    worlds_before: int
    worlds_after: int
    common_repairs_after: int


class DecisionDiagnostics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["decision-diagnostics-v1"] = "decision-diagnostics-v1"
    escape_classification: Literal["supported_win", "compatible_win", "not_won"]
    physical_goal_satisfied: bool
    correct_state_without_successful_finish: bool
    final_evidence: EvidenceAssessment
    submissions: tuple[SubmissionAssessment, ...]
    measured_contexts: tuple[int, ...]
    passive_measurements: int
    intervention_measurements: int
    no_signal_measurements: int
    first_intervention_turn: int | None
    first_intervention_measurement: int | None
    first_guaranteed_repair_turn: int | None
    # Only the explicitly enabled operator report includes the reading timeline.
    readings: tuple[ReadingAssessment, ...] | None = None


def assess_evidence(posterior, attempted) -> EvidenceAssessment:
    """Assess the committed, physically eligible decision before its outcome."""
    worlds, signatures = posterior.counts()
    if worlds == 0:
        raise ValueError("cannot classify an empty public posterior")
    common = len(posterior.common_decisions())
    accepting = None if attempted is None else posterior.accepting_count(attempted)
    classification = (
        "ineligible"
        if accepting is None
        else "contradicted"
        if accepting == 0
        else "guaranteed"
        if accepting == worlds
        else "compatible"
    )
    return EvidenceAssessment(
        remaining_worlds=worlds,
        winning_set_signatures=signatures,
        common_repairs=common,
        accepting_worlds=accepting,
        classification=classification,
    )


class DecisionAuditTrail:
    """One-pass accumulator over committed public events; no selected truth access."""

    def __init__(self, posterior):
        self.submissions: list[SubmissionAssessment] = []
        self.readings: list[ReadingAssessment] = []
        self.first_guaranteed = 0 if posterior.common_decisions() else None

    def submission(self, record, posterior, attempted):
        self.submissions.append(
            SubmissionAssessment(
                turn=record.turn,
                won=record.terminal_status.value == "won",
                evidence=assess_evidence(posterior, attempted),
            )
        )

    def after_evidence(self, turn, posterior):
        if self.first_guaranteed is None and posterior.common_decisions():
            self.first_guaranteed = turn

    def measurement(self, record, posterior, before, features):
        self.readings.append(
            ReadingAssessment(
                turn=record.turn,
                ordinal=len(self.readings) + 1,
                context=features[0],
                intervention=features[1],
                worlds_before=before,
                worlds_after=posterior.counts()[0],
                common_repairs_after=len(posterior.common_decisions()),
            )
        )
        self.after_evidence(record.turn, posterior)

    def summary(self, posterior, attempted, *, won, physical_goal, extended):
        final = assess_evidence(posterior, attempted)
        if won:
            # Success is intentionally not fed back into the posterior.
            classification = self.submissions[-1].evidence.classification
            if classification not in ("guaranteed", "compatible"):
                raise ValueError("winning submission contradicts public evidence or eligibility")
            escape = "supported_win" if classification == "guaranteed" else "compatible_win"
        else:
            escape = "not_won"
        first = next((r for r in self.readings if r.intervention is True), None)
        return DecisionDiagnostics(
            escape_classification=escape,
            physical_goal_satisfied=physical_goal,
            correct_state_without_successful_finish=physical_goal and not won,
            final_evidence=final,
            submissions=tuple(self.submissions),
            measured_contexts=tuple(
                sorted({r.context for r in self.readings if r.context is not None})
            ),
            passive_measurements=sum(r.intervention is False for r in self.readings),
            intervention_measurements=sum(r.intervention is True for r in self.readings),
            no_signal_measurements=sum(r.context is None for r in self.readings),
            first_intervention_turn=None if first is None else first.turn,
            first_intervention_measurement=None if first is None else first.ordinal,
            first_guaranteed_repair_turn=self.first_guaranteed,
            readings=tuple(self.readings) if extended else None,
        )
