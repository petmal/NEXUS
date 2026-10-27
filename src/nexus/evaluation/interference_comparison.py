"""Structural qualification of unchanged v1 worlds for a two-model comparison."""

from pathlib import Path
from time import perf_counter

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.coordination import task_config
from nexus.evaluation.discovery import digest
from nexus.evaluation.interference import Pilot, cell_report, task_for, validate_pairs
from nexus.ontology.interference.generation import selection, specification
from nexus.ontology.interference.planner import actions_for, optimal
from nexus.ontology.interference.structure import metrics, trajectory
from nexus.ontology.interference.structure_proof import scalar_metrics
from nexus.ontology.repair.qualification import source_binding

VERSION = "interference-comparison-preflight-v1"
PREFIX = "interference-comparison"


def structural_cell(cell, pilot, kernels):
    result = cell_report(cell, pilot, kernels)
    admitted = selection(cell.seed)
    spec = specification(
        admitted.world, admitted.short if cell.horizon == "short" else admitted.long, cell.coupling
    )
    values = metrics(spec)
    independently = scalar_metrics(spec)
    checks = {
        "independent_structural_costs": all(
            values[name] == value for name, value in independently.items()
        ),
        "coordinate_metric_matches_original": values["minimum_coordinate_goal_breaks"]
        == result["minimum_coordinate_goal_breaks"],
        "block_cost_ordering": 0
        < values["minimum_machine_blocks"]
        <= values["minimum_machine_blocks_on_optimal_paths"]
        <= result["reference_operations"],
    }
    # Exercise the exact diagnostics emitted by the real runtime at termination.
    from nexus.generator import generate_episode
    from nexus.protocol.session import Session

    episode = generate_episode(
        cell.seed,
        axis_version=2,
        science_family=pilot.family,
        theory_level=0,
        discovery_level=0,
        planning_level=0,
        resource_pressure=cell.resource,
        ontology_options=cell.options().model_dump(),
        verifier_secret="operator-structural-check",
    )
    session = Session(episode)
    for action in actions_for(spec, optimal(spec).modes):
        response = session.act(expected_turn=session.state.turn, action=action)
        if not response.ok:
            raise ValueError("reference trajectory rejected")
    observed = trajectory(spec, session.trace)
    checks["live_structural_diagnostics"] = (
        bool(response.victory_code)
        and observed["success_excess_actions"] == 0
        and observed["first_loss_of_optimality_turn"] is None
        and observed["whole_bank_reopening_operations"]
        >= values["minimum_whole_bank_reopening_operations"]
        and observed["machine_blocks"] >= values["minimum_machine_blocks_on_optimal_paths"]
    )
    if not all(checks.values()):
        raise ValueError(f"row{cell.id} failed structural qualification: {checks}")
    result.update(structural=values, structural_checks=checks, reference_trajectory=observed)
    return result


def preflight(pilot: Pilot, output: Path):
    start = perf_counter()
    sources = source_binding()
    report = {
        "version": VERSION,
        "status": "running",
        "matrix_sha256": digest(pilot.model_dump()),
        "sources": sources,
        "cells": [],
        "empirical_difficulty_calibrated": False,
        "scope": "Unchanged qualified v1 worlds; exact block and whole-bank metrics independently verified. Model settings are in the separately pinned configuration. No new harder world is admitted and no model calls occur.",
    }
    atomic_json(output, report)
    try:
        kernels = {}
        for cell in pilot.runs:
            report["cells"].append(structural_cell(cell, pilot, kernels))
            atomic_json(output, report)
        validate_pairs(report["cells"])
        if source_binding() != sources:
            raise ValueError("implementation changed during structural preflight")
        report.update(status="passed", seconds=perf_counter() - start)
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise


def export_tasks(pilot: Pilot, report: dict, directory: Path):
    if (
        report.get("version") != VERSION
        or report.get("status") != "passed"
        or report.get("sources") != source_binding()
        or report.get("matrix_sha256") != digest(pilot.model_dump())
    ):
        raise ValueError("comparison task export requires current successful qualification")
    kernels = {}
    expected = [structural_cell(cell, pilot, kernels) for cell in pilot.runs]
    if report.get("cells") != expected:
        raise ValueError("comparison proof fields differ from recomputed qualification")
    validate_pairs(expected)
    directory.mkdir(parents=True, exist_ok=True)
    for suite in ("core", "slack"):
        atomic_json(
            directory / f"nexus-{PREFIX}-{suite}-tasks.yaml",
            task_config(
                [task_for(cell, pilot) for cell in pilot.runs if cell.suite == suite], pilot
            ),
        )
