"""Qualified paired coordination tasks; no model calls or difficulty claims."""

import json
from copy import deepcopy
from pathlib import Path
from time import perf_counter
from typing import Literal

from pydantic import Field, StrictInt, model_validator

from nexus.evaluation.artifacts import StrictModel, atomic_json
from nexus.evaluation.discovery import digest
from nexus.generator import generate_episode, qualify_episode
from nexus.ontology.coordination.planner import bank_contiguous_cost, optimal
from nexus.ontology.coordination.proof import (
    independent_bank_minima,
    physical_minimum,
    prove_kernel,
)
from nexus.ontology.coordination.schema import FAMILY, GenerationOptions
from nexus.ontology.repair.qualification import source_binding


class Cell(StrictModel):
    id: str
    suite: Literal["core", "spatial", "slack"]
    seed: StrictInt
    banks: StrictInt = Field(ge=2, le=3)
    registers_per_bank: StrictInt = Field(ge=2, le=3)
    coupling: Literal["independent", "coupled"]
    planning: StrictInt
    resource: StrictInt = Field(ge=1, le=2)

    def options(self):
        return GenerationOptions(
            banks=self.banks,
            registers_per_bank=self.registers_per_bank,
            coupling=self.coupling,
        )


class Pilot(StrictModel):
    version: Literal["coordination-pilot-v1"]
    family: Literal["stateful-coordination-v1"] = FAMILY
    recommended_tool_call_limit: Literal[600] = 600
    max_turns: Literal[650] = 650
    runs: tuple[Cell, ...] = Field(min_length=40, max_length=40)

    @model_validator(mode="after")
    def matched(self):
        if tuple(c.id for c in self.runs) != tuple(f"{i:02d}" for i in range(1, 41)):
            raise ValueError("coordination pilot requires ordered rows01..40")
        seeds = {c.seed for c in self.runs}
        if len(seeds) != 2:
            raise ValueError("exactly two independent seed fixtures are required")
        core = {
            (seed, banks, depth, coupling, 0, 2)
            for seed in seeds
            for banks in (2, 3)
            for depth in (2, 3)
            for coupling in ("independent", "coupled")
        }
        spatial = {
            (seed, 3, 3, coupling, 3, resource)
            for seed in seeds
            for coupling in ("independent", "coupled")
            for resource in (1, 2)
        }
        slack = {(*values[:-1], 1) for values in core}
        for suite, expected in (("core", core), ("spatial", spatial), ("slack", slack)):
            cells = [c for c in self.runs if c.suite == suite]
            actual = {
                (c.seed, c.banks, c.registers_per_bank, c.coupling, c.planning, c.resource)
                for c in cells
            }
            if actual != expected or len(cells) != len(expected):
                raise ValueError(f"incomplete or duplicate matched {suite} conditions")
        return self


