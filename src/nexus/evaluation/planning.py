"""Bounded matched P/R pilot; qualification is independent of live model outcomes."""

from time import perf_counter
from typing import Literal

from pydantic import Field, StrictInt, model_validator

from nexus.evaluation.artifacts import StrictModel, atomic_json
from nexus.evaluation.discovery import digest
from nexus.generator import generate_episode, qualify_episode
from nexus.ontology.planning.planner import optimal, science_shortest_cost
from nexus.ontology.planning.proof import all_world_policy, physical_minimum
from nexus.ontology.repair.qualification import source_binding
from nexus.ontology.stateful.proof import prove_kernel

PROFILES = ((0, 0, 2), (0, 1, 2), (0, 2, 2), (0, 3, 2), (0, 3, 1), (3, 0, 2), (3, 3, 2), (3, 3, 1))


class Cell(StrictModel):
    id: str
    seed: StrictInt
    theory: Literal[0, 3]
    discovery: Literal[5] = 5
    planning: Literal[0, 1, 2, 3]
    resource: Literal[1, 2]


class Pilot(StrictModel):
    version: Literal["planning-resource-pilot-v1"]
    family: Literal["stateful-planning-v1"] = "stateful-planning-v1"
    external_python: Literal[False] = False
    fresh_context_per_execution: Literal[True] = True
    recommended_tool_call_limit: Literal[600] = 600
    max_turns: Literal[650] = 650
    runs: tuple[Cell, ...] = Field(min_length=16, max_length=16)

    @model_validator(mode="after")
    def matched(self):
        if tuple(c.id for c in self.runs) != tuple(f"{i:02d}" for i in range(1, 17)):
            raise ValueError("P/R pilot requires ordered rows01..16")
        for offset in (0, 8):
            block = self.runs[offset : offset + 8]
            if (
                len({c.seed for c in block}) != 1
                or tuple((c.theory, c.planning, c.resource) for c in block) != PROFILES
            ):
                raise ValueError("each P/R block must share one seed and the controlled profiles")
        if self.runs[0].seed == self.runs[8].seed:
            raise ValueError("two distinct physical fixtures are required")
        return self


def preflight(pilot, output):
    start = perf_counter()
    report = {
        "version": "planning-resource-preflight-v1",
        "status": "running",
        "matrix_sha256": digest(pilot.model_dump()),
        "sources": source_binding(),
        "empirical_difficulty_calibrated": False,
        "cells": [],
        "selection_scope": "Operator-selected planning-tradeoff cases; not a random population estimate. Keep seeds, source, reference plans and this report private from players.",
    }
    atomic_json(output, report)
    try:
        report["kernel"] = prove_kernel()
        for cell in pilot.runs:
            ep = generate_episode(
                cell.seed,
                axis_version=2,
                science_family=pilot.family,
                theory_level=cell.theory,
                discovery_level=5,
                planning_level=cell.planning,
                resource_pressure=cell.resource,
                verifier_secret="operator-pr-preflight",
            )
            spec, world = ep.public.investigation.data(), ep.investigation_truth.data()
            joint = optimal(world, spec.target, cell.planning)
            baseline = science_shortest_cost(world, spec.target, cell.planning)
            live = qualify_episode(ep)
            checks = {
                **live.checks,
                "independent_optimum": joint.actions
                == physical_minimum(world, spec.target, cell.planning),
                "routing_baseline_bound": joint.actions <= baseline,
                "tool_limit_covers_reference": ep.generation_metadata.recommended_tool_call_limit
                <= pilot.recommended_tool_call_limit,
            }
            if cell.planning == 3:
                checks["strict_joint_planning_tradeoff"] = joint.actions < baseline
            prior = all_world_policy(spec.target, cell.planning) if cell.theory == 3 else None
            if not all(checks.values()) or not live.passed:
                raise ValueError(f"row{cell.id} failed: {checks}, {live.errors}")
            report["cells"].append(
                {
                    **cell.model_dump(),
                    "checks": checks,
                    "target": spec.target,
                    "physical_minimum": joint.actions,
                    "joint_plan_operations": len(joint.modes),
                    "joint_plan_moves": joint.moves,
                    "science_minimum_operations": optimal(world, spec.target, 0).actions - 2,
                    "cheapest_routed_science_shortest": baseline,
                    "reference_actions_realized": live.metrics["actions"],
                    "certificate": ep.generation_metadata.investigation_certificate,
                    "all_world_reference": prior,
                }
            )
            atomic_json(output, report)
        if source_binding() != report["sources"]:
            raise ValueError("implementation changed during preflight")
        report.update(
            status="passed",
            seconds=perf_counter() - start,
            scope="Exact known-law spatial minima, all-prior public-policy bounds, live wins and replay. No model evaluations or monotonic P-level difficulty claim.",
        )
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise


