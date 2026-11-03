"""Operator-only fresh fixtures, matched contrasts and source-bound qualification.

Lives outside src/nexus deliberately: no player-world semantics or historical
runtime digest changes. The release image and report separately bind this script.
No model calls, empirical outcomes or private witness data enter task prompts.
"""

from __future__ import annotations

import argparse
import copy
import json
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace
from typing import Literal

from pydantic import Field, StrictInt, model_validator

from nexus.evaluation import cross_axis, interference, interference_comparison
from nexus.evaluation.artifacts import StrictModel, atomic_json
from nexus.evaluation.budget_diagnostic import science_projection
from nexus.evaluation.coordination import task_config
from nexus.evaluation.discovery import digest
from nexus.evaluation.revision import certificate_witness
from nexus.generator import generate_episode
from nexus.ontology.repair.qualification import source_binding
from nexus.provenance import source_digest

ROOT = Path(__file__).resolve().parents[1]
VERSION = "fresh-world-preflight-v1"
SUITES = ("anchor", "controls", "td", "pr-a", "pr-b")
ANCHORS = ("S05", "S08", "S21", "S22", "S23", "S24")
MODELS = ("astra", "luna", "flash", "grok")
HISTORY = (
    "cross-axis-matrix.json",
    "model-revision-matrix.json",
    "td-cycle-matrix.json",
    "structural-model-matrix.json",
    "budget-diagnostic-matrix.json",
    "interference-matrix.json",
)


class Cell(StrictModel):
    id: str
    suite: Literal["controls", "td", "pr-a", "pr-b"]
    family: Literal["model-revision-v1", "compositional-repair-v1", "stateful-interference-v1"]
    seed: StrictInt = Field(ge=0)
    theory: Literal[0, 3]
    discovery: Literal[0, 5]
    planning: Literal[0, 1]
    resource: Literal[1, 2]
    budget_profile: Literal["standard", "diagnostic-plus6"] = "standard"
    ontology_options: dict[str, str] = Field(default_factory=dict)
    expected_budget: StrictInt | None = None

    def generate(self):
        return generate_episode(
            self.seed,
            axis_version=2,
            science_family=self.family,
            theory_level=self.theory,
            discovery_level=self.discovery,
            planning_level=self.planning,
            resource_pressure=self.resource,
            budget_profile=self.budget_profile,
            ontology_options=self.ontology_options or None,
            verifier_secret="operator-fresh-worlds-only",
        )


def expected_runs():
    """Frozen before live evaluation; seed aliases and old fixtures excluded."""
    cells = []

    def add(**values):
        cells.append(Cell(id=f"F{len(cells) + 1:02d}", **values))

    for seed in (2073, 2178):
        for known in (True, False):
            add(
                suite="controls" if known else "td",
                family="model-revision-v1",
                seed=seed,
                theory=0 if known else 3,
                discovery=0 if known else 5,
                planning=0,
                resource=1,
                expected_budget=64,
                ontology_options={
                    "guidance": "principles",
                    "finish_policy": "recoverable",
                    "consistency_check": "off",
                },
            )
    for seed in (541, 586):
        for known, profile in (
            (True, "standard"),
            (False, "standard"),
            (False, "diagnostic-plus6"),
        ):
            add(
                suite="controls" if known else "td",
                family="compositional-repair-v1",
                seed=seed,
                theory=0 if known else 3,
                discovery=0 if known else 5,
                planning=1,
                resource=1,
                budget_profile=profile,
                expected_budget=8 if known else 30 if profile == "standard" else 36,
            )
    for seed, suite, order in ((107, "pr-a", (2, 1)), (109, "pr-b", (1, 2))):
        for horizon in ("short", "long"):
            for coupling in ("independent", "coupled"):
                for resource in order:
                    add(
                        suite=suite,
                        family="stateful-interference-v1",
                        seed=seed,
                        theory=0,
                        discovery=0,
                        planning=0,
                        resource=resource,
                        ontology_options={"horizon": horizon, "coupling": coupling},
                    )
    return tuple(cells)


class Pilot(StrictModel):
    version: Literal["fresh-world-pilot-v1"] = "fresh-world-pilot-v1"
    recommended_tool_call_limit: Literal[600] = 600
    max_turns: Literal[650] = 650
    evaluation_seed: Literal["nexus-cross-axis-pilot-v1"] = "nexus-cross-axis-pilot-v1"
    runs: tuple[Cell, ...]

    @model_validator(mode="after")
    def inventory(self):
        if self.runs != expected_runs():
            raise ValueError("fresh-world v1 requires the complete frozen 26-row inventory")
        return self