def preflight(pilot: Pilot, output: Path):
    start = perf_counter()
    sources = source_binding()
    report = {
        "version": "coordination-preflight-v1",
        "status": "running",
        "matrix_sha256": digest(pilot.model_dump()),
        "sources": sources,
        "empirical_difficulty_calibrated": False,
        "cells": [],
        "scope": "Exact known-law costs and bank-contiguous baselines; no model results.",
    }
    atomic_json(output, report)
    paired = {}
    kernel_checks = {}
    try:
        for cell in pilot.runs:
            ep = generate_episode(
                cell.seed,
                axis_version=2,
                science_family=pilot.family,
                theory_level=0,
                discovery_level=0,
                planning_level=cell.planning,
                resource_pressure=cell.resource,
                ontology_options=cell.options().model_dump(),
                verifier_secret="operator-coordination-preflight",
            )
            spec = ep.public.investigation.data()
            pair_key = (cell.seed, cell.banks, cell.registers_per_bank)
            pair = (spec.resolved, spec.target)
            if pair_key in paired and paired[pair_key] != pair:
                raise ValueError("paired coefficients or targets differ")
            paired[pair_key] = pair
            kernel_key = (*pair_key, cell.coupling)
            if kernel_key not in kernel_checks:
                kernel_checks[kernel_key] = prove_kernel(spec)
            plan = optimal(spec)
            contiguous = bank_contiguous_cost(spec)
            independent_minimum = physical_minimum(spec)
            live = qualify_episode(ep)
            checks = {
                **live.checks,
                "independent_optimum": plan.actions == independent_minimum,
                "restricted_baseline_bound": plan.actions <= contiguous,
                "paired_laws_and_targets": True,
                "complete_transition_checks": kernel_checks[kernel_key]
                == (3 ** (cell.banks * cell.registers_per_bank))
                * cell.banks
                * cell.registers_per_bank,
                "tool_limit_covers_reference": 3 * plan.actions + 20
                <= pilot.recommended_tool_call_limit,
            }
            if cell.planning == 0:
                checks["independent_factorization_or_strict_interleaving_gap"] = (
                    plan.actions == contiguous == sum(independent_bank_minima(spec)) + 2
                    if cell.coupling == "independent"
                    else plan.actions < contiguous
                )
            if not live.passed or not all(checks.values()):
                raise ValueError(f"row{cell.id} failed: {checks}; {live.errors}")
            report["cells"].append(
                {
                    **cell.model_dump(),
                    "checks": checks,
                    "target": spec.target,
                    "resolved": spec.resolved.model_dump(),
                    "physical_minimum": plan.actions,
                    "reference_operations": len(plan.modes),
                    "reference_moves": plan.moves,
                    "bank_contiguous_minimum": contiguous,
                    "interleaving_gap": contiguous - plan.actions,
                    "kernel_transition_checks": kernel_checks[kernel_key],
                    "certificate": ep.generation_metadata.investigation_certificate,
                    "action_budget": ep.public.initial_state.resources.actions_remaining,
                    "public_evidence_sha256": digest(ep.public.evidence_files),
                }
            )
            atomic_json(output, report)
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
        report.get("version") != "coordination-preflight-v1"
        or report.get("status") != "passed"
        or report.get("matrix_sha256") != digest(pilot.model_dump())
        or report.get("sources") != source_binding()
        or len(report.get("cells", ())) != len(pilot.runs)
    ):
        raise ValueError("task export requires the current successful matrix/source preflight")
    for cell, result in zip(pilot.runs, report["cells"], strict=True):
        if any(result.get(k) != v for k, v in cell.model_dump().items()):
            raise ValueError("preflight cell binding differs")
        checks = result.get("checks", {})
        required = {
            "compiled_contract",
            "public_policy_supported_win",
            "exact_reference_actions",
            "exact_replay",
            "independent_optimum",
            "restricted_baseline_bound",
            "paired_laws_and_targets",
            "complete_transition_checks",
            "tool_limit_covers_reference",
        }
        if cell.planning == 0:
            required.add("independent_factorization_or_strict_interleaving_gap")
        if not required <= checks.keys() or any(v is not True for v in checks.values()):
            raise ValueError("preflight did not pass required guarantees")
        minimum = result.get("physical_minimum")
        baseline = result.get("bank_contiguous_minimum")
        allowance = max(6, (minimum + 1) // 2) if type(minimum) is int and cell.resource == 1 else 0
        if (
            type(minimum) is not int
            or minimum < 1
            or type(baseline) is not int
            or baseline < minimum
            or result.get("action_budget") != minimum + allowance
            or result.get("interleaving_gap") != baseline - minimum
        ):
            raise ValueError("preflight cost/budget fields are inconsistent")
        if cell.planning == 0 and (
            (cell.coupling == "independent" and baseline != minimum)
            or (cell.coupling == "coupled" and baseline <= minimum)
        ):
            raise ValueError("preflight lacks the paired P0 gap guarantee")
    directory.mkdir(parents=True, exist_ok=True)
    for suite in ("core", "spatial", "slack"):
        tasks = [task_for(cell, pilot) for cell in pilot.runs if cell.suite == suite]
        atomic_json(directory / f"nexus-coordination-{suite}-tasks.yaml", task_config(tasks, pilot))


def export_repeat_tasks(directory: Path):
    """Two further explicit attempts per historical row, after fresh qualification."""
    from nexus.evaluation import planning

    directory.mkdir(parents=True, exist_ok=True)
    pilot = planning.Pilot.model_validate_json(
        Path("docs/planning-resource-matrix.json").read_text()
    )
    report = planning.preflight(pilot, directory / "planning-repeat-preflight.json")
    original_path = directory / "qualified-planning-tasks.yaml"
    planning.export_tasks(pilot, report, original_path)
    original = json.loads(original_path.read_text())
    by_row = {t["name"].rsplit("-", 1)[1]: t for t in original["task-config"]["tasks"]}
    repeated = []
    for attempt, rows in ((3, ("06", "07", "15", "08", "16")), (4, ("16", "08", "15", "07", "06"))):
        for row in rows:
            task = deepcopy(by_row[row])
            task["name"] += f"-repeat-{attempt:02d}"
            task["tags"] += ["planning-resource-repeat-v1", f"attempt-{attempt:02d}"]
            repeated.append(task)
    original["task-config"]["tasks"] = repeated
    atomic_json(directory / "nexus-coordination-repeat-tasks.yaml", original)
    return original


def task_config(tasks: list, pilot: Pilot):
    return {
        "task-config": {
            "max-turns": pilot.max_turns,
            "tool-selector": {
                "tools": [{"name": "nexus", "max-calls": pilot.recommended_tool_call_limit}]
            },
            "validation-rules": {"custom-validator": "nexus-victory"},
            "tasks": tasks,
        }
    }


def task_for(cell: Cell, pilot: Pilot):
    return {
        "name": f"NEXUS coordination-{cell.id}",
        "disabled": False,
        "suite": "nexus",
        "category": "coordination-pilot",
        "difficulty": "experimental",
        "tags": [pilot.version, pilot.family, cell.suite],
        "prompt": (
            "Complete the live NEXUS mission and return its actual victory receipt. "
            "Begin with manifest and observe, then read every listed evidence file. "
            "Use only the NEXUS tool; no external Python, source access or solver is available. "
            "The laws, map and current register values are public. Track the original carried "
            "seal, machine locations, committed changes and remaining action allowance. "
            "A probe previews one operation without committing it. Put every register at its "
            "specified target simultaneously, return to the stated finish room, and finish."
        ),
        "response-result-format": "The actual victory_code and nothing else. No quotes, Markdown or explanation.",
        "tool-selector": {
            "service-inputs": {
                "nexus": {
                    "axis-version": 2,
                    "science-family": pilot.family,
                    "seed": str(cell.seed),
                    "theory-level": 0,
                    "discovery-level": 0,
                    "planning-level": cell.planning,
                    "resource-pressure": cell.resource,
                    "ontology-options": json.dumps(
                        cell.options().model_dump(), sort_keys=True, separators=(",", ":")
                    ),
                    "budget-profile": "standard",
                    "generation-timing": True,
                    "extended-diagnostics": True,
                }
            }
        },
    }
