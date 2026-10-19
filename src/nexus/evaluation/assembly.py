"""Source-bound admission of explicitly scoped joint-assembly matrix claims."""

import json
from hashlib import sha256
from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.matrix import atomic_json
from nexus.generator import generate_episode
from nexus.models.actions import FinishAction, MoveAction, TakeAction
from nexus.ontology.assembly.laws import BUILDS, WORLD_INDEX, accepted
from nexus.ontology.assembly.policy import construction, public_policy
from nexus.ontology.assembly.proof import prove_all, world_audit
from nexus.ontology.assembly.schema import FAMILY
from nexus.protocol.session import Session


class Cell(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    seed: StrictInt
    theory: Literal[0, 2, 3]
    discovery: Literal[0, 3, 4]
    budget_profile: Literal["standard", "diagnostic-plus6"] = "standard"
    tier: Literal[
        "execution-control",
        "calibrated-control",
        "cancellation-control",
        "joint-three-channel",
        "joint-transfer",
        "known-shape",
    ]
    expected_certificate_readings: StrictInt = Field(ge=0, le=7)
    expected_policy_readings: StrictInt = Field(ge=0, le=7)
    expected_supported_closures: tuple[
        Literal["local_only", "joint_only", "b_and_joint", "c_and_joint"], ...
    ] = ()
    purpose: str

    @model_validator(mode="after")
    def profile(self):
        if (self.theory == 0) != (self.discovery == 0):
            raise ValueError("control must be T0/D0")
        profiles = {
            "execution-control": (0, 0),
            "calibrated-control": (3, 3),
            "cancellation-control": (2, 4),
            "joint-three-channel": (3, 4),
            "joint-transfer": (3, 4),
            "known-shape": (2, 4),
        }
        if (self.theory, self.discovery) != profiles[self.tier]:
            raise ValueError("tier contradicts T/D profile")
        if self.tier.startswith("joint-") and self.expected_certificate_readings < 4:
            raise ValueError("joint challenge admission requires at least four supporting readings")
        if len(set(self.expected_supported_closures)) != len(self.expected_supported_closures):
            raise ValueError("duplicate closure claim")
        return self


class Pilot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["joint-assembly-pilot-v1"]
    external_python: Literal[False]
    fresh_context_per_execution: Literal[True]
    recommended_tool_call_limit: int = Field(ge=80)
    runs: tuple[Cell, ...] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def ids(self):
        if len({c.id for c in self.runs}) != len(self.runs):
            raise ValueError("duplicate matrix identifiers")
        return self


def recovery_check(episode):
    """Adversarial fault injection, followed by a public-only policy from that state."""
    world = episode.investigation_truth.data()
    wrong = next(d for d in BUILDS if not accepted(world, d))
    session = Session(episode)
    actions = (
        TakeAction(artifact="carrier"),
        *((MoveAction(target="workshop"),) if session.observe().room != "workshop" else ()),
        *construction(wrong),
        FinishAction(),
    )
    for action in actions:
        result = session.act(session.state.turn, action)
        if not result.ok:
            raise ValueError(result.message)
    if result.victory_code or session.state.terminal_status.value != "active":
        raise ValueError("fault injection did not leave a recoverable rejected build")
    result = public_policy(session, episode.public.evidence_files)
    if (
        not result.victory_code
        or result.performance.decision_diagnostics.escape_classification != "supported_win"
    ):
        raise ValueError("public policy failed to recover within the same budget")
    if canonical_hash(replay(episode, session.trace)) != canonical_hash(session.state):
        raise ValueError("recovery replay mismatch")
    return result.current_turn


def preflight(pilot, output):
    from nexus.ontology.repair.qualification import source_binding

    start = perf_counter()
    report = {
        "version": "joint-assembly-preflight-v1",
        "status": "running",
        "sources": None,
        "matrix_sha256": sha256(
            json.dumps(pilot.model_dump(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "cells": [],
        "empirical_difficulty_calibrated": False,
        "deep_tier_admitted": False,
    }
    atomic_json(output, report)
    try:
        sources = source_binding()
        report["sources"] = sources
        proof = prove_all()
        report["proof_sha256"] = sha256(
            json.dumps(proof, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        for cell in pilot.runs:
            begin = perf_counter()
            ep = generate_episode(
                cell.seed,
                axis_version=2,
                science_family=FAMILY,
                theory_level=cell.theory,
                discovery_level=cell.discovery,
                planning_level=0,
                resource_pressure=1,
                budget_profile=cell.budget_profile,
                verifier_secret="operator-assembly-preflight",
            )
            generation = perf_counter() - begin
            spec = ep.public.investigation.data()
            detail = world_audit(spec, WORLD_INDEX[ep.investigation_truth.data()])
            closures = tuple(name for name, v in detail["closures"].items() if v["supported"])
            session = Session(ep)
            result = public_policy(session, ep.public.evidence_files)
            checks = {
                "exact_supporting_certificate": detail["minimum_supporting_readings"]
                == cell.expected_certificate_readings,
                "public_policy_reading_count": detail["public_policy_readings"]
                == cell.expected_policy_readings,
                "closure_claims": set(closures) == set(cell.expected_supported_closures),
                "public_policy_wins": bool(result.victory_code),
                "supported_win": result.performance.decision_diagnostics.escape_classification
                == "supported_win",
                "within_reference_bound": result.current_turn
                <= ep.generation_metadata.guaranteed_policy_action_count,
                "exact_replay": canonical_hash(replay(ep, session.trace))
                == canonical_hash(session.state),
            }
            if cell.tier.startswith("joint-"):
                checks["joint_evidence_obstruction"] = not any(
                    detail["closures"][n]["supported"] for n in ("local_only", "joint_only")
                )
            if cell.tier == "joint-three-channel":
                checks["all_three_channels_necessary"] = (
                    not closures and detail["minimum_supporting_readings"] >= 5
                )
            if cell.tier == "cancellation-control":
                checks["disclosed_cancellation"] = (
                    spec.known_kernel == 0 and detail["closures"]["local_only"]["supported"]
                )
            if not all(checks.values()):
                raise ValueError(f"{cell.id}: failed checks {checks}")
            recovered = recovery_check(ep) if cell.theory else None
            report["cells"].append(
                {
                    **cell.model_dump(),
                    **detail,
                    "checks": checks,
                    "mechanism": ep.investigation_truth.data().model_dump(mode="json"),
                    "actions": result.current_turn,
                    "budget": ep.generation_metadata.action_budget,
                    "recovery_actions_including_injected_failure": recovered,
                    "generation_seconds": generation,
                    "certificate_scope": "Exact actual-outcome supporting readings, oracle query choice; excludes finish feedback and setup. Recovery is a separate adversarial fault test, not a difficulty lower bound.",
                }
            )
            atomic_json(output, report)
        if source_binding() != sources:
            raise ValueError("source changed during preflight")
        hard = [c for c in report["cells"] if c["tier"].startswith("joint-")]
        report["coverage"] = {
            "challenge_kernels": sorted({c["mechanism"]["kernel"] for c in hard}),
            "distinct_challenge_physics": len(
                {
                    tuple(
                        c["mechanism"][k]
                        for k in ("gain_b", "phase_b", "gain_c", "phase_c", "kernel")
                    )
                    for c in hard
                }
            ),
            "controls": sorted({c["tier"] for c in report["cells"] if "control" in c["tier"]}),
        }
        report.update(status="passed", seconds=perf_counter() - start)
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