def bindings():
    return {
        "source_sha256": source_digest(),
        "sources": source_binding(),
        "operator_source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "history_sha256": {
            name: sha256((ROOT / "docs" / name).read_bytes()).hexdigest() for name in HISTORY
        },
    }


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def revision_details(ep):
    from nexus.ontology.revision.inference import Belief
    from nexus.ontology.revision.laws import class_id
    from nexus.ontology.revision.proof import prove_no_three_reading_certificate
    from nexus.ontology.revision.qualification import audit

    spec, truth = ep.public.investigation.data(), ep.investigation_truth.data()
    details = audit(spec, truth)
    c = details["minimum_reading_only_certificate"]
    length = (
        0
        if c == 0
        else next(
            i for i, n in enumerate(details["all_queries_through_length_closure"], 1) if n == 1
        )
    )
    witness = certificate_witness(ep, details["certificate_queries"])
    require(witness == details["minimum_supported_actions"], "revision certificate witness differs")
    lower = (
        None
        if c < 4
        else prove_no_three_reading_certificate(Belief(spec).mask, class_id(truth.program))
    )
    return {
        "behavior_class": class_id(truth.program),
        "minimum_reading_certificate": c,
        "identifying_query_horizon": length,
        "minimum_supported_actions": witness,
        "independent_no_three_reading_certificate": lower,
        "scope": "Actual-outcome reading certificate, not a worst-case cognitive depth bound.",
    }


def qualify_td(cell, ep):
    row, session = cross_axis._live_smoke(cell, ep)
    if cell.family == "model-revision-v1":
        details = revision_details(ep)
        if cell.id.startswith("F") and cell.theory == 3:
            require(
                details["minimum_reading_certificate"] >= 4
                and details["identifying_query_horizon"] >= 4,
                "fresh revision fixture misses certificate/horizon admission",
            )
    else:
        details = cross_axis._repair_details(cell, ep, session)
        details["scope"] = (
            "Reading-only intervention/context obstructions concern the undisclosed prior; "
            "the disclosed supplied-repair condition is an execution control."
        )
    return {**row, "qualification": details}, session


def fingerprint(family, seed):
    """Behavior/mission identity, not merely a numeric seed or generated episode ID."""
    if family == "model-revision-v1":
        from nexus.ontology.revision.laws import class_id

        cell = next(c for c in expected_runs() if c.family == family)
        return str(
            class_id(
                cell.model_copy(update={"seed": seed}).generate().investigation_truth.data().program
            )
        )
    if family == "compositional-repair-v1":
        from nexus.ontology.compositional.laws import population, rows

        index = seed % len(population())
        return digest(([r[index] for r in rows()], population()[index][1]))
    from nexus.ontology.interference.generation import selection

    selected = selection(seed)
    return digest(selected.world.model_dump())


def novelty(pilot):
    history = {name: json.loads((ROOT / "docs" / name).read_text()) for name in HISTORY}
    seeds = {
        "model-revision-v1": {
            c["seed"]
            for name, key in (
                ("model-revision-matrix.json", "runs"),
                ("td-cycle-matrix.json", "cases"),
            )
            for c in history[name][key]
            if c.get("family", "model-revision-v1") == "model-revision-v1"
        },
        "compositional-repair-v1": {
            c["seed"]
            for name in ("structural-model-matrix.json", "budget-diagnostic-matrix.json")
            for c in history[name]["runs"]
        },
        "stateful-interference-v1": {
            c["seed"] for c in history["interference-matrix.json"]["runs"]
        },
    }
    result = {}
    for family, old_seeds in seeds.items():
        old_seeds.update(
            c["seed"] for c in history["cross-axis-matrix.json"]["runs"] if c["family"] == family
        )
        selected = sorted({c.seed for c in pilot.runs if c.family == family})
        old = {fingerprint(family, seed) for seed in old_seeds}
        new = [fingerprint(family, seed) for seed in selected]
        require(
            len(set(new)) == 2 and not set(new) & old,
            f"{family} fresh worlds alias each other or a historical fixture",
        )
        result[family] = {
            "selected_seeds": selected,
            "identities": new,
            "historical_seeds_checked": sorted(old_seeds),
            "distinct_from_history_and_each_other": True,
        }
    return result


