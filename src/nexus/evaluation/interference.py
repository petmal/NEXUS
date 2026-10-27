"""Paired short/long disclosed-interference qualification and MindTrial export."""

import json
from pathlib import Path
from time import perf_counter
from typing import Literal

from pydantic import Field, StrictInt, model_validator

from nexus.evaluation.artifacts import StrictModel, atomic_json
from nexus.evaluation.coordination import task_config
from nexus.evaluation.discovery import digest
from nexus.generator import generate_episode, qualify_episode
from nexus.ontology.interference.generation import selection
from nexus.ontology.interference.laws import encode
from nexus.ontology.interference.planner import (
    bank_contiguous_distances,
    minimum_goal_breaks,
    optimal,
)
from nexus.ontology.interference.proof import (
    independent_bank_minima,
    prove_kernel,
    scalar_cost,
    scalar_minimum_goal_breaks,
)
from nexus.ontology.interference.schema import COUNT, FAMILY, SIZE, GenerationOptions
from nexus.ontology.repair.qualification import source_binding

SEEDS = (67, 79, 101, 103)


class Cell(StrictModel):
    id: str
    suite: Literal["core", "slack"]
    seed: StrictInt
    horizon: Literal["short", "long"]
    coupling: Literal["independent", "coupled"]
    resource: StrictInt = Field(ge=1, le=2)

    def options(self):
        return GenerationOptions(horizon=self.horizon, coupling=self.coupling)


class Pilot(StrictModel):
    version: Literal["interference-pilot-v1"]
    family: Literal["stateful-interference-v1"] = FAMILY
    recommended_tool_call_limit: Literal[600] = 600
    max_turns: Literal[650] = 650
    runs: tuple[Cell, ...] = Field(min_length=32, max_length=32)

    @model_validator(mode="after")
    def matched(self):
        if tuple(c.id for c in self.runs) != tuple(f"{i:02d}" for i in range(1, 33)):
            raise ValueError("interference pilot requires ordered rows01..32")
        for suite, resource in (("core", 2), ("slack", 1)):
            cells = [c for c in self.runs if c.suite == suite]
            actual = {(c.seed, c.horizon, c.coupling, c.resource) for c in cells}
            expected = {
                (s, h, c, resource)
                for s in SEEDS
                for h in ("short", "long")
                for c in ("independent", "coupled")
            }
            if actual != expected or len(cells) != len(expected):
                raise ValueError(f"incomplete or duplicate matched {suite} conditions")
        return self


def cell_report(cell, pilot, kernels):
    ep = generate_episode(
        cell.seed,
        axis_version=2,
        science_family=FAMILY,
        theory_level=0,
        discovery_level=0,
        planning_level=0,
        resource_pressure=cell.resource,
        ontology_options=cell.options().model_dump(),
        verifier_secret="operator-interference-preflight",
    )
    spec = ep.public.investigation.data()
    key = (spec.resolved, cell.coupling)
    if key not in kernels:
        kernels[key] = prove_kernel(spec)
    plan = optimal(spec)
    minimum = scalar_cost(spec)
    baseline = bank_contiguous_distances(spec.resolved, cell.coupling)[encode(spec.target)]
    breaks = minimum_goal_breaks(spec)
    live = qualify_episode(ep)
    selected = selection(cell.seed)
    proof = ep.generation_metadata.investigation_certificate
    checks = {
        **live.checks,
        "independent_optimum": minimum is not None and plan.actions == minimum + 2,
        "independent_restricted_baseline": baseline == scalar_cost(spec, "bank_contiguous"),
        "independent_coordinate_break_minimum": breaks == scalar_minimum_goal_breaks(spec),
        "paired_seed_kernel_and_target": spec.resolved == selected.world
        and spec.target == (selected.short if cell.horizon == "short" else selected.long),
        "complete_transition_checks": kernels[key] == COUNT * SIZE,
        "tool_limit_covers_allowance": 3 * proof["action_budget"] + 20
        <= pilot.recommended_tool_call_limit,
        "horizon_stratum_bound": (
            12 <= minimum <= 20 if cell.horizon == "short" else 30 <= minimum <= 48
        )
        if cell.coupling == "coupled"
        else True,
        "factorization_or_optimal_interleaving": plan.actions
        == sum(independent_bank_minima(spec)) + 2
        if cell.coupling == "independent"
        else baseline is None or minimum < baseline,
        "coupled_coordinate_regression_required": True
        if cell.coupling == "independent"
        else breaks > 0 and scalar_cost(spec, "goal_preserving") is None,
    }
    if not live.passed or not all(checks.values()):
        raise ValueError(f"row{cell.id} failed qualification: {checks}; {live.errors}")
    return {
        **cell.model_dump(mode="json"),
        "checks": checks,
        "target": list(spec.target),
        "resolved": spec.resolved.model_dump(mode="json"),
        "physical_minimum": plan.actions,
        "reference_operations": len(plan.modes),
        "bank_contiguous_operations": baseline,
        "interleaving_gap": None if baseline is None else baseline - minimum,
        "minimum_coordinate_goal_breaks": breaks,
        "kernel_transition_checks": kernels[key],
        "certificate": proof,
        "action_budget": proof["action_budget"],
        "public_evidence_sha256": digest(ep.public.evidence_files),
    }


