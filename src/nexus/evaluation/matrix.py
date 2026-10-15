"""Strict operator matrix admission and real public-policy preflight."""

import hashlib
import json
from pathlib import Path
from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.difficulty import dynamics_audit, inspect_dynamics, inspect_repair, population
from nexus.generator import generate_episode, qualify_episode
from nexus.models.episode import PrivateEpisode
from nexus.presentation import evidence_files
from nexus.protocol.session import Session


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Environment(StrictModel):
    NEXUS_AXIS_VERSION: Literal["2"] = "2"
    NEXUS_SCIENCE_FAMILY: Literal["coupled-repair-v1", "coupled-dynamics-v1"]
    NEXUS_THEORY_LEVEL: Literal["0", "3"]
    NEXUS_DISCOVERY_LEVEL: Literal["0", "5"]
    NEXUS_PLANNING_LEVEL: Literal["0", "1"] = "1"
    NEXUS_RESOURCE_PRESSURE: Literal["1"] = "1"
    NEXUS_SEED: str = Field(pattern=r"^(0|[1-9][0-9]*)$")
    NEXUS_GENERATION_TIMING: Literal["true"] = "true"


class Cell(StrictModel):
    id: str = Field(pattern=r"^nexus-[0-9]{2}$")
    role: Literal["compact-control", "execution-control", "structural-transfer", "history-transfer"]
    environment: Environment


class Matrix(StrictModel):
    version: Literal["difficulty-matrix-v1"]
    runs_per_model: Literal[10] = 10
    external_python: Literal[False] = False
    recommended_tool_call_limit: int = Field(ge=1, le=500, strict=True)
    selection_scope: str
    runs: tuple[Cell, ...]

    @model_validator(mode="after")
    def inventory(self):
        if len(self.runs) != self.runs_per_model or len({r.id for r in self.runs}) != len(
            self.runs
        ):
            raise ValueError("matrix requires ten uniquely identified cells")
        if any(r.environment.NEXUS_PLANNING_LEVEL != "1" for r in self.runs):
            raise ValueError("this matrix holds logistics at P1 and resources at R1")
        expected = {
            "compact-control": 3,
            "execution-control": 1,
            "structural-transfer": 5,
            "history-transfer": 1,
        }
        if {role: sum(r.role == role for r in self.runs) for role in expected} != expected:
            raise ValueError("matrix requires three compact, one execution and six transfer cells")
        for r in self.runs:
            e = r.environment
            expected_family = (
                "coupled-repair-v1" if r.role == "compact-control" else "coupled-dynamics-v1"
            )
            axes = ("0", "0") if r.role == "execution-control" else ("3", "5")
            if (
                e.NEXUS_SCIENCE_FAMILY != expected_family
                or (e.NEXUS_THEORY_LEVEL, e.NEXUS_DISCOVERY_LEVEL) != axes
            ):
                raise ValueError("cell role does not match supported family/axis profile")
        return self


