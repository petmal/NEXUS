"""Operator-only paired diagnostic: same world, named 30/36-action conditions."""

import hashlib
from pathlib import Path
from time import perf_counter
from typing import Literal

from pydantic import Field, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.artifacts import StrictModel, atomic_json
from nexus.generator import generate_episode, qualify_episode
from nexus.ontology.compositional.policy import public_policy
from nexus.protocol.session import Session
from nexus.provenance import source_digest


class ModelCondition(StrictModel):
    provider: Literal["google", "xai"]
    model: str
    reasoning: str
    max_completion_tokens: int | None = Field(default=None, gt=0, strict=True)
    max_requests_per_minute: int = Field(gt=0, strict=True)

    @model_validator(mode="after")
    def pilot_configuration(self):
        expected = {
            "google": ("gemini-3.8-flash", "high", None, 3),
            "xai": ("grok-4.7", "xhigh", 65536, 30),
        }[self.provider]
        if (
            self.model,
            self.reasoning,
            self.max_completion_tokens,
            self.max_requests_per_minute,
        ) != expected:
            raise ValueError("model condition differs from the pinned pilot configuration")
        return self


class BudgetCell(StrictModel):
    id: str
    pair: str
    model: str
    original_cell: Literal["structural-05", "structural-07", "structural-08"]
    seed: int = Field(ge=0, strict=True)
    budget_profile: Literal["standard", "diagnostic-plus6"]

    def environment(self):
        return {
            "NEXUS_AXIS_VERSION": "2",
            "NEXUS_SCIENCE_FAMILY": "compositional-repair-v1",
            "NEXUS_THEORY_LEVEL": "3",
            "NEXUS_DISCOVERY_LEVEL": "5",
            "NEXUS_PLANNING_LEVEL": "1",
            "NEXUS_RESOURCE_PRESSURE": "1",
            "NEXUS_SEED": str(self.seed),
            "NEXUS_BUDGET_PROFILE": self.budget_profile,
            "NEXUS_GENERATION_TIMING": "true",
            "NEXUS_EXTENDED_DIAGNOSTICS": "true",
        }

    def generate(self):
        return generate_episode(
            self.seed,
            axis_version=2,
            science_family="compositional-repair-v1",
            theory_level=3,
            discovery_level=5,
            planning_level=1,
            resource_pressure=1,
            budget_profile=self.budget_profile,
        )


class BudgetDiagnostic(StrictModel):
    version: Literal["budget-diagnostic-v1"]
    external_python: Literal[False] = False
    recommended_tool_call_limit: Literal[120] = 120
    fresh_context_per_execution: Literal[True] = True
    models: dict[str, ModelCondition]
    runs: tuple[BudgetCell, ...]

    @model_validator(mode="after")
    def inventory(self):
        if len(self.runs) != 8 or len({r.id for r in self.runs}) != 8:
            raise ValueError("budget diagnostic requires eight distinct executions")
        pairs = {r.pair for r in self.runs}
        if len(pairs) != 4 or {r.model for r in self.runs} != self.models.keys():
            raise ValueError(
                "budget diagnostic requires four pairs and matching model configurations"
            )
        selected = set()
        for pair in pairs:
            runs = [r for r in self.runs if r.pair == pair]
            if len(runs) != 2 or {r.budget_profile for r in runs} != {
                "standard",
                "diagnostic-plus6",
            }:
                raise ValueError("each pair requires standard and diagnostic-plus6")
            if len({(r.model, r.original_cell, r.seed) for r in runs}) != 1:
                raise ValueError("paired executions must use the same model, cell and seed")
            cell = runs[0]
            if (
                cell.seed
                != {"structural-05": 438, "structural-07": 493, "structural-08": 542}[
                    cell.original_cell
                ]
            ):
                raise ValueError("seed does not match original pilot cell")
            selected.add((self.models[cell.model].provider, cell.seed))
        if selected != {("google", 438), ("google", 493), ("google", 542), ("xai", 438)}:
            raise ValueError("expected three Gemini pairs and one Grok pair")
        return self


def digest(matrix):
    return hashlib.sha256(matrix.model_dump_json().encode()).hexdigest()


def science_projection(episode):
    """Remove only the nonce and disclosed budget; everything else must agree."""
    public = episode.public.model_dump(mode="json")
    public.pop("episode_id")
    public["initial_state"]["resources"].pop("actions_remaining")
    return {"public": public, "truth": episode.investigation_truth.model_dump(mode="json")}


def verify_binding(matrix, report):
    if report.get("version") != "budget-preflight-v1" or report.get("status") != "diagnostic-ready":
        raise ValueError("incomplete budget preflight")
    if report.get("source_sha256") != source_digest() or report.get("matrix_sha256") != digest(
        matrix
    ):
        raise ValueError("stale budget preflight")
    if [(r["id"], r["pair"], r["model"], r["environment"]) for r in report["rows"]] != [
        (r.id, r.pair, r.model, r.environment()) for r in matrix.runs
    ]:
        raise ValueError("budget preflight inventory mismatch")
    if [p["pair"] for p in report["pairs"]] != sorted({r.pair for r in matrix.runs}) or not all(
        all(p[k] is True for k in ("same_science", "same_reference_actions", "same_observations"))
        for p in report["pairs"]
    ):
        raise ValueError("budget pairs are not controlled")
    for row, cell in zip(report["rows"], matrix.runs, strict=True):
        budget = 30 if cell.budget_profile == "standard" else 36
        if (
            row["budget"] != budget
            or type(row["reference_actions"]) is not int
            or not 0 < row["reference_actions"] <= 27
            or not all(row[k] is True for k in ("qualified", "won", "replay_verified"))
        ):
            raise ValueError("budget execution failed qualification or replay")


def preflight(matrix: BudgetDiagnostic, output: Path):
    report = {
        "version": "budget-preflight-v1",
        "status": "running",
        "source_sha256": source_digest(),
        "matrix_sha256": digest(matrix),
        "scope": "targeted paired diagnostic; four model/seed pairs, no population difficulty claim",
        "rows": [],
        "pairs": [],
    }
    atomic_json(output, report)
    grouped = {}
    try:
        for cell in matrix.runs:
            start = perf_counter()
            episode = cell.generate()
            elapsed = perf_counter() - start
            session = Session(episode)
            result = public_policy(session, episode.public.evidence_files)
            row = {
                "id": cell.id,
                "pair": cell.pair,
                "model": cell.model,
                "environment": cell.environment(),
                "generation_seconds": elapsed,
                "budget": episode.generation_metadata.action_budget,
                "reference_actions": result.current_turn,
                "qualified": qualify_episode(episode).passed,
                "won": bool(result.victory_code),
                "replay_verified": canonical_hash(replay(episode, session.trace))
                == canonical_hash(session.state),
            }
            report["rows"].append(row)
            grouped.setdefault(cell.pair, []).append((episode, session))
            atomic_json(output, report)
        for pair, ((first, left), (second, right)) in sorted(grouped.items()):
            report["pairs"].append(
                {
                    "pair": pair,
                    "same_science": science_projection(first) == science_projection(second),
                    "same_reference_actions": [r.action for r in left.trace]
                    == [r.action for r in right.trace],
                    "same_observations": [r.events for r in left.trace]
                    == [r.events for r in right.trace],
                }
            )
        report["status"] = "diagnostic-ready"
        verify_binding(matrix, report)
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
    atomic_json(output, report)
    return report