def matched_contrasts(pilot, episodes, sessions):
    result = []

    def add(cells, kind, checks, interpretation):
        require(all(checks.values()), f"failed {kind} contrast {[c.id for c in cells]}")
        result.append(
            {
                "ids": [c.id for c in cells],
                "kind": kind,
                "checks": checks,
                "interpretation": interpretation,
            }
        )

    for family in ("model-revision-v1", "compositional-repair-v1"):
        for seed in sorted({c.seed for c in pilot.runs if c.family == family}):
            cells = [c for c in pilot.runs if c.family == family and c.seed == seed]
            a, b = (episodes[c.id] for c in cells[:2])
            checks = {"same_physics": cross_axis._same_physics(a, b)}
            if family == "model-revision-v1":
                checks["same_64_action_allowance"] = (
                    a.generation_metadata.action_budget == b.generation_metadata.action_budget == 64
                )
            add(
                cells[:2],
                "disclosure-control",
                checks,
                "Revision changes T/D together at fixed budget; repair supplies a solution and "
                "changes 8 to 30 actions. Neither isolates a numeric T or D effect.",
            )
            if len(cells) == 3:
                a, b = (episodes[c.id] for c in cells[1:])
                add(
                    cells[1:],
                    "resource",
                    {
                        "same_science_except_budget": science_projection(a)
                        == science_projection(b),
                        "same_reference_actions": [r.action for r in sessions[cells[1].id].trace]
                        == [r.action for r in sessions[cells[2].id].trace],
                        "same_reference_events": [r.events for r in sessions[cells[1].id].trace]
                        == [r.events for r in sessions[cells[2].id].trace],
                        "30_36_allowances": (
                            a.generation_metadata.action_budget,
                            b.generation_metadata.action_budget,
                        )
                        == (30, 36),
                    },
                    "Same repair science and physics; only the action allowance changes.",
                )
    pr = [c for c in pilot.runs if c.family == "stateful-interference-v1"]
    for seed in (107, 109):
        for horizon in ("short", "long"):
            for coupling in ("independent", "coupled"):
                cells = [
                    c
                    for c in pr
                    if c.seed == seed
                    and c.ontology_options == {"horizon": horizon, "coupling": coupling}
                ]
                a, b = (episodes[c.id] for c in cells)
                add(
                    cells,
                    "resource",
                    {
                        "same_science_except_budget": science_projection(a)
                        == science_projection(b),
                    },
                    "Only the disclosed action allowance differs: exact minimum versus added slack.",
                )
        for varying, fixed_values in (
            ("horizon", ("independent", "coupled")),
            ("coupling", ("short", "long")),
        ):
            other = "coupling" if varying == "horizon" else "horizon"
            for fixed in fixed_values:
                for resource in (1, 2):
                    cells = [
                        c
                        for c in pr
                        if c.seed == seed
                        and c.resource == resource
                        and c.ontology_options[other] == fixed
                    ]
                    a, b = (episodes[c.id].public.investigation.data() for c in cells)
                    checks = {"same_resolved_law_coefficients": a.resolved == b.resolved}
                    if varying == "coupling":
                        checks["same_target"] = a.target == b.target
                    else:
                        costs = [
                            episodes[c.id].generation_metadata.investigation_certificate[
                                "minimum_operations"
                            ]
                            for c in cells
                        ]
                        checks["longer_exact_horizon"] = costs[1] >= costs[0] + (
                            10 if fixed == "coupled" else 4
                        )
                    add(
                        cells,
                        varying,
                        checks,
                        "Horizon changes target on one kernel; coupling changes dependency laws "
                        "at one target. The resource rule is fixed, absolute budgets may differ. "
                        "These are structural contrasts, not fixed-compute causal effects.",
                    )
    return result


def task_for(cell, pilot):
    if cell.family == "stateful-interference-v1":
        task = interference.task_for(
            interference.Cell(
                id=cell.id,
                suite="core" if cell.resource == 2 else "slack",
                seed=cell.seed,
                resource=cell.resource,
                **cell.ontology_options,
            ),
            SimpleNamespace(version=pilot.version, family=cell.family),
        )
    else:
        task = cross_axis.task_for(cell, pilot)
    task.update(
        name=f"NEXUS fresh-{cell.id}",
        category="fresh-worlds",
        tags=[pilot.version, cell.family, cell.suite],
    )
    return task


