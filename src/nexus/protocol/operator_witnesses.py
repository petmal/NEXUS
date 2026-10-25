"""Optional evidence witnesses, never part of a player response or success rule."""

from __future__ import annotations

from collections.abc import Hashable, Sequence

from nexus.engine.canonical import canonical_hash
from nexus.models.episode import PublicEpisode
from nexus.models.events import TraceRecord
from nexus.ontology.catalog import runtime_for
from nexus.ontology.diagnostics import (
    EvidenceWitnessReport,
    SubmissionWitness,
    SupportedDecisionPoint,
)
from nexus.protocol.decision_metrics import assess_evidence


def submission_witnesses(
    public: PublicEpisode, trace: Sequence[TraceRecord]
) -> EvidenceWitnessReport | None:
    if public.investigation is None:
        return None
    runtime = runtime_for(public.investigation)
    factory = getattr(runtime, "decision_witness", None)
    if factory is None:
        return None
    equivalence_key = getattr(runtime, "decision_equivalence_key", None)
    rejected: dict[Hashable, int] = {}
    posterior = runtime.belief(public.investigation)
    tracker = runtime.mission_tracker(public)
    seen: set[tuple[int, ...]] = set()
    result: list[SubmissionWitness] = []
    common = posterior.common_decisions()
    first = (
        SupportedDecisionPoint(
            turn=0, state_sha256=canonical_hash(public.initial_state), decision=common[0]
        )
        if common
        else None
    )
    for index, record in enumerate(trace):
        tracker.observe(record)
        if record.action.type == "finish":
            attempted = tracker.attempted()
            key = (
                equivalence_key(public.investigation, attempted)
                if equivalence_key is not None and attempted is not None
                else None
            )
            if equivalence_key is not None and attempted is not None and key is None:
                raise ValueError("decision equivalence capability returned a null key")
            evidence = assess_evidence(posterior, attempted)
            witness = factory(posterior, attempted, tuple(trace[:index]))
            if (evidence.classification in ("compatible", "contradicted")) != (witness is not None):
                raise ValueError("family witness disagrees with pre-submission evidence")
            result.append(
                SubmissionWitness(
                    turn=record.turn,
                    classification=evidence.classification,
                    build=attempted,
                    repeated_build=attempted is not None and attempted in seen,
                    previous_rejected_equivalent_turn=(
                        rejected.get(key) if key is not None else None
                    ),
                    witness=witness,
                )
            )
            if attempted is not None:
                seen.add(attempted)
                if record.terminal_status.value != "won":
                    posterior.exclude_target(attempted)
                    if key is not None:
                        rejected.setdefault(key, record.turn)
        observed = runtime.measurement(record)
        if observed is not None:
            posterior.observe(observed)
        common = posterior.common_decisions()
        if first is None and common:
            first = SupportedDecisionPoint(
                turn=record.turn, state_sha256=record.after_hash, decision=common[0]
            )
    return EvidenceWitnessReport(
        submissions=tuple(result),
        first_supported_decision=first,
        decision_equivalence_available=equivalence_key is not None,
    )
