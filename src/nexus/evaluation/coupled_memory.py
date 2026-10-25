"""Source-bound, paired experiment with honest shortcut and bandwidth controls."""

from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.discovery import Cell, digest, recovery_check
from nexus.generator import generate_episode
from nexus.ontology.coupled_memory.proof import prove
from nexus.ontology.discovery.audit import world_audit
from nexus.ontology.discovery.policy import public_policy
from nexus.ontology.repair.qualification import source_binding
from nexus.protocol.session import Session


class Pilot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["coupled-memory-pilot-v1"]
    external_python: Literal[False]
    fresh_context_per_execution: Literal[True]
    common_action_budget: Literal[64]
    recommended_tool_call_limit: Literal[120]
    max_turns: Literal[160]
    runs: tuple[Cell, ...] = Field(min_length=10, max_length=10)

    @model_validator(mode="after")
    def pairs(self):
        if tuple(c.id for c in self.runs) != tuple(f"{i:02d}" for i in range(1, 11)):
            raise ValueError("matrix requires ordered IDs 01..10")
        if (self.runs[0].family, self.runs[0].seed, self.runs[0].role) != (
            "representation-discovery-v1",
            305,
            "discovery",
        ):
            raise ValueError("row01 must preserve the previous memory baseline")
        if any(c.family != "coupled-memory-v1" for c in self.runs[1:]):
            raise ValueError("rows02..10 must use the new family")
        if tuple(c.role for c in self.runs[1:5]) != (
            "execution-control",
            "known-shape",
            "discovery",
            "budget-ablation",
        ):
            raise ValueError("rows02..05 must provide T0/T2/T3/R0 controls")
        if len({c.seed for c in self.runs[1:5]}) != 1:
            raise ValueError("paired controls must share a truth")
        if any(c.role != "structure-contrast" for c in self.runs[5:]):
            raise ValueError("rows06..10 must be structural contrasts")
        return self


def preflight(pilot, output):
    start = perf_counter()
    report = {
        "version": "coupled-memory-preflight-v1",
        "status": "running",
        "cells": [],
        "matrix_sha256": digest(pilot.model_dump()),
        "deep_tier_admitted": False,
        "empirical_difficulty_calibrated": False,
    }
    atomic_json(output, report)
    try:
        report["sources"] = source_binding()
        proof = prove()
        report["proof_sha256"] = digest(proof)
        report["bounds"] = {
            k: proof[k]
            for k in (
                "adaptive_reading_lower",
                "adaptive_reading_upper",
                "fixed_panel_lower",
                "fixed_panel_upper",
                "oracle_ablations",
                "bandwidth_controls",
                "mixed_probe_finish_evidence_event_lower",
                "mixed_probe_finish_evidence_event_upper",
                "mixed_scope",
                "calibration_first_scope",
            )
        }
        for c in pilot.runs:
            begin = perf_counter()
            ep = generate_episode(
                c.seed,
                axis_version=2,
                science_family=c.family,
                theory_level=c.theory,
                discovery_level=c.discovery,
                planning_level=c.planning,
                resource_pressure=c.resource,
                verifier_secret="operator-coupled-memory-preflight",
            )
            elapsed = perf_counter() - begin
            detail = world_audit(
                c.family, ep.public.investigation.data(), ep.investigation_truth.data()
            )
            session = Session(ep)
            result = public_policy(session, ep.public.evidence_files)
            checks = {
                "certificate_lower": c.expected_certificate_lower
                == detail["certificate_reading_lower"],
                "certificate_upper": c.expected_certificate_upper
                == detail["certificate_reading_upper"],
                "policy_readings": c.expected_policy_readings == detail["public_policy_readings"],
                "live_supported_win": bool(result.victory_code)
                and result.performance.decision_diagnostics.escape_classification
                == "supported_win",
                "replay": canonical_hash(replay(ep, session.trace))
                == canonical_hash(session.state),
                "reference_bound": result.current_turn
                <= ep.generation_metadata.guaranteed_policy_action_count,
                "equal_budget": ep.public.initial_state.resources.actions_remaining
                == (64 if c.resource else None),
            }
            if c.theory:
                checks["history_witness"] = detail["predictive_witness"] is not None
                if c.family == "coupled-memory-v1":
                    checks["bidirectional_feedback_observable"] = all(
                        detail["feedback_witnesses"].values()
                    )
            if not all(checks.values()):
                raise ValueError(f"{c.id}: failed checks {checks}")
            recovered = recovery_check(ep)
            if recovered > 64:
                raise ValueError("recovery exceeds common allowance")
            report["cells"].append(
                {
                    **c.model_dump(),
                    **detail,
                    "checks": checks,
                    "mechanism": ep.investigation_truth.data().model_dump(mode="json"),
                    "actions": result.current_turn,
                    "generation_seconds": elapsed,
                    "recovery_actions": recovered,
                }
            )
            atomic_json(output, report)
        cells = report["cells"]
        if any(c["mechanism"] != cells[1]["mechanism"] for c in cells[2:5]):
            raise ValueError("matched controls changed physical truth")
        contrasts = [cells[3], *cells[5:]]
        if len({tuple(c["dynamics"]) for c in contrasts}) != len(contrasts) or len(
            {c["behavior_class"] for c in contrasts}
        ) != len(contrasts):
            raise ValueError("structure contrasts duplicate dynamics or mission behavior")
        # Require a range of feedback/recurrence structures, predictive sizes and
        # observation encoders, not just renamed wiring or different seed labels.
        if (
            len({tuple(c["dynamics"][1:]) for c in contrasts}) < 4
            or len({c["predictive_states"] for c in contrasts}) < 3
            or len({tuple(c["mechanism"]["program"][4:]) for c in contrasts}) < 3
        ):
            raise ValueError("matrix lacks structural/observation diversity")
        if source_binding() != report["sources"]:
            raise ValueError("source changed during qualification")
        report.update(
            status="passed",
            seconds=perf_counter() - start,
            qualification_scope="Experimental feedback inference. Exact mechanics and declared bounds; no cognitive-depth, superadditivity or model-failure claim.",
        )
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