def export_tasks(pilot, report, output):
    """JSON is valid YAML; require the exact successful matrix/source preflight."""
    if (
        report.get("version") != "planning-resource-preflight-v1"
        or report.get("status") != "passed"
        or report.get("matrix_sha256") != digest(pilot.model_dump())
        or report.get("sources") != source_binding()
        or len(report.get("cells", ())) != len(pilot.runs)
    ):
        raise ValueError("task export requires a current successful P/R preflight")
    kernel = report.get("kernel", {})
    if (
        kernel.get("independent_transition_checks") != 256 * 4 * 626
        or kernel.get("proper_closed_coordinate_partitions") != 0
    ):
        raise ValueError("task export requires complete physics kernel evidence")
    required = {
        "compiled_contract",
        "public_policy_supported_win",
        "within_reference_bound",
        "exact_replay",
        "independent_optimum",
        "routing_baseline_bound",
        "tool_limit_covers_reference",
    }
    for cell, result in zip(pilot.runs, report["cells"], strict=True):
        checks = required | ({"strict_joint_planning_tradeoff"} if cell.planning == 3 else set())
        if (
            any(result.get(k) != v for k, v in cell.model_dump().items())
            or set(result.get("checks", {})) != checks
            or any(result["checks"][key] is not True for key in checks)
        ):
            raise ValueError("task export requires ordered matching cells and all admission checks")
        positive_fields = (
            "physical_minimum",
            "joint_plan_operations",
            "science_minimum_operations",
            "cheapest_routed_science_shortest",
            "reference_actions_realized",
        )
        if any(type(result.get(key)) is not int or result[key] < 1 for key in positive_fields):
            raise ValueError("task export requires complete positive action costs")
        certificate = result.get("certificate") or {}
        reference = certificate.get("reference_action_upper")
        if type(reference) is not int or reference < 1:
            raise ValueError("task export requires a positive certified reference bound")
        expected_kind = (
            "exact-known-law-optimum" if cell.theory == 0 else "public-policy-upper-bound"
        )
        slack = max(6, (reference + 1) // 2) if cell.resource == 1 else 0
        if (
            certificate.get("reference_kind") != expected_kind
            or certificate.get("family") != pilot.family
            or certificate.get("action_budget") != reference + slack
            or certificate.get("resource_allowance") != slack
            or result["reference_actions_realized"] > reference
            or (cell.theory == 0 and reference != result["physical_minimum"])
        ):
            raise ValueError("task export requires consistent reference scope and budget")
        if cell.theory == 3:
            proof = result.get("all_world_reference") or {}
            lower, upper = proof.get("minimum_actions"), proof.get("maximum_actions")
            if type(lower) is not int or type(upper) is not int or not 0 < lower <= upper:
                raise ValueError("task export requires positive T3 realized cost bounds")
            if (
                proof.get("worlds") != 256
                or proof.get("all_finishes_supported") is not True
                or proof.get("reference_bound_exact_for_this_policy") is not True
                or proof.get("policy_optimality_proved") is not False
                or upper != reference
            ):
                raise ValueError("task export requires complete T3 all-prior policy evidence")
    prompt = (
        "Complete the live NEXUS mission and return its actual victory receipt. "
        "Begin with manifest and observe, then read every listed evidence file. "
        "Use only the NEXUS tool for in-world observations and actions. No external "
        "Python, source access or solver is available. Finite hypothesis enumeration "
        "is valid. Track the carried seal, committed changes, location and remaining "
        "actions. A probe previews one operation without committing it. Satisfy the "
        "full goal, call finish successfully, then return exactly the victory_code."
    )
    tasks = [
        {
            "name": f"NEXUS planning-resource-{c.id}",
            "disabled": False,
            "suite": "nexus",
            "category": "planning-resource-pilot",
            "difficulty": "experimental",
            "tags": [pilot.version, pilot.family],
            "prompt": prompt,
            "response-result-format": "The actual victory_code and nothing else. No quotes, Markdown or explanation.",
            "tool-selector": {
                "service-inputs": {
                    "nexus": {
                        "axis-version": 2,
                        "science-family": pilot.family,
                        "seed": str(c.seed),
                        "theory-level": c.theory,
                        "discovery-level": c.discovery,
                        "planning-level": c.planning,
                        "resource-pressure": c.resource,
                        "budget-profile": "standard",
                        "generation-timing": True,
                        "extended-diagnostics": True,
                    }
                }
            },
        }
        for c in pilot.runs
    ]
    atomic_json(
        output,
        {
            "task-config": {
                "max-turns": pilot.max_turns,
                "validation-rules": {
                    "custom-validator": "nexus-victory",
                    "case-sensitive": True,
                    "ignore-whitespace": False,
                    "trim-lines": False,
                },
                "system-prompt": {
                    "enable-for": "text",
                    "template": "Use NEXUS to complete the live task. Your final answer must match: {{.ResponseResultFormat}}",
                },
                "tool-selector": {
                    "disabled": False,
                    "tools": [
                        {
                            "name": "nexus",
                            "disabled": False,
                            "max-calls": pilot.recommended_tool_call_limit,
                            "timeout": "60s",
                        }
                    ],
                },
                "tasks": tasks,
            }
        },
    )
