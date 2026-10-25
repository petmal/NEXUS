"""Fail-closed, source-bound admission of a paired state-changing discovery pilot."""

from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.discovery import digest
from nexus.generator import generate_episode
from nexus.ontology.repair.qualification import source_binding
from nexus.ontology.stateful.laws import WORLD_INDEX
from nexus.ontology.stateful.policy import public_policy
from nexus.ontology.stateful.proof import (
    handoff_audit,
    prove_kernel,
    prove_public_policy,
    world_audit,
)
from nexus.protocol.session import Session


class Cell(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    seed: StrictInt
    theory: Literal[0, 3]
    discovery: Literal[0, 4, 5]
    planning: Literal[0, 1]
    resource: Literal[0, 1]
    family: Literal["stateful-discovery-v1", "coupled-memory-v1"] = "stateful-discovery-v1"
    role: Literal[
        "shortcut-control",
        "execution-control",
        "known-law",
        "discovery",
        "resource-control",
        "structure-contrast",
        "planning-control",
        "previous-baseline",
    ]
    purpose: str


class Pilot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["stateful-pilot-v1"]
    external_python: Literal[False]
    fresh_context_per_execution: Literal[True]
    common_action_budget: Literal[64]
    recommended_tool_call_limit: Literal[120]
    max_turns: Literal[160]
    runs: tuple[Cell, ...] = Field(min_length=10, max_length=10)

    @model_validator(mode="after")
    def pairs(self):
        if tuple(c.id for c in self.runs) != tuple(f"{i:02d}" for i in range(1, 11)):
            raise ValueError("stateful matrix requires ordered rows01..10")
        roles = (
            "shortcut-control",
            "execution-control",
            "known-law",
            "discovery",
            "resource-control",
            "structure-contrast",
            "structure-contrast",
            "structure-contrast",
            "planning-control",
            "previous-baseline",
        )
        profiles = (
            (3, 5, 1, 1),
            (0, 0, 1, 1),
            (0, 5, 1, 1),
            (3, 5, 1, 1),
            (3, 5, 1, 0),
            (3, 5, 1, 1),
            (3, 5, 1, 1),
            (3, 5, 1, 1),
            (3, 5, 0, 1),
            (3, 4, 0, 1),
        )
        for i, (c, role, axes) in enumerate(zip(self.runs, roles, profiles)):
            if (
                c.role != role
                or (c.theory, c.discovery, c.planning, c.resource) != axes
                or c.family != ("coupled-memory-v1" if i == 9 else "stateful-discovery-v1")
            ):
                raise ValueError("matrix role/family/axes differ from controlled design")
        if len({self.runs[i].seed for i in (1, 2, 3, 4, 8)}) != 1:
            raise ValueError("disclosure/resource/planning controls must share physical truth")
        return self


def preflight(pilot, output):
    start = perf_counter()
    report = {
        "version": "stateful-preflight-v1",
        "status": "running",
        "cells": [],
        "matrix_sha256": digest(pilot.model_dump()),
        "sources": source_binding(),
        "empirical_difficulty_calibrated": False,
        "selection_scope": "Operator-selected seeds; the player contract retains all 256 laws. Do not expose seeds, selection filters, proof reports or source access to evaluated models. This is a challenge set, not an unbiased population difficulty estimate.",
    }
    atomic_json(output, report)
    try:
        report["kernel"] = prove_kernel()
        for c in pilot.runs:
            began = perf_counter()
            ep = generate_episode(
                c.seed,
                axis_version=2,
                science_family=c.family,
                theory_level=c.theory,
                discovery_level=c.discovery,
                planning_level=c.planning,
                resource_pressure=c.resource,
                verifier_secret="operator-stateful-preflight",
            )
            spec = ep.public.investigation.data()
            checks = {}
            detail = {}
            if c.family == "stateful-discovery-v1":
                w = WORLD_INDEX[ep.investigation_truth.data()]
                detail.update(
                    world=w,
                    target=spec.target,
                    mechanism=ep.investigation_truth.data().model_dump(mode="json"),
                )
                detail["all_world_reference"] = prove_public_policy(spec.target)
                if c.role == "shortcut-control":
                    detail["handoff"] = handoff_audit(spec.target, w, stop_on_shortcut=True)
                    checks["negative_control_rejected_by_hard_gate"] = not detail["handoff"][
                        "passes"
                    ]
                elif c.theory == 3:
                    audit = world_audit(spec.target, w)
                    detail.update(audit)
                    checks.update(
                        supported_minimum_at_least12=audit["supported_action_minimum"] >= 12,
                        committed_progress_at_least9=audit[
                            "minimum_committed_operations_with_free_evidence"
                        ]
                        >= 9,
                        initial_panel_blind_negative22=not audit["initial_blind_through_22"],
                        no_shallow_handoff20=audit["handoff"]["passes"],
                        adaptive_branch_at_most20=audit["adaptive_witness"][
                            "selected_branch_actions"
                        ]
                        <= 20,
                        all_outcome_witness_within_common_budget=audit["adaptive_witness"][
                            "all_outcome_upper"
                        ]
                        + 1
                        + c.planning
                        <= 64,
                    )
                    detail["trajectory_tier"] = "bounded-feedback-qualified-v1"
                run = public_policy
            else:
                from nexus.ontology.discovery.policy import public_policy as previous_policy

                run = previous_policy
            session = Session(ep)
            result = run(session, ep.public.evidence_files)
            checks.update(
                live_supported_win=bool(result.victory_code)
                and result.performance.decision_diagnostics.escape_classification
                == "supported_win",
                exact_replay=canonical_hash(replay(ep, session.trace))
                == canonical_hash(session.state),
                reference_bound=result.current_turn
                <= ep.generation_metadata.guaranteed_policy_action_count,
                matched_resource_allowance=ep.public.initial_state.resources.actions_remaining
                == (64 if c.resource else None),
            )
            if not all(checks.values()):
                raise ValueError(f"row{c.id} failed qualification: {checks}")
            report["cells"].append(
                {
                    **c.model_dump(),
                    **detail,
                    "checks": checks,
                    "reference_actual_actions": result.current_turn,
                    "reference_action_upper": ep.generation_metadata.guaranteed_policy_action_count,
                    "seconds": perf_counter() - began,
                }
            )
            atomic_json(output, report)
        contrasts = [report["cells"][i] for i in (3, 5, 6, 7)]
        if (
            len({tuple(c["mechanism"]["gains"]) for c in contrasts}) != 4
            or len({tuple(c["mechanism"]["powers"]) for c in contrasts}) < 3
        ):
            raise ValueError("hard rows lack gain and nonlinear-shape diversity")
        if source_binding() != report["sources"]:
            raise ValueError("source changed during qualification")
        report.update(
            status="passed",
            seconds=perf_counter() - start,
            qualification_scope="Exact supported-path and committed-progress minima; bounded free-panel/one-handoff exclusions; independently checked mechanics and all-outcome policies. No universal cognitive-depth, unbounded-shortcut or model-failure claim.",
        )
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
