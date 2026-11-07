"""Source-bound smaller-model screen with unchanged historical world mechanics.

This operator-only module never calls a model. Full historical qualification is
retained even when only a subset is selected for live evaluation. Neither the
matrix, this report nor private reference trajectories belong in player inputs.
"""

from __future__ import annotations

import json
from functools import lru_cache
from hashlib import sha256
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Literal

from pydantic import Field, StrictInt, model_validator

from nexus.presentation import evidence_binding, evidence_files
from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation import interference, interference_comparison, planning, stateful, td_cycle
from nexus.evaluation.artifacts import StrictModel, atomic_json
from nexus.evaluation.budget_diagnostic import science_projection
from nexus.evaluation.coordination import task_config
from nexus.evaluation.discovery import digest
from nexus.generator import generate_episode, qualify_episode
from nexus.ontology.repair.qualification import source_binding
from nexus.protocol.session import Session
from nexus.provenance import source_digest

VERSION = "cross-axis-preflight-v1"
SUITES = ("canary-core", "canary-slack", "rerun-core", "rerun-slack", "smoke-td", "smoke-pr")
DEPENDENCIES = {
    "interference": "interference-matrix.json",
    "stateful": "stateful-matrix.json",
    "revision": "td-cycle-matrix.json",
    "planning": "planning-resource-matrix.json",
    "structural": "structural-model-matrix.json",
    "budget": "budget-diagnostic-matrix.json",
}
PROMPT = (
    "Complete the live NEXUS mission and return its actual victory receipt. "
    "Begin with manifest and observe, then read every listed evidence file. "
    "Use the disclosed action contract and the episode's own instructions to learn "
    "the controls, available evidence, mission and remaining action allowance. "
    "Use only the NEXUS tool; no external Python, source access or solver is available. "
    "Track observations, committed changes and resources. Satisfy the full mission, "
    "call finish successfully, and return exactly the actual victory_code."
)


class Cell(StrictModel):
    id: str
    suite: Literal[
        "canary-core", "canary-slack", "rerun-core", "rerun-slack", "smoke-td", "smoke-pr"
    ]
    family: Literal[
        "stateful-interference-v1",
        "stateful-discovery-v1",
        "model-revision-v1",
        "stateful-planning-v1",
        "compositional-repair-v1",
    ]
    seed: StrictInt = Field(ge=0)
    theory: Literal[0, 3]
    discovery: Literal[0, 5]
    planning: Literal[0, 1, 2, 3]
    resource: Literal[0, 1, 2]
    budget_profile: Literal["standard", "diagnostic-plus6"] = "standard"
    ontology_options: dict[str, str] = Field(default_factory=dict)
    source_matrix: str
    source_id: str
    source_variant: Literal["original", "known-control", "baseline"] = "original"
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
            verifier_secret="operator-cross-axis-preflight",
        )