def anchor_cells():
    cells = {c.id: c for c in cross_axis.expected_runs()}
    return tuple(cells[key] for key in ANCHORS)


def tasks(pilot):
    original = cross_axis.Pilot.model_validate_json(
        (ROOT / "docs/cross-axis-matrix.json").read_text()
    )
    return {
        suite: task_config(
            [cross_axis.task_for(c, original) for c in anchor_cells()]
            if suite == "anchor"
            else [task_for(c, pilot) for c in pilot.runs if c.suite == suite],
            pilot,
        )
        for suite in SUITES
    }


@lru_cache(maxsize=2)
def _qualified(pilot_json, binding_json):
    from nexus.ontology.revision.proof import prove

    pilot = Pilot.model_validate_json(pilot_json)
    start_binding = json.loads(binding_json)
    rows, episodes, sessions, kernels = [], {}, {}, {}
    independent = {
        "revision": {key: value for key, value in prove().items() if key != "seconds"},
        "compositional": cross_axis.compositional_conformance(),
    }
    for cell in (*anchor_cells(), *pilot.runs):
        episode = cell.generate()
        episodes[cell.id] = episode
        if cell.family == "stateful-interference-v1":
            row = interference_comparison.structural_cell(
                interference.Cell(
                    id=cell.id,
                    suite="core" if cell.resource == 2 else "slack",
                    seed=cell.seed,
                    resource=cell.resource,
                    **cell.ontology_options,
                ),
                SimpleNamespace(family=cell.family, recommended_tool_call_limit=600),
                kernels,
            )
            row = {
                "qualification": row,
                "action_budget": row["action_budget"],
                "reference_action_upper": row["physical_minimum"],
            }
        else:
            row, sessions[cell.id] = qualify_td(cell, episode)
        rows.append({**cell.model_dump(mode="json"), **row})
    fresh = novelty(pilot)
    contrasts = matched_contrasts(pilot, episodes, sessions)
    require(bindings() == start_binding, "source or history changed during qualification")
    return json.dumps(
        {
            "version": VERSION,
            "status": "passed",
            **start_binding,
            "matrix_sha256": digest(pilot.model_dump()),
            "cells": rows,
            "independent_conformance": independent,
            "novelty": fresh,
            "scientific_contrasts": contrasts,
            "inventory": {"anchor": 6, "fresh": 26, "controls": 4, "td": 6, "pr-a": 8, "pr-b": 8},
            "empirical_difficulty_calibrated": False,
            "scope": "Two purpose-selected fresh seeds per family, no live outcomes used for "
            "selection. Distinct behavior classes/repair observation and acceptance signatures/PR "
            "kernels checked against committed historical matrices; not a random population sample "
            "or a proof of nonisomorphism. Reading certificates are not cognitive depth measures.",
        },
        sort_keys=True,
    )


def qualified(pilot):
    current = bindings()
    report = json.loads(_qualified(pilot.model_dump_json(), json.dumps(current, sort_keys=True)))
    require(bindings() == current, "source changed while retrieving qualification")
    return report


def preflight(pilot, output):
    started = perf_counter()
    running = {"version": VERSION, "status": "running", "matrix_sha256": digest(pilot.model_dump())}
    atomic_json(output, running)
    try:
        report = qualified(pilot)
        report["seconds"] = perf_counter() - started
        atomic_json(output, report)
        return report
    except Exception as exc:
        atomic_json(
            output, {**running, "status": "blocked", "error": f"{type(exc).__name__}: {exc}"}
        )
        raise


def validate_report(pilot, report):
    actual = copy.deepcopy(report)
    actual.pop("seconds", None)
    require(actual == qualified(pilot), "fresh-world proof differs from current recomputation")


def export_tasks(pilot, report, directory):
    validate_report(pilot, report)
    directory.mkdir(parents=True, exist_ok=True)
    for suite, value in tasks(pilot).items():
        atomic_json(directory / f"nexus-fresh-world-{suite}-tasks.yaml", value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=ROOT / "docs/fresh-world-matrix.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tasks-output", type=Path)
    args = parser.parse_args()
    pilot = Pilot.model_validate_json(args.matrix.read_text())
    report = preflight(pilot, args.output)
    if args.tasks_output:
        export_tasks(pilot, report, args.tasks_output)
    print(f"Fresh-world preflight passed: {len(report['cells'])} rows; no model calls")


if __name__ == "__main__":
    main()