def validate_pairs(cells):
    groups = {}
    for cell in cells:
        groups.setdefault((cell["seed"], cell["coupling"], cell["resource"]), {})[
            cell["horizon"]
        ] = cell
    for pair in groups.values():
        short, long = pair["short"], pair["long"]
        if short["resolved"] != long["resolved"] or long["reference_operations"] < short[
            "reference_operations"
        ] + (10 if short["coupling"] == "coupled" else 4):
            raise ValueError("short/long pair lacks its shared kernel or required horizon increase")
    for seed in SEEDS:
        for horizon in ("short", "long"):
            pair = [c for c in cells if c["seed"] == seed and c["horizon"] == horizon]
            if len({digest((c["resolved"], c["target"])) for c in pair}) != 1:
                raise ValueError("coupling/budget pairs differ in law or target")


def preflight(pilot: Pilot, output: Path):
    start = perf_counter()
    sources = source_binding()
    report = {
        "version": "interference-preflight-v1",
        "status": "running",
        "matrix_sha256": digest(pilot.model_dump()),
        "sources": sources,
        "empirical_difficulty_calibrated": False,
        "cells": [],
        "scope": "Independent exact costs, bank-contiguous minima, coordinate-goal regression, live public policy and replay. No model results.",
    }
    atomic_json(output, report)
    try:
        kernels = {}
        for cell in pilot.runs:
            report["cells"].append(cell_report(cell, pilot, kernels))
            atomic_json(output, report)
        validate_pairs(report["cells"])
        if source_binding() != sources:
            raise ValueError("implementation changed during preflight")
        report.update(status="passed", seconds=perf_counter() - start)
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise


def export_tasks(pilot: Pilot, report: dict, directory: Path):
    if (
        report.get("version") != "interference-preflight-v1"
        or report.get("status") != "passed"
        or report.get("sources") != source_binding()
        or report.get("matrix_sha256") != digest(pilot.model_dump())
    ):
        raise ValueError("task export requires current successful matrix/source preflight")
    # Recompute numerical and live checks, so missing, forged or edited cell
    # fields cannot be exported merely by asserting a passed status.
    kernels = {}
    expected = [cell_report(cell, pilot, kernels) for cell in pilot.runs]
    if report.get("cells") != expected:
        raise ValueError("preflight cells differ from recomputed qualification")
    validate_pairs(expected)
    directory.mkdir(parents=True, exist_ok=True)
    for suite in ("core", "slack"):
        atomic_json(
            directory / f"nexus-interference-{suite}-tasks.yaml",
            task_config([task_for(c, pilot) for c in pilot.runs if c.suite == suite], pilot),
        )


def task_for(cell: Cell, pilot: Pilot):
    return {
        "name": f"NEXUS interference-{cell.id}",
        "disabled": False,
        "suite": "nexus",
        "category": "interference-pilot",
        "difficulty": "experimental",
        "tags": [pilot.version, pilot.family, cell.suite],
        "prompt": "Complete the live NEXUS mission and return its actual victory receipt. Begin with manifest and observe, then read every listed evidence file. Use only the NEXUS tool; no external Python, source access or solver is available. The laws, prerequisites, map and current register values are public. Track the original carried seal, committed changes and remaining action allowance. A probe previews one operation without committing it. Put every register at its specified target simultaneously and finish in the stated room.",
        "response-result-format": "The actual victory_code and nothing else. No quotes, Markdown or explanation.",
        "tool-selector": {
            "service-inputs": {
                "nexus": {
                    "axis-version": 2,
                    "science-family": FAMILY,
                    "seed": str(cell.seed),
                    "theory-level": 0,
                    "discovery-level": 0,
                    "planning-level": 0,
                    "resource-pressure": cell.resource,
                    "budget-profile": "standard",
                    "ontology-options": json.dumps(
                        cell.options().model_dump(), sort_keys=True, separators=(",", ":")
                    ),
                    "generation-timing": True,
                    "extended-diagnostics": True,
                }
            }
        },
    }