def source_digest() -> str:
    root = Path(__file__).resolve().parents[1]
    values = [
        (p.relative_to(root).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
        for p in sorted(root.rglob("*"))
        if p.suffix in (".py", ".json")
    ]
    return hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()


def matrix_digest(matrix: Matrix) -> str:
    return hashlib.sha256(
        json.dumps(matrix.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def verify_preflight_binding(matrix: Matrix, report: dict) -> None:
    """Reject stale/incomplete reports. Identity checking does not rerun a proof."""
    if report.get("version") != "difficulty-preflight-v1" or report.get("status") != "pilot-ready":
        raise ValueError("preflight is incomplete, blocked or unsupported")
    if (
        report.get("matrix_sha256") != matrix_digest(matrix)
        or report.get("source_sha256") != source_digest()
    ):
        raise ValueError("preflight source or matrix binding is stale")
    rows = report.get("rows", [])
    if [(r["id"], r["role"], r["family"]) for r in rows] != [
        (r.id, r.role, r.environment.NEXUS_SCIENCE_FAMILY) for r in matrix.runs
    ]:
        raise ValueError("preflight rows do not match the matrix")
    if not all(
        r.get("won") is True
        and r.get("replay_verified") is True
        and r.get("qualification", {}).get("passed") is True
        for r in rows
    ):
        raise ValueError("preflight lacks qualification or live win/replay evidence")
    actual = coverage(rows)
    if report.get("coverage") != actual or not all(actual.values()):
        raise ValueError("preflight coverage is missing or inconsistent")
    if (
        report.get("full_rollout_ready") is not False
        or report.get("empirical_difficulty") != "uncalibrated"
    ):
        raise ValueError("structural preflight cannot authorize a full rollout")


def atomic_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def coverage(rows: list[dict]) -> dict[str, bool]:
    repairs = [r for r in rows if r["role"] == "compact-control"]
    challenges = [r for r in rows if r["role"] in ("structural-transfer", "history-transfer")]
    controls = [r for r in rows if r["role"] == "execution-control"]
    return {
        "repair_all_three_laws": {r["difficulty"]["law_degree"] for r in repairs} == {1, 2, 3},
        "repair_no_zero_coupling": all(
            not r["difficulty"]["selected_zero_coupling"] for r in repairs
        ),
        "six_distinct_scientific_worlds": len(challenges)
        == len({r["difficulty"]["world_index"] for r in challenges})
        == 6,
        "six_distinct_mission_targets": len({r["target_fingerprint"] for r in challenges}) == 6,
        "all_transition_forms": {r["difficulty"]["structure"]["transition"] for r in challenges}
        == {0, 1, 2},
        "all_response_forms": {r["difficulty"]["structure"]["response"] for r in challenges}
        == {0, 1, 2},
        "both_wirings": {r["difficulty"]["structure"]["wiring"] for r in challenges} == {0, 1},
        "every_challenge_needs_four_measurements": len(challenges) == 6
        and all(r["difficulty"]["certificate"]["lower_bound"] >= 4 for r in challenges),
        "untreated_data_never_suffices": len(challenges) == 6
        and all(r["difficulty"]["untreated_target_classes"] > 1 for r in challenges),
        "order_sensitive_and_order_insensitive_cases": {
            r["difficulty"]["order_sensitive"] for r in challenges
        }
        == {False, True},
        "history_transfer_needs_longer_experiment": any(
            r["role"] == "history-transfer" and r["difficulty"]["one_pulse_target_classes"] > 1
            for r in challenges
        ),
        "paired_execution_control": len(controls) == 1
        and any(
            r["difficulty"]["world_index"] == controls[0]["difficulty"]["world_index"]
            for r in challenges
        ),
    }


def preflight(matrix: Matrix, output: Path, *, max_certificate_seconds: float = 30) -> dict:
    started = perf_counter()
    report: dict = {
        "version": "difficulty-preflight-v1",
        "status": "running",
        "matrix_sha256": matrix_digest(matrix),
        "source_sha256": source_digest(),
        "operator_only": True,
        "empirical_difficulty": "uncalibrated",
        "full_rollout_ready": False,
        "rows": [],
    }
    atomic_json(output, report)
    try:
        for cell in matrix.runs:
            e = cell.environment
            episode = generate_episode(
                int(e.NEXUS_SEED),
                axis_version=2,
                science_family=e.NEXUS_SCIENCE_FAMILY,
                theory_level=int(e.NEXUS_THEORY_LEVEL),
                discovery_level=int(e.NEXUS_DISCOVERY_LEVEL),
                planning_level=int(e.NEXUS_PLANNING_LEVEL),
                resource_pressure=1,
            )
            episode = PrivateEpisode.model_validate_json(episode.model_dump_json())
            result = qualify_episode(episode)
            if not result.passed:
                raise ValueError(f"{cell.id}: compiled qualification failed: {result.errors}")
            if e.NEXUS_SCIENCE_FAMILY == "coupled-repair-v1":
                from nexus.ontology.repair.policy import public_policy
                from nexus.ontology.repair.runtime import expected

                difficulty = inspect_repair(episode)
                session = Session(episode)
                won = public_policy(session)
            else:
                from nexus.ontology.dynamics.policy import public_policy
                from nexus.ontology.dynamics.runtime import expected

                difficulty = inspect_dynamics(episode, max_seconds=max_certificate_seconds)
                session = Session(episode)
                won = public_policy(session, evidence_files(episode.public))
            if not won.victory_code or canonical_hash(
                replay(episode, session.trace)
            ) != canonical_hash(session.state):
                raise ValueError(f"{cell.id}: live win/replay failed")
            if len(session.trace) + 5 > matrix.recommended_tool_call_limit:
                raise ValueError(
                    f"{cell.id}: tool-call allowance below reference plus evidence requests"
                )
            report["rows"].append(
                {
                    "id": cell.id,
                    "role": cell.role,
                    "family": e.NEXUS_SCIENCE_FAMILY,
                    "difficulty": difficulty,
                    "target_fingerprint": hashlib.sha256(bytes(expected(episode))).hexdigest(),
                    "won": True,
                    "replay_verified": True,
                    "actions": won.current_turn,
                    "action_budget": episode.generation_metadata.action_budget,
                    "qualification": result.model_dump(mode="json"),
                }
            )
            atomic_json(output, report)
            print(f"{cell.id}: won, replayed, {difficulty['band']}", flush=True)
        report["coverage"] = coverage(report["rows"])
        report["population"] = population()
        # Explicitly demonstrate why disclosing a selected pool invalidates full-prior claims.
        selected = tuple(
            r["difficulty"]["world_index"]
            for r in report["rows"]
            if r["role"] in ("structural-transfer", "history-transfer")
        )
        audit = dynamics_audit()
        from nexus.solver.observation_audit import ObservationAudit

        restricted = ObservationAudit(
            tuple(audit.predictions[i] for i in selected),
            tuple(bytes(row[i] for i in selected) for row in audit.rows),
        )
        report["selected_pool_disclosure"] = {
            "warning": "Never disclose this matrix, seed pool, hidden coverage labels or qualification reports to evaluated players. The full-prior certificate does not apply after conditioning on this selected pool.",
            "certificate_lower_bounds_if_pool_revealed": [
                restricted.certificate(i, max_readings=1).lower_bound for i in range(len(selected))
            ],
        }
        if not all(report["coverage"].values()):
            raise ValueError(
                "matrix coverage gates failed: "
                + ", ".join(k for k, v in report["coverage"].items() if not v)
            )
        if report["source_sha256"] != source_digest():
            raise ValueError("package changed during preflight; rerun in a fresh process")
        report["status"] = "pilot-ready"
    except Exception as exc:
        report["status"] = "blocked"
        report["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        report["seconds"] = perf_counter() - started
        atomic_json(output, report)
    return report
