"""Fail-closed experimental matrix preflight, with explicit failed deep-tier gate."""

from __future__ import annotations

import json
from hashlib import sha256
from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.matrix import atomic_json
from nexus.generator import generate_episode
from nexus.ontology.history.generation import selection
from nexus.ontology.history.laws import WORLD_INDEX, decisions, shortest
from nexus.ontology.history.policy import public_policy
from nexus.protocol.session import Session


class Cell(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    family: Literal["history-coupled-v1", "coupled-evidence-v1"]
    seed: StrictInt
    control: bool = False
    budget_profile: Literal["standard", "diagnostic-plus6"] = "standard"
    orientation_rival: StrictInt | None = None
    purpose: str


class Pilot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["history-pilot-v1"]
    external_python: Literal[False]
    fresh_context_per_execution: Literal[True]
    recommended_tool_call_limit: int = Field(ge=80)
    runs: tuple[Cell, ...] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def identifiers(self):
        if len({r.id for r in self.runs}) != len(self.runs):
            raise ValueError("duplicate matrix identifiers")
        return self


def preflight(pilot, output):
    from nexus.ontology.repair.qualification import source_binding
    from nexus.ontology.transfer.policy import public_policy as transfer_policy

    report = {
        "version": "history-preflight-v1",
        "status": "running",
        "sources": None,
        "matrix_sha256": sha256(
            json.dumps(pilot.model_dump(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "deep_tier_admitted": False,
        "empirical_difficulty_calibrated": False,
        "cells": [],
        "scope": "Opt-in diagnostic PoC. Full-prior constructive witness, exact live acceptance and replay; no mandatory deep reasoning claim. Rejected finish shortcuts remain legal.",
    }
    atomic_json(output, report)
    try:
        sources = source_binding()
        report["sources"] = sources
        atomic_json(output, report)
        for cell in pilot.runs:
            start = perf_counter()
            ep = generate_episode(
                cell.seed,
                axis_version=2,
                science_family=cell.family,
                theory_level=0 if cell.control else 3,
                discovery_level=0 if cell.control else 5,
                planning_level=1,
                resource_pressure=1,
                budget_profile=cell.budget_profile,
                verifier_secret="operator-history-preflight",
            )
            generation = perf_counter() - start
            session = Session(ep)
            policy = public_policy if cell.family == "history-coupled-v1" else transfer_policy
            started = perf_counter()
            result = policy(session, ep.public.evidence_files)
            seconds = perf_counter() - started
            checks = {
                "public_policy_wins": bool(result.victory_code),
                "supported_win": result.performance.decision_diagnostics.escape_classification
                == "supported_win",
                "reference_bound": result.current_turn
                <= ep.generation_metadata.guaranteed_policy_action_count,
                "replay": canonical_hash(replay(ep, session.trace))
                == canonical_hash(session.state),
            }
            extra = {}
            if cell.family == "history-coupled-v1":
                world = selection(cell.seed)
                index = WORLD_INDEX[world]
                extra = {
                    "world_index": index,
                    "law": world.model_dump(mode="json"),
                    "shortest_physical_pulses": len(shortest(world)),
                }
                if cell.orientation_rival is not None:
                    rival = selection(cell.orientation_rival)
                    other = WORLD_INDEX[rival]
                    checks["passive_orientation_rival"] = (
                        world.gates == rival.gates
                        and world != rival
                        and not decisions().winning[index] & decisions().winning[other]
                    )
            elif cell.orientation_rival is not None:
                raise ValueError("orientation-rival claim requires history family")
            if not all(checks.values()):
                raise ValueError(f"{cell.id}: failed checks {checks}")
            report["cells"].append(
                {
                    **cell.model_dump(),
                    **extra,
                    "checks": checks,
                    "actions": result.current_turn,
                    "budget": ep.generation_metadata.action_budget,
                    "reference_action_upper": ep.generation_metadata.guaranteed_policy_action_count,
                    "generation_seconds": generation,
                    "live_policy_seconds": seconds,
                    "certificate": ep.generation_metadata.investigation_certificate,
                }
            )
            atomic_json(output, report)
        if source_binding() != sources:
            raise ValueError("installed source changed during preflight")
        report["status"] = "passed"
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
