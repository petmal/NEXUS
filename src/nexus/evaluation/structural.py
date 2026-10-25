"""Small operator-only pilot: exact query scopes, targeted fixtures and live replay."""

import hashlib
from pathlib import Path
from time import perf_counter
from typing import Literal

from pydantic import Field, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.artifacts import StrictModel, atomic_json
from nexus.generator import generate_episode, qualify_episode
from nexus.ontology.compositional.inference import audit
from nexus.ontology.compositional.laws import QUERIES, population
from nexus.protocol.session import Session
from nexus.provenance import source_digest


class Cell(StrictModel):
    id: str
    role: Literal["execution-control", "dynamics-control", "structural", "intervention-fixture"]
    seed: int = Field(ge=0, strict=True)

    def environment(self):
        return {
            "NEXUS_AXIS_VERSION": "2",
            "NEXUS_SCIENCE_FAMILY": "coupled-dynamics-v1"
            if self.role == "dynamics-control"
            else "compositional-repair-v1",
            "NEXUS_THEORY_LEVEL": "0" if self.role == "execution-control" else "3",
            "NEXUS_DISCOVERY_LEVEL": "0" if self.role == "execution-control" else "5",
            "NEXUS_PLANNING_LEVEL": "1",
            "NEXUS_RESOURCE_PRESSURE": "1",
            "NEXUS_SEED": str(self.seed),
            "NEXUS_GENERATION_TIMING": "true",
        }


class Pilot(StrictModel):
    version: Literal["structural-pilot-v1"]
    external_python: Literal[False] = False
    recommended_tool_call_limit: Literal[120] = 120
    runs: tuple[Cell, ...]

    @model_validator(mode="after")
    def inventory(self):
        if len(self.runs) != 8 or len({r.id for r in self.runs}) != 8:
            raise ValueError("pilot requires eight distinct cells")
        counts = {
            role: sum(r.role == role for r in self.runs)
            for role in (
                "execution-control",
                "dynamics-control",
                "structural",
                "intervention-fixture",
            )
        }
        if tuple(counts.values()) != (1, 1, 2, 4):
            raise ValueError(
                "pilot requires execution/dynamics controls, two structural and four intervention fixtures"
            )
        challenge = [
            r.seed % 615 for r in self.runs if r.role in ("structural", "intervention-fixture")
        ]
        if len(set(challenge)) != len(challenge):
            raise ValueError("duplicate challenge world")
        return self


def digest(pilot):
    return hashlib.sha256(pilot.model_dump_json().encode()).hexdigest()


def coverage(rows):
    challenge = [r for r in rows if r["role"] in ("structural", "intervention-fixture")]
    return {
        "all_graphs": {r["topology"] for r in challenge} == {0, 1, 2},
        "multiple_change_locations": len({r["changed_module"] for r in challenge}) >= 2,
        "four_intervention_obstructions": sum(
            r["role"] == "intervention-fixture" and r["untrimmed_common_repairs"] == 0
            for r in challenge
        )
        == 4,
        "fixtures_need_three_positive_readings": all(
            r["positive_reading_lower_bound"] >= 3
            for r in challenge
            if r["role"] == "intervention-fixture"
        ),
        "both_contexts_needed_in_fixtures": all(
            all(n == 0 for n in r["single_context_common_repairs"])
            for r in challenge
            if r["role"] == "intervention-fixture"
        ),
        "live_wins_replay": len(rows) == 8
        and all(r["won"] and r["replay_verified"] and r["qualified"] for r in rows),
    }


def verify_binding(pilot, report):
    if report.get("version") != "structural-preflight-v1" or report.get("status") != "pilot-ready":
        raise ValueError("incomplete structural preflight")
    if report.get("source_sha256") != source_digest() or report.get("matrix_sha256") != digest(
        pilot
    ):
        raise ValueError("stale structural preflight")
    if [(r["id"], r["role"], r["environment"]) for r in report["rows"]] != [
        (c.id, c.role, c.environment()) for c in pilot.runs
    ]:
        raise ValueError("preflight inventory mismatch")
    if report["coverage"] != coverage(report["rows"]) or not all(report["coverage"].values()):
        raise ValueError("pilot coverage incomplete")
    if (
        report.get("empirical_difficulty") != "uncalibrated"
        or report.get("full_rollout_ready") is not False
    ):
        raise ValueError("pilot cannot authorize a broad rollout")


def preflight(pilot: Pilot, output: Path):
    report = {
        "version": "structural-preflight-v1",
        "status": "running",
        "source_sha256": source_digest(),
        "matrix_sha256": digest(pilot),
        "empirical_difficulty": "uncalibrated",
        "full_rollout_ready": False,
        "selection_scope": "Targeted nonrandom fixtures, not a population failure estimate. No seed, role, pool or private annotation is supplied to players. Fresh context per cell; no external Python.",
        "rows": [],
    }
    atomic_json(output, report)
    try:
        data = audit()
        for cell in pilot.runs:
            env = cell.environment()
            started = perf_counter()
            episode = generate_episode(
                cell.seed,
                axis_version=2,
                science_family=env["NEXUS_SCIENCE_FAMILY"],
                theory_level=int(env["NEXUS_THEORY_LEVEL"]),
                discovery_level=int(env["NEXUS_DISCOVERY_LEVEL"]),
                planning_level=1,
                resource_pressure=1,
            )
            generation_seconds = perf_counter() - started
            if cell.role == "dynamics-control":
                from nexus.ontology.dynamics.policy import public_policy
            else:
                from nexus.ontology.compositional.policy import public_policy
            session = Session(episode)
            result = public_policy(session, episode.public.evidence_files)
            row = {
                "id": cell.id,
                "role": cell.role,
                "environment": env,
                "generation_seconds": generation_seconds,
                "actions": result.current_turn,
                "budget": episode.generation_metadata.action_budget,
                "readings": sum(r.action.type == "probe" for r in session.trace),
                "won": bool(result.victory_code),
                "qualified": qualify_episode(episode).passed,
                "replay_verified": canonical_hash(replay(episode, session.trace))
                == canonical_hash(session.state),
            }
            if cell.role in ("structural", "intervention-fixture"):
                index = cell.seed % len(population())
                world, _ = population()[index]
                row.update(
                    positive_reading_lower_bound=data.positive_reading_lower(index),
                    topology=world.topology,
                    changed_module=world.changed,
                    untrimmed_common_repairs=len(
                        data.common(
                            data.closure(
                                index, [i for i, q in enumerate(QUERIES) if q[2] == (0, 0)]
                            )
                        )
                    ),
                    single_context_common_repairs=[
                        len(
                            data.common(
                                data.closure(
                                    index, [i for i, q in enumerate(QUERIES) if q[0] == mode]
                                )
                            )
                        )
                        for mode in (0, 1)
                    ],
                )
            report["rows"].append(row)
            atomic_json(output, report)
        report["coverage"] = coverage(report["rows"])
        report["status"] = "pilot-ready"
        verify_binding(pilot, report)
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
    atomic_json(output, report)
    return report