def expected_runs() -> tuple[Cell, ...]:
    """Frozen scientific inventory; changes require an explicit source revision."""
    cells = []
    for index in range(32):
        offset = index % 16
        seed = (67, 79, 101, 103)[offset // 4]
        horizon = "short" if offset % 4 < 2 else "long"
        coupled = offset % 4 in ((1, 2) if offset // 4 % 2 == 0 else (0, 3))
        original = "core" if index < 16 else "slack"
        cells.append(
            Cell(
                id=f"interference-{index + 1:02d}",
                suite=f"{'canary' if 8 <= offset <= 11 else 'rerun'}-{original}",
                family="stateful-interference-v1",
                seed=seed,
                theory=0,
                discovery=0,
                planning=0,
                resource=2 if index < 16 else 1,
                ontology_options={
                    "horizon": horizon,
                    "coupling": "coupled" if coupled else "independent",
                },
                source_matrix="interference",
                source_id=f"{index + 1:02d}",
            )
        )
    for index, (t, d, r) in enumerate(((0, 0, 1), (0, 5, 1), (3, 5, 1), (3, 5, 0)), 1):
        cells.append(
            Cell(
                id=f"S{index:02d}",
                suite="smoke-td",
                family="stateful-discovery-v1",
                seed=229,
                theory=t,
                discovery=d,
                planning=1,
                resource=r,
                source_matrix="stateful",
                source_id=f"{index + 1:02d}",
                expected_budget=64 if r else None,
            )
        )
    for index, (seed, source, guidance) in enumerate(
        (
            (5866, "12", "principles"),
            (468, "11", "provisional"),
            (6467, "03", "principles"),
            (5866, "01", "principles"),
            (1101, "10", "provisional"),
            (438, "04", "principles"),
            (3, "06", "principles"),
            (1185, "07", "principles"),
        ),
        5,
    ):
        cells.append(
            Cell(
                id=f"S{index:02d}",
                suite="smoke-td",
                family="model-revision-v1",
                seed=seed,
                theory=0 if index == 5 else 3,
                discovery=0 if index == 5 else 5,
                planning=0,
                resource=1,
                expected_budget=64,
                ontology_options={
                    "guidance": guidance,
                    "finish_policy": "recoverable",
                    "consistency_check": "off",
                },
                source_matrix="revision",
                source_id=source,
                source_variant="baseline",
            )
        )
    for index, (seed, p, r, source, budget) in enumerate(
        (
            (21, 0, 2, "01", 11),
            (21, 1, 2, "02", 16),
            (21, 2, 2, "03", 20),
            (21, 3, 2, "04", 22),
            (21, 3, 1, "05", 33),
            (31, 0, 2, "09", 10),
            (31, 3, 2, "12", 19),
            (31, 3, 1, "13", 29),
        ),
        13,
    ):
        cells.append(
            Cell(
                id=f"S{index:02d}",
                suite="smoke-pr",
                family="stateful-planning-v1",
                seed=seed,
                theory=0,
                discovery=5,
                planning=p,
                resource=r,
                source_matrix="planning",
                source_id=source,
                expected_budget=budget,
            )
        )
    for index, (seed, known, profile, source, source_id, budget) in enumerate(
        (
            (438, True, "standard", "structural", "structural-05", 8),
            (438, False, "standard", "structural", "structural-05", 30),
            (438, False, "diagnostic-plus6", "budget", "budget-02", 36),
            (493, False, "diagnostic-plus6", "budget", "budget-03", 36),
        ),
        21,
    ):
        cells.append(
            Cell(
                id=f"S{index:02d}",
                suite="smoke-td",
                family="compositional-repair-v1",
                seed=seed,
                theory=0 if known else 3,
                discovery=0 if known else 5,
                planning=1,
                resource=1,
                budget_profile=profile,
                expected_budget=budget,
                source_matrix=source,
                source_id=source_id,
                source_variant="known-control" if known else "original",
            )
        )
    return tuple(cells)


class Pilot(StrictModel):
    version: Literal["cross-axis-pilot-v1"] = "cross-axis-pilot-v1"
    external_python: Literal[False] = False
    fresh_context_per_execution: Literal[True] = True
    recommended_tool_call_limit: Literal[600] = 600
    max_turns: Literal[650] = 650
    dependency_matrix_sha256: dict[str, str]
    runs: tuple[Cell, ...] = Field(min_length=56, max_length=56)

    @model_validator(mode="after")
    def inventory(self):
        if self.runs != expected_runs():
            raise ValueError(
                "cross-axis screen requires the frozen ordered32 reruns and24 smoke rows"
            )
        if set(self.dependency_matrix_sha256) != set(DEPENDENCIES) or any(
            len(value) != 64 or any(c not in "0123456789abcdef" for c in value)
            for value in self.dependency_matrix_sha256.values()
        ):
            raise ValueError("all six exact historical matrix byte digests are required")
        return self


def dependency_paths() -> dict[str, Path]:
    # The image keeps operator matrices under /app/docs; local runs use repo cwd.
    roots = (Path.cwd() / "docs", Path(__file__).resolve().parents[3] / "docs")
    for root in roots:
        if all((root / name).is_file() for name in DEPENDENCIES.values()):
            return {key: root / name for key, name in DEPENDENCIES.items()}
    raise ValueError("complete operator dependency matrices are required in docs/")


def _dependencies(pilot):
    paths = dependency_paths()
    texts = {key: path.read_text(encoding="utf-8") for key, path in paths.items()}
    actual = {key: sha256(paths[key].read_bytes()).hexdigest() for key in paths}
    if actual != pilot.dependency_matrix_sha256:
        raise ValueError("historical dependency matrix bytes differ from the selected matrix")
    return texts


def _stable(value):
    """Exclude only elapsed-time measurements, never a scientific/proof field."""
    if isinstance(value, dict):
        return {
            key: _stable(item)
            for key, item in value.items()
            if key not in {"seconds", "generation_seconds"}
        }
    if isinstance(value, (tuple, list)):
        return [_stable(item) for item in value]
    return value


def _require(ok, message):
    if not ok:
        raise ValueError(message)


def _scalar_reading(world, mode, point, trims):
    topology, f, g, h, changed, replacement = world
    operators = (lambda x, y: x + y, lambda x, y: x - y, lambda x, y: x * y, lambda x, y: x * x + y)
    selected = [f, g, h]
    if mode:
        selected[changed] = replacement
    x, y, z = point
    a, b, c, d = trims
    first = (operators[selected[0]](x, y) + a) % 3
    second = (operators[selected[1]](y if topology == 1 else first, z) + b) % 3
    final = (
        operators[selected[2]](second, x)
        if topology == 0
        else operators[selected[2]](first, second)
    )
    return (final + c + mode * d) % 3


def compositional_conformance():
    """Current independent arithmetic/support premises of the factored argument.

    This is finite executable evidence, not a proof of every Python state/history.
    Each selected live episode separately checks runtime acceptance and replay.
    """
    from nexus.ontology.compositional.laws import (
        MISSION,
        QUERIES,
        REPAIRS,
        accepted,
        population,
        reading,
    )

    independent = []
    raw_worlds = 0
    for world in product(range(3), range(4), range(4), range(4), range(3), range(4)):
        if world[5] == world[world[4] + 1]:
            continue
        raw_worlds += 1
        wins = sum(
            1 << i
            for i, repair in enumerate(REPAIRS)
            if all(_scalar_reading(world, mode, point, repair) == 0 for mode, point in MISSION)
        )
        if wins:
            independent.append((world, wins))
    _require(
        independent == [(tuple(w), wins) for w, wins in population()],
        "independent compositional support differs",
    )
    queries = acceptances = 0
    for world, wins in population():
        for i, repair in enumerate(REPAIRS):
            _require(
                accepted(world, repair) == bool(wins >> i & 1), "compositional acceptance differs"
            )
            acceptances += 1
        for mode, point, (a, b) in QUERIES:
            baseline = _scalar_reading(world, mode, point, (a, b, 0, 0))
            for c, d in product(range(3), repeat=2):
                observed = reading(world, (mode, *point, a, b, c, d))
                _require(
                    observed == _scalar_reading(world, mode, point, (a, b, c, d)),
                    "independent compositional reading differs",
                )
                _require(
                    (observed - c - mode * d) % 3 == baseline, "normalized query loses information"
                )
                queries += 1
    return {
        "passed": True,
        "raw_worlds": raw_worlds,
        "admitted_worlds": len(independent),
        "independent_acceptance_checks": acceptances,
        "independent_raw_reading_checks": queries,
        "scope": "Complete grammar support, all accepted repairs and raw/normalized arithmetic; selected live witness and acceptance checks below. Factored conformance, not exhaustive runtime histories.",
    }


def _live_smoke(cell, episode):
    policies = {
        "stateful-discovery-v1": "nexus.ontology.stateful.policy",
        "model-revision-v1": "nexus.ontology.discovery.policy",
        "stateful-planning-v1": "nexus.ontology.planning.policy",
        "compositional-repair-v1": "nexus.ontology.compositional.policy",
    }
    from importlib import import_module

    session = Session(episode)
    result = import_module(policies[cell.family]).public_policy(
        session, evidence_files(episode.public)
    )
    qualified = qualify_episode(episode)
    budget = episode.public.initial_state.resources.actions_remaining
    checks = {
        "compiled_contract": qualified.passed and all(qualified.checks.values()),
        "public_policy_supported_win": bool(result.victory_code)
        and result.performance.decision_diagnostics.escape_classification == "supported_win",
        "exact_replay": canonical_hash(replay(episode, session.trace))
        == canonical_hash(session.state),
        "within_reference_bound": result.current_turn
        <= episode.generation_metadata.guaranteed_policy_action_count,
        "expected_action_budget": budget == cell.expected_budget,
        "tool_limit_covers_reference": 3
        * episode.generation_metadata.guaranteed_policy_action_count
        + 20
        <= 600,
    }
    _require(all(checks.values()), f"{cell.id} live smoke checks failed: {checks}")
    return {
        "checks": checks,
        "action_budget": budget,
        "reference_actions": result.current_turn,
        "reference_action_upper": episode.generation_metadata.guaranteed_policy_action_count,
        "certificate": episode.generation_metadata.investigation_certificate,
        **evidence_binding(episode.public),
        "public_investigation_sha256": digest(episode.public.investigation.model_dump(mode="json")),
    }, session


def _repair_details(cell, episode, session):
    from nexus.ontology.compositional import runtime
    from nexus.ontology.compositional.inference import audit
    from nexus.ontology.compositional.laws import QUERIES, REPAIRS, population

    data = audit()
    index = cell.seed % len(population())
    world, wins = population()[index]
    passive = data.closure(index, [i for i, q in enumerate(QUERIES) if q[2] == (0, 0)])
    contexts = [
        len(data.common(data.closure(index, [i for i, q in enumerate(QUERIES) if q[0] == mode])))
        for mode in (0, 1)
    ]
    lower = data.positive_reading_lower(index)
    _require(
        not data.common(passive) and contexts == [0, 0] and lower >= 3,
        "selected repair fixture lacks its intervention obstruction",
    )
    # Every accepted repair, including noncanonical alternatives, at the live seam.
    state = session.state.model_copy(deep=True)
    for i, doses in enumerate(REPAIRS):
        artifact = state.artifacts["seal"]
        artifact.payload = (
            artifact.data().model_copy(update={"doses": doses}).model_dump(mode="json")
        )
        runtime.assess_mission(episode, state)
        _require(
            state.mission_accepted == bool(wins >> i & 1),
            "live repair acceptance differs from independent support",
        )
    return {
        "world_index": index,
        "topology": world.topology,
        "changed_module": world.changed,
        "positive_reading_lower_bound": lower,
        "untrimmed_closure_worlds": passive.bit_count(),
        "untrimmed_common_repairs": 0,
        "single_context_common_repairs": contexts,
        "live_acceptance_checks": len(REPAIRS),
        "checks": {
            "intervention_obstruction": True,
            "both_contexts_required": True,
            "three_reading_lower_bound": True,
            "all_live_repairs_match": True,
        },
        "scope": "Obstructions and reading-only certificate concern the undisclosed prior; S21 supplies a repair and is only an execution control. Rejected finishes are excluded from the reading-only bound.",
    }


def _same_physics(left, right):
    def initial(ep):
        value = ep.public.initial_state.model_dump(mode="json")
        value["resources"].pop("actions_remaining")
        return value

    return left.investigation_truth == right.investigation_truth and initial(left) == initial(right)


def scientific_contrasts(episodes, sessions, dependencies):
    result = []

    def add(ids, kind, description, checks):
        _require(all(checks.values()), f"scientific contrast {ids} failed: {checks}")
        result.append({"ids": ids, "kind": kind, "interpretation": description, "checks": checks})

    for left, right, kind, description in (
        (
            "S01",
            "S02",
            "procedure-disclosure",
            "D0 supplies the procedure; D5 does not. Laws, physics and64-action allowance agree. This is not a ladder of unknown-law inference depth.",
        ),
        (
            "S02",
            "S03",
            "law-disclosure",
            "T0 discloses laws; T3 withholds them at fixed D5/P1/R1 and64 actions.",
        ),
        (
            "S03",
            "S04",
            "resource",
            "Same science and physics;64 actions versus no environment action cap. Tool/turn ceilings still apply.",
        ),
        (
            "S05",
            "S08",
            "compound-disclosure",
            "Same revision world and64 actions; T and D jointly change from0/0 to3/5. No separate T or D effect is identifiable.",
        ),
        (
            "S21",
            "S22",
            "compound-execution-control",
            "Same repair world; supplied repair versus unknown repair and8 versus30 actions. This does not isolate T/D.",
        ),
    ):
        a, b = episodes[left], episodes[right]
        checks = {"same_physics": _same_physics(a, b)}
        if kind in {"procedure-disclosure", "law-disclosure", "compound-disclosure"}:
            checks["same_action_budget"] = (
                a.generation_metadata.action_budget == b.generation_metadata.action_budget
            )
        if kind == "resource":
            checks["same_science_except_budget"] = science_projection(a) == science_projection(b)
        add([left, right], kind, description, checks)
    for left, right in (("S16", "S17"), ("S19", "S20"), ("S22", "S23")):
        a, b = episodes[left], episodes[right]
        checks = {
            "same_science_except_budget": science_projection(a) == science_projection(b),
            "same_reference_actions": [r.action for r in sessions[left].trace]
            == [r.action for r in sessions[right].trace],
            "same_reference_observations": [r.events for r in sessions[left].trace]
            == [r.events for r in sessions[right].trace],
        }
        if left == "S22":
            checks["exact_30_36_allowances"] = (
                a.generation_metadata.action_budget,
                b.generation_metadata.action_budget,
            ) == (30, 36)
        add(
            [left, right],
            "resource",
            "Only the disclosed action allowance changes; the public science, physical world and reference observations agree.",
            checks,
        )
    for ids in (("S13", "S14", "S15", "S16"), ("S18", "S19")):
        values = [episodes[key] for key in ids]
        add(
            list(ids),
            "layout-under-zero-slack-rule",
            "P changes physical layout at fixed T0/D5 and R2's zero-slack rule. Absolute budgets differ with the exact minimum; this is not a fixed-action-budget P contrast.",
            {
                "same_law_and_target": all(
                    ep.investigation_truth == values[0].investigation_truth
                    and ep.public.investigation.data().target
                    == values[0].public.investigation.data().target
                    for ep in values
                ),
                "all_exact_zero_slack": all(
                    ep.generation_metadata.investigation_certificate["resource_allowance"] == 0
                    for ep in values
                ),
            },
        )
    add(
        ["S07", "S08"],
        "certificate-structure",
        "Identical public archive and responses through query length3; different full behavior and optimistic reading certificate C2 versusC4 at L*=4. The full three-world proof also qualifies unselected seed6464. This is not a pure numeric D intervention.",
        {
            "full_balanced_triple_qualified": all(
                dependencies["revision"]["balanced_triple"][key] is True
                for key in (
                    "public_evidence_identical",
                    "all_words_through_length_three_identical",
                    "distinct_full_behaviors",
                )
            ),
        },
    )
    add(
        ["S11", "S12"],
        "rival-horizon",
        "Complete rival pair with identical public evidence, agreeing through length5 and first differing at6. C differs (3 versus2); these are structural coordinates, not cognitive-depth bounds.",
        {
            "complete_rival_pair_qualified": dependencies["revision"]["rival_pairs"][0]["ids"]
            == ["06", "07"]
            and len(dependencies["revision"]["rival_pairs"][0]["shortest_distinguishing_word"])
            == 6,
        },
    )
    return result


def _dependency_reports(texts, directory):
    specifications = (
        ("interference", interference.Pilot, interference_comparison.preflight),
        ("stateful", stateful.Pilot, stateful.preflight),
        ("revision", td_cycle.Cycle, td_cycle.preflight),
        ("planning", planning.Pilot, planning.preflight),
    )
    reports = {}
    for key, schema, qualify in specifications:
        matrix = schema.model_validate_json(texts[key])
        report = qualify(matrix, directory / f"{key}.json")
        _require(report.get("status") == "passed", f"{key} full qualification did not pass")
        reports[key] = _stable(report)
    return reports


@lru_cache(maxsize=1)
def _qualified_json(source, sources_json, pilot_json, dependency_json):
    """Cache only immutable evidence, keyed by every installed/source/matrix byte.

    Export within a preflight process avoids repeating expensive full proofs.
    A fresh process or any source/dependency change performs qualification again.
    """
    pilot = Pilot.model_validate_json(pilot_json)
    texts = json.loads(dependency_json)
    with TemporaryDirectory(prefix="nexus-cross-axis-") as temporary:
        dependencies = _dependency_reports(texts, Path(temporary))
    conformance = compositional_conformance()
    source_cells = {
        key: {c["id"]: c for c in report["cells"]} for key, report in dependencies.items()
    }
    original = interference.Pilot.model_validate_json(texts["interference"])
    originals = {c.id: c for c in original.runs}
    lineage = {
        key: {c["id"]: c for c in json.loads(texts[key])["runs"]}
        for key in ("structural", "budget")
    }
    cells, episodes, sessions = [], {}, {}
    for cell in pilot.runs:
        row = {**cell.model_dump(mode="json"), "task_name": task_for(cell, pilot, original)["name"]}
        if cell.family == "stateful-interference-v1":
            old = originals[cell.source_id]
            _require(
                (old.seed, old.resource, old.options().model_dump())
                == (cell.seed, cell.resource, cell.ontology_options),
                "interference source row changed",
            )
            row["qualification"] = source_cells["interference"][cell.source_id]
            row["checks"] = {
                "unchanged_original_condition": True,
                "full_structural_qualification": True,
            }
        else:
            episode = cell.generate()
            episodes[cell.id] = episode
            live, session = _live_smoke(cell, episode)
            sessions[cell.id] = session
            row.update(live)
            if cell.family == "compositional-repair-v1":
                ancestor = lineage[cell.source_matrix][cell.source_id]
                _require(ancestor["seed"] == cell.seed, "repair source world changed")
                if cell.source_matrix == "budget":
                    _require(
                        ancestor["budget_profile"] == cell.budget_profile,
                        "repair source allowance changed",
                    )
                row["qualification"] = _repair_details(cell, episode, session)
            else:
                proof = source_cells[cell.source_matrix][cell.source_id]
                _require(proof["seed"] == cell.seed, "selected source seed differs")
                if cell.source_matrix == "revision":
                    _require(
                        proof["guidance"] == cell.ontology_options["guidance"],
                        "selected guidance differs",
                    )
                    _require(
                        (proof["role"] == "execution") == (cell.theory == 0),
                        "selected revision disclosure differs",
                    )
                else:
                    _require(
                        all(
                            proof[key] == getattr(cell, key)
                            for key in ("theory", "discovery", "planning", "resource")
                        ),
                        "selected source profile differs",
                    )
                row["qualification"] = proof
        cells.append(row)
    contrasts = scientific_contrasts(episodes, sessions, dependencies)
    _require(
        source_digest() == source and source_binding() == json.loads(sources_json),
        "implementation changed during cross-axis qualification",
    )
    _require(_dependencies(pilot) == texts, "dependency changed during cross-axis qualification")
    report = {
        "version": VERSION,
        "status": "passed",
        "source_sha256": source,
        "sources": json.loads(sources_json),
        "matrix_sha256": digest(pilot.model_dump()),
        "dependency_matrix_sha256": pilot.dependency_matrix_sha256,
        "cells": cells,
        "dependencies": dependencies,
        "compositional_conformance": conformance,
        "scientific_contrasts": contrasts,
        "suites": {
            suite: [cell.id for cell in pilot.runs if cell.suite == suite] for suite in SUITES
        },
        "inventory": {
            "total": 56,
            "unchanged_interference": 32,
            "new_smoke": 24,
            "smoke_td": 16,
            "smoke_pr": 8,
        },
        "qualification_gates": {
            "complete_current_source_dependencies": True,
            "all56_selected_conditions": True,
            "supported_public_witness_and_canonical_replay": True,
            "repair_current_conformance_and_intervention_obstructions": True,
            "matched_scientific_contrasts": True,
            "unchanged_interference_prompts_and_physics": True,
        },
        "limits": {
            "recommended_tool_call_limit": 600,
            "max_turns": 650,
            "historical_td_tool_call_limit": 120,
            "historical_td_max_turns": 160,
            "environment_budgets_unchanged": True,
        },
        "empirical_difficulty_calibrated": False,
        "scope": "Purpose-selected smaller-model screen, not a population failure estimate or calibrated cognitive ladder. Full historical proofs are preserved, including unselected proof companions. No model calls. Common600/650 harness ceilings differ from historical T/D120/160; no pure historical model effect can be inferred across that contract change.",
    }
    return json.dumps(report, sort_keys=True)


def _qualified(pilot):
    source = source_digest()
    sources = source_binding()
    texts = _dependencies(pilot)
    result = json.loads(
        _qualified_json(
            source,
            json.dumps(sources, sort_keys=True),
            pilot.model_dump_json(),
            json.dumps(texts, sort_keys=True),
        )
    )
    _require(
        source_digest() == source and source_binding() == sources and _dependencies(pilot) == texts,
        "source changed while retrieving qualification",
    )
    return result


def preflight(pilot: Pilot, outputPath: Path):
    start = perf_counter()
    output = Path(outputPath)
    report = {
        "version": VERSION,
        "status": "running",
        "matrix_sha256": digest(pilot.model_dump()),
        "source_sha256": source_digest(),
        "cells": [],
    }
    atomic_json(output, report)
    try:
        report = _qualified(pilot)
        report["seconds"] = perf_counter() - start
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(
            status="blocked", error=f"{type(exc).__name__}: {exc}", seconds=perf_counter() - start
        )
        atomic_json(output, report)
        raise


def validate_report(pilot: Pilot, report: dict) -> None:
    """Fail closed on stale, incomplete, edited or fabricated qualification."""
    if (
        report.get("version") != VERSION
        or report.get("status") != "passed"
        or report.get("source_sha256") != source_digest()
        or report.get("sources") != source_binding()
        or report.get("matrix_sha256") != digest(pilot.model_dump())
        or report.get("dependency_matrix_sha256") != pilot.dependency_matrix_sha256
        or [cell.get("id") for cell in report.get("cells", [])] != [cell.id for cell in pilot.runs]
    ):
        raise ValueError("cross-axis export requires a complete current matrix/source preflight")
    _require(
        _stable(report) == _qualified(pilot),
        "cross-axis proof fields differ from recomputed current-source qualification",
    )


def task_for(cell: Cell, pilot: Pilot, original: interference.Pilot | None = None):
    if cell.family == "stateful-interference-v1":
        if original is None:
            original = interference.Pilot.model_validate_json(_dependencies(pilot)["interference"])
        return interference.task_for(
            next(c for c in original.runs if c.id == cell.source_id), original
        )
    inputs = {
        "axis-version": 2,
        "science-family": cell.family,
        "seed": str(cell.seed),
        "theory-level": cell.theory,
        "discovery-level": cell.discovery,
        "planning-level": cell.planning,
        "resource-pressure": cell.resource,
        "budget-profile": cell.budget_profile,
        "generation-timing": True,
        "extended-diagnostics": True,
    }
    if cell.ontology_options:
        inputs["ontology-options"] = json.dumps(
            cell.ontology_options, sort_keys=True, separators=(",", ":")
        )
    return {
        "name": f"NEXUS smoke-{cell.id}",
        "disabled": False,
        "suite": "nexus",
        "category": "cross-axis-smoke",
        "difficulty": "experimental",
        "tags": [pilot.version, cell.family, cell.suite],
        "prompt": PROMPT,
        "response-result-format": "The actual victory_code and nothing else. No quotes, Markdown or explanation.",
        "tool-selector": {"service-inputs": {"nexus": inputs}},
    }


def export_tasks(pilot: Pilot, report: dict, directory: Path):
    validate_report(pilot, report)
    directory = Path(directory)
    original = interference.Pilot.model_validate_json(_dependencies(pilot)["interference"])
    directory.mkdir(parents=True, exist_ok=True)
    for suite in SUITES:
        tasks = [task_for(cell, pilot, original) for cell in pilot.runs if cell.suite == suite]
        atomic_json(directory / f"nexus-cross-axis-{suite}-tasks.yaml", task_config(tasks, pilot))
