"""Fail-closed qualification of paired, explicitly experimental discovery pilots."""

import json
from hashlib import sha256
from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.matrix import atomic_json
from nexus.generator import generate_episode
from nexus.models.actions import ConfigureAction, FinishAction, OperateAction, TakeAction
from nexus.ontology.discovery.audit import world_audit
from nexus.ontology.discovery.domains import module
from nexus.ontology.discovery.policy import public_policy
from nexus.ontology.discovery.proof import prove_all
from nexus.protocol.session import Session

FAMILIES = ("representation-discovery-v1", "uncertainty-construction-v1")


class Cell(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    family: Literal["representation-discovery-v1", "uncertainty-construction-v1", "coupled-memory-v1"]
    seed: StrictInt
    theory: Literal[0, 2, 3]
    discovery: Literal[0, 4]
    planning: Literal[0]
    resource: Literal[0, 1]
    role: Literal[
        "execution-control", "known-shape", "discovery", "structure-contrast", "budget-ablation"
    ]
    expected_policy_readings: StrictInt = Field(ge=0, le=6)
    expected_certificate_lower: StrictInt = Field(ge=0, le=6)
    expected_certificate_upper: StrictInt = Field(ge=0, le=6)
    purpose: str

    @model_validator(mode="after")
    def profile(self):
        expected = {
            "execution-control": (0, 0, 1),
            "known-shape": (2, 4, 1),
            "discovery": (3, 4, 1),
            "structure-contrast": (3, 4, 1),
            "budget-ablation": (3, 4, 0),
        }
        if (self.theory, self.discovery, self.resource) != expected[self.role]:
            raise ValueError("role contradicts T/D/R profile")
        if self.expected_certificate_lower > self.expected_certificate_upper:
            raise ValueError("inverted certificate bounds")
        return self


class Pilot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["discovery-pocs-pilot-v1"]
    external_python: Literal[False]
    fresh_context_per_execution: Literal[True]
    extended_private_diagnostics: Literal[True]
    common_action_budget: Literal[64]
    recommended_tool_call_limit: Literal[120]
    max_turns: Literal[160]
    runs: tuple[Cell, ...] = Field(min_length=10, max_length=10)

    @model_validator(mode="after")
    def complete_pairs(self):
        if tuple(c.id for c in self.runs) != tuple(f"{i:02d}" for i in range(1, 11)):
            raise ValueError("matrix must contain ordered unique IDs 01..10")
        roles = (
            "execution-control",
            "known-shape",
            "discovery",
            "structure-contrast",
            "budget-ablation",
        )
        for start, family in ((0, FAMILIES[0]), (5, FAMILIES[1])):
            group = self.runs[start : start + 5]
            if tuple(c.role for c in group) != roles or any(c.family != family for c in group):
                raise ValueError("each family requires all five paired roles")
            if len({group[i].seed for i in (0, 1, 2, 4)}) != 1 or group[3].seed == group[2].seed:
                raise ValueError(
                    "matched controls need identical seeds and a separate structure contrast"
                )
        return self


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def recovery_check(ep):
    laws = module(ep.public.investigation.ontology, "laws")
    belief = module(ep.public.investigation.ontology, "inference").Belief(
        ep.public.investigation.data()
    )
    wrong = next(
        b for b in belief.table.builds if not laws.accepted(ep.investigation_truth.data(), b)
    )
    session = Session(ep)
    for action in (
        TakeAction(artifact="carrier"),
        ConfigureAction(machine="assembler", settings=wrong),
        OperateAction(machine="assembler", artifact="carrier"),
        FinishAction(),
    ):
        result = session.act(session.state.turn, action)
        if not result.ok:
            raise ValueError(result.message)
    if result.victory_code or session.state.terminal_status.value != "active":
        raise ValueError("rejected construction is not recoverable")
    result = public_policy(session, ep.public.evidence_files)
    if (
        not result.victory_code
        or result.performance.decision_diagnostics.escape_classification != "supported_win"
    ):
        raise ValueError("recovery failed")
    if canonical_hash(replay(ep, session.trace)) != canonical_hash(session.state):
        raise ValueError("recovery replay mismatch")
    return result.current_turn


def preflight(pilot, output):
    from nexus.ontology.repair.qualification import source_binding

    start = perf_counter()
    report = {
        "version": "discovery-preflight-v1",
        "status": "running",
        "sources": None,
        "matrix_sha256": digest(pilot.model_dump()),
        "cells": [],
        "empirical_difficulty_calibrated": False,
        "deep_tier_admitted": False,
    }
    atomic_json(output, report)
    try:
        report["sources"] = source_binding()
        proof = prove_all()
        report["proof_sha256"] = digest(proof)
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
                verifier_secret="operator-discovery-preflight",
            )
            generation_seconds = perf_counter() - begin
            detail = world_audit(
                cell.family, ep.public.investigation.data(), ep.investigation_truth.data()
            )
            session = Session(ep)
            result = public_policy(session, ep.public.evidence_files)
            checks = {
                "certificate_lower": detail["certificate_reading_lower"]
                == cell.expected_certificate_lower,
                "certificate_upper": detail["certificate_reading_upper"]
                == cell.expected_certificate_upper,
                "policy_readings": detail["public_policy_readings"]
                == cell.expected_policy_readings,
                "live_supported_win": bool(result.victory_code)
                and result.performance.decision_diagnostics.escape_classification
                == "supported_win",
                "reference_bound": result.current_turn
                <= ep.generation_metadata.guaranteed_policy_action_count,
                "exact_replay": canonical_hash(replay(ep, session.trace))
                == canonical_hash(session.state),
                "equal_budget": ep.public.initial_state.resources.actions_remaining
                == (64 if cell.resource else None),
            }
            if cell.theory:
                checks["nontrivial_prior"] = detail["prior_mission_classes"] > 1
                if cell.family == FAMILIES[0]:
                    checks["memory_required"] = (
                        detail["predictive_states"] == 27
                        and detail["predictive_witness"] is not None
                    )
                else:
                    checks["measurement_relevant"] = detail["loading_matters_to_every_valid_build"]
                    checks["moments_insufficient"] = not detail["moments_only_supported"]
            if not all(checks.values()):
                raise ValueError(f"{cell.id}: failed checks {checks}")
            recovered = recovery_check(ep)
            if recovered > 64:
                raise ValueError("recovery exceeds the common moderate allowance")
            report["cells"].append(
                {
                    **cell.model_dump(),
                    **detail,
                    "checks": checks,
                    "mechanism": ep.investigation_truth.data().model_dump(mode="json"),
                    "actions": result.current_turn,
                    "budget": ep.public.initial_state.resources.actions_remaining,
                    "recovery_actions_including_injected_failure": recovered,
                    "generation_seconds": generation_seconds,
                }
            )
            atomic_json(output, report)
        for group_start in (0, 5):
            cells = report["cells"][group_start : group_start + 5]
            if any(cells[i]["mechanism"] != cells[0]["mechanism"] for i in (1, 2, 4)):
                raise ValueError("matched physical worlds differ")
        left, right = report["cells"][2:4]
        if (
            left["skeleton"] == right["skeleton"]
            or left["behavior_class"] == right["behavior_class"]
        ):
            raise ValueError("representation contrast is only parameter spelling")
        left, right = report["cells"][7:9]
        if left["mechanism"]["checks"] == right["mechanism"]["checks"]:
            raise ValueError("uncertainty contrast does not change dependence structure")
        if source_binding() != report["sources"]:
            raise ValueError("source changed during preflight")
        report.update(
            status="passed",
            seconds=perf_counter() - start,
            qualification_scope="Exact finite mechanics, scoped shortcut certificates, matched controls and live supported wins. Not a guarantee of LLM failure or intrinsic deep reasoning.",
        )
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
