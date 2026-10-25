"""Fail-closed paired model-revision pilot with independently proved semantics."""

from itertools import permutations
from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.discovery import digest
from nexus.generator import generate_episode
from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.discovery.policy import public_policy
from nexus.ontology.inference import Measurement
from nexus.ontology.revision.inference import Belief
from nexus.ontology.revision.laws import EDGES, QUERIES, class_id, compiled
from nexus.ontology.revision.proof import prove, prove_no_three_reading_certificate, require
from nexus.ontology.revision.qualification import audit, policy_reading_bound
from nexus.protocol.session import Session
from nexus.provenance import source_digest


class Cell(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    family: Literal["model-revision-v1", "stateful-discovery-v1"] = "model-revision-v1"
    seed: StrictInt = Field(ge=0)
    theory: Literal[0, 3] = 3
    discovery: Literal[0, 5] = 5
    planning: Literal[0] = 0
    resource: Literal[1] = 1
    guidance: Literal["principles", "provisional"] | None = "provisional"
    role: Literal[
        "execution-control",
        "principles",
        "revision",
        "structure-contrast",
        "shortcut-control",
        "previous-baseline",
    ]
    purpose: str


class Pilot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["model-revision-pilot-v1"]
    external_python: Literal[False]
    fresh_context_per_execution: Literal[True]
    common_action_budget: Literal[64]
    recommended_tool_call_limit: Literal[120]
    max_turns: Literal[160]
    runs: tuple[Cell, ...] = Field(min_length=10, max_length=10)

    @model_validator(mode="after")
    def inventory(self):
        if tuple(c.id for c in self.runs) != tuple(f"{i:02d}" for i in range(1, 11)):
            raise ValueError("revision pilot requires ordered unique IDs 01..10")
        roles = (
            "execution-control",
            "principles",
            "revision",
            "principles",
            "revision",
            "principles",
            "revision",
            "structure-contrast",
            "shortcut-control",
            "previous-baseline",
        )
        for i, c in enumerate(self.runs):
            axes = (0, 0) if i == 0 else (3, 5)
            guidance = None if i == 9 else "principles" if i in (0, 1, 3, 5) else "provisional"
            if (
                c.role != roles[i]
                or (c.theory, c.discovery) != axes
                or c.guidance != guidance
                or c.family != ("stateful-discovery-v1" if i == 9 else "model-revision-v1")
            ):
                raise ValueError("role/family/disclosure mismatch in controlled pilot")
        for left, right in ((1, 2), (3, 4), (5, 6)):
            if self.runs[left].seed != self.runs[right].seed:
                raise ValueError("guidance pairs must use identical physical worlds")
        if self.runs[0].seed != self.runs[1].seed:
            raise ValueError("execution control must match the first discovery pair")
        return self


def topology_key(program):
    """Remove hidden-reservoir renaming and global mode-label swaps from coverage."""
    encodings = []
    for rest in permutations((1, 2, 3)):
        mapping = (0, *rest)
        links = tuple((mapping[EDGES[e][0]], mapping[EDGES[e][1]]) for e in program)
        encodings.extend((links, links[2:] + links[:2]))
    return min(encodings)


def fixed_panel_bound(mask):
    """Constructive full-prior panel; this greedy upper bound is not optimality."""
    groups = (mask,)
    queries = []
    prior = compiled()
    while any(group.bit_count() > 1 for group in groups):
        q = min(
            range(len(QUERIES)),
            key=lambda q: (
                sum(
                    (group & part).bit_count() ** 2
                    for group in groups
                    for part in prior.partitions[q]
                ),
                len(QUERIES[q]),
                QUERIES[q],
            ),
        )
        updated = tuple(
            group & part for group in groups for part in prior.partitions[q] if group & part
        )
        require(updated != groups, "fixed panel cannot resolve prior")
        groups = updated
        queries.append(QUERIES[q])
    return queries


def certificate_witness(episode, queries, rejected=()):
    """Replay the optimistic branch through public operations, not direct mutation."""
    session = Session(episode)
    posterior = Belief(episode.public.investigation.data())

    def act(action):
        response = session.act(expected_turn=session.status().turn, action=action)
        require(response.ok, f"certificate action failed: {response.message}")
        return response

    act(TakeAction(artifact="carrier"))
    for query in queries:
        act(ConfigureAction(machine="reader", settings=query))
        response = act(ProbeAction(machine="reader", artifact="carrier"))
        reading = next(
            e["details"]["result"]["payload"]["reading"]
            for e in response.events
            if "result" in e["details"]
        )
        posterior.observe(Measurement("reader", reading))
    for build in rejected:
        act(ConfigureAction(machine="assembler", settings=build))
        act(OperateAction(machine="assembler", artifact="carrier"))
        response = act(FinishAction())
        require(response.victory_code is None, "mixed witness rejection unexpectedly won")
        posterior.exclude_target(build)
    current = session.state.machines["assembler"].settings
    if not posterior.supports(current):
        act(ConfigureAction(machine="assembler", settings=posterior.common_decisions()[0]))
    act(OperateAction(machine="assembler", artifact="carrier"))
    result = act(FinishAction())
    require(bool(result.victory_code), "certificate did not win")
    require(
        result.performance.decision_diagnostics.escape_classification == "supported_win",
        "certificate won without evidence support",
    )
    require(
        canonical_hash(replay(episode, session.trace)) == canonical_hash(session.state),
        "certificate replay mismatch",
    )
    return result.current_turn


def mixed_feedback_witness(episode, certificate_queries):
    """An optimistic mixed-route witness, not an optimal public policy.

    Proves the surviving shortcut: binary finish feedback can replace readings.
    Selecting the actual rejection branch is operator-only qualification work.
    """
    spec, world = episode.public.investigation.data(), episode.investigation_truth.data()
    truth = class_id(world.program)
    prior = compiled()
    mask = Belief(spec).mask
    queries = certificate_queries[:-1]
    from nexus.ontology.revision.laws import QUERY_INDEX

    for query in queries:
        q = QUERY_INDEX[query]
        mask &= prior.partitions[q][prior.rows[truth][q]]
    rejected = tuple(p for i, p in enumerate(prior.representatives) if i != truth and mask >> i & 1)
    actions = certificate_witness(episode, queries, rejected)
    return {
        "readings": len(queries),
        "failed_finishes": len(rejected),
        "actions": actions,
        "queries": queries,
        "rejected_builds": rejected,
        "scope": "Constructive optimistic supported-win witness; not a minimum or a guaranteed policy.",
    }


def preflight(pilot, output):
    started = perf_counter()
    report = {
        "version": "model-revision-preflight-v1",
        "status": "running",
        "cells": [],
        "matrix_sha256": digest(pilot.model_dump()),
        "selection_scope": "Operator-selected challenge/control set, not a population estimate. Keep seeds, qualification and private source out of evaluated contexts.",
        "empirical_difficulty_calibrated": False,
    }
    atomic_json(output, report)
    episodes = {}
    try:
        report["source_sha256"] = source_digest()
        report["independent_proof"] = prove()
        prior = compiled()
        archive_masks = {tuple(row[:2]): 0 for row in prior.rows}
        for i, row in enumerate(prior.rows):
            archive_masks[tuple(row[:2])] |= 1 << i
        report["all_archive_policy_bounds"] = {
            str(key): policy_reading_bound(mask) for key, mask in archive_masks.items()
        }
        require(
            max(report["all_archive_policy_bounds"].values()) <= 7,
            "reference policy exceeds its declared bound",
        )
        for cell in pilot.runs:
            begin = perf_counter()
            ep = generate_episode(
                cell.seed,
                axis_version=2,
                science_family=cell.family,
                theory_level=cell.theory,
                discovery_level=cell.discovery,
                planning_level=cell.planning,
                resource_pressure=cell.resource,
                ontology_options=None if cell.guidance is None else {"guidance": cell.guidance},
                verifier_secret="operator-revision-preflight",
            )
            episodes[cell.id] = ep
            checks = {}
            detail = {}
            if cell.family == "model-revision-v1":
                spec, truth = ep.public.investigation.data(), ep.investigation_truth.data()
                detail = audit(spec, truth)
                detail["program"] = truth.program
                detail["topology_key"] = topology_key(truth.program)
                detail["fixed_panel_reading_upper"] = len(fixed_panel_bound(Belief(spec).mask))
                checks["certificate_replays_at_exact_minimum"] = (
                    certificate_witness(ep, detail["certificate_queries"])
                    == detail["minimum_supported_actions"]
                )
                if cell.role in ("principles", "revision", "structure-contrast"):
                    checks.update(
                        no_three_reading_certificate=detail["minimum_reading_only_certificate"]
                        >= 4,
                        independent_mode_study_insufficient=detail[
                            "combined_single_mode_all_history_closure"
                        ]
                        > 1,
                        ordered_interaction_required=detail["order_sensitive_witness"] is not None,
                        nontrivial_observable_memory=detail["actual_minimal_machine_states"] >= 6,
                    )
                    if cell.guidance == "provisional":
                        checks.update(
                            genuine_provisional_counterexample=detail[
                                "provisional_is_globally_valid"
                            ]
                            is False
                            and detail["counterexample_is_legal_query"],
                            counterexample_does_not_solve_repair=(
                                detail[
                                    "minimum_additional_reading_certificate_after_counterexample"
                                ]
                                is not None
                                and detail[
                                    "minimum_additional_reading_certificate_after_counterexample"
                                ]
                                >= 3
                            ),
                        )
                    require(all(checks.values()), f"row{cell.id} failed admission: {checks}")
                    detail["independent_reading_lower_bound"] = prove_no_three_reading_certificate(
                        Belief(spec).mask, class_id(truth.program)
                    )
                    detail["mixed_feedback_witness"] = mixed_feedback_witness(
                        ep, detail["certificate_queries"]
                    )
                elif cell.role == "shortcut-control":
                    checks["negative_control_detected"] = (
                        detail["minimum_reading_only_certificate"] == 1
                    )
                run_policy = public_policy
            else:
                from nexus.ontology.stateful.policy import public_policy as stateful_policy

                run_policy = stateful_policy
            session = Session(ep)
            result = run_policy(session, ep.public.evidence_files)
            checks.update(
                supported_live_win=bool(result.victory_code)
                and result.performance.decision_diagnostics.escape_classification
                == "supported_win",
                replay=canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state),
                common_budget=ep.public.initial_state.resources.actions_remaining == 64,
                declared_bound=result.current_turn
                <= ep.generation_metadata.guaranteed_policy_action_count,
            )
            require(all(checks.values()), f"row{cell.id} failed admission: {checks}")
            report["cells"].append(
                {
                    **cell.model_dump(),
                    **detail,
                    "checks": checks,
                    "reference_actual_actions": result.current_turn,
                    "reference_action_upper": ep.generation_metadata.guaranteed_policy_action_count,
                    "seconds": perf_counter() - begin,
                }
            )
            atomic_json(output, report)
        for a, b in (("02", "03"), ("04", "05"), ("06", "07")):
            left, right = episodes[a], episodes[b]
            require(
                left.investigation_truth == right.investigation_truth
                and left.public.initial_state == right.public.initial_state,
                "paired physics/resources differ",
            )
            require(
                Belief(left.public.investigation.data()).mask
                == Belief(right.public.investigation.data()).mask,
                "provisional model changed the trusted prior",
            )
        contrasts = [report["cells"][i] for i in (2, 4, 6, 7)]
        require(
            len({class_id(tuple(row["program"])) for row in contrasts}) == 4,
            "duplicate behavioral contrast",
        )
        require(
            len({row["topology_key"] for row in contrasts}) == 4,
            "renamed or mode-swapped topology contrast",
        )
        require(source_digest() == report["source_sha256"], "source changed during preflight")
        report.update(
            status="passed",
            seconds=perf_counter() - started,
            qualification_scope="Exact all-history behavior, four-reading actual-outcome certificates, all-unary-history ambiguity, paired guidance and distinct topology. No universal mental non-decomposition or model-failure claim.",
        )
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
