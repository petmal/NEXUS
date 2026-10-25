"""Shortest public-observation conflicts and surviving alternatives for revision."""

from __future__ import annotations

from nexus.models.events import TraceRecord
from nexus.ontology.diagnostics import (
    DecisionWitness,
    ObservationContradiction,
    RejectionContradiction,
    UnresolvedAlternative,
)
from nexus.ontology.discovery.runtime import Tracker, measurement
from nexus.ontology.revision.inference import Belief
from nexus.ontology.revision.laws import QUERIES, class_id, compiled, read


def decision_witness(
    posterior: Belief, attempted: tuple[int, ...] | None, earlier: tuple[TraceRecord, ...]
) -> DecisionWitness | None:
    """Use only the disclosed prior and observations before this submission."""
    if attempted is None or posterior.supports(attempted):
        return None
    prior = compiled()
    attempted_class = class_id(attempted)
    row = prior.rows[attempted_class]
    if posterior.accepting_count(attempted):
        for q, word in enumerate(QUERIES):
            others = posterior.mask & ~prior.partitions[q][row[q]]
            if others:
                alternative = (others & -others).bit_length() - 1
                return UnresolvedAlternative(
                    alternative=prior.representatives[alternative],
                    query=word,
                    attempted_prediction=(row[q],),
                    alternative_prediction=(prior.rows[alternative][q],),
                )
        raise ValueError("compatible decision has no legal conflicting survivor")

    conflicts: list[ObservationContradiction] = []
    for mode, observed in enumerate(posterior.spec.archive):
        if row[mode] != observed:
            conflicts.append(
                ObservationContradiction(
                    source="archive",
                    source_turn=0,
                    query=(mode,),
                    observed=(observed,),
                    predicted=(row[mode],),
                )
            )
    tracker = Tracker("workshop", "workshop", None)
    rejected: list[RejectionContradiction] = []
    for record in earlier:
        tracker.observe(record)
        observation = measurement(record)
        if observation is not None:
            word = tuple(observation.sample["query"])
            observed = tuple(observation.sample["values"])
            predicted = read(attempted, word)
            if predicted != observed:
                conflicts.append(
                    ObservationContradiction(
                        source="reading",
                        source_turn=record.turn,
                        query=word,
                        observed=observed,
                        predicted=predicted,
                    )
                )
        elif record.action.type == "finish" and record.terminal_status.value != "won":
            build = tracker.attempted()
            if build is not None and class_id(build) == attempted_class:
                rejected.append(
                    RejectionContradiction(
                        source_turn=record.turn,
                        rejected_build=build,
                    )
                )
    if conflicts:
        return min(conflicts, key=lambda item: (len(item.query), item.query, item.source_turn))
    if rejected:
        return rejected[0]
    if posterior.spec.resolved is not None:
        actual = prior.rows[class_id(posterior.spec.resolved)]
        q = next(q for q in range(len(QUERIES)) if actual[q] != row[q])
        return ObservationContradiction(
            source="disclosed_construction",
            source_turn=0,
            query=QUERIES[q],
            observed=(actual[q],),
            predicted=(row[q],),
        )
    raise ValueError("contradicted decision has no public-evidence witness")
