"""Bounded, operator-only T/D screen; qualification is not empirical calibration."""

from __future__ import annotations

from itertools import combinations
from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.discovery import digest
from nexus.evaluation.revision import certificate_witness, fixed_panel_bound, topology_key
from nexus.generator import generate_episode
from nexus.ontology.discovery.policy import public_policy
from nexus.ontology.revision.inference import Belief
from nexus.ontology.revision.laws import QUERIES, class_id, compiled
from nexus.ontology.revision.proof import prove, prove_no_three_reading_certificate, require
from nexus.ontology.revision.qualification import audit, minimum_certificate
from nexus.protocol.session import Session
from nexus.provenance import source_digest


class Case(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    seed: StrictInt = Field(ge=0)
    role: Literal[
        "balanced", "horizon-contrast", "rival-pair", "consistency", "shortcut", "execution"
    ]
    guidance: Literal["principles", "provisional"] = "principles"
    expected_certificate: StrictInt = Field(ge=0, le=7)
    expected_horizon: StrictInt = Field(ge=0, le=8)
    pair: str | None = None
    single_shot: bool = False


class Cycle(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["td-cycle-v1"]
    external_python: Literal[False] = False
    fresh_context_per_execution: Literal[True] = True
    common_action_budget: Literal[64] = 64
    tool_call_limit: Literal[120] = 120
    max_turns: Literal[160] = 160
    repeats: Literal[2] = 2
    cases: tuple[Case, ...] = Field(min_length=12, max_length=12)

    @model_validator(mode="after")
    def inventory(self):
        require(
            tuple(c.id for c in self.cases) == tuple(f"{i:02}" for i in range(1, 13)),
            "ordered IDs 01..12 required",
        )
        roles = (
            ("balanced",) * 3
            + ("horizon-contrast",) * 2
            + ("rival-pair",) * 4
            + ("consistency", "shortcut", "execution")
        )
        require(tuple(c.role for c in self.cases) == roles, "controlled role inventory changed")
        require(
            tuple(c.id for c in self.cases if c.single_shot) == ("01", "02", "03", "08", "09"),
            "single-shot panel changed",
        )
        require(len({c.seed for c in self.cases[:11]}) == 11, "duplicate discovery worlds")
        require(
            self.cases[11].seed == self.cases[0].seed,
            "known-construction control must match first world",
        )
        require(
            self.cases[9].seed == 1101 and self.cases[10].seed == 468,
            "fixed consistency/shortcut controls require deliberate cycle revision",
        )
        for i, c in enumerate(self.cases):
            require(
                c.guidance == ("provisional" if i in (9, 10) else "principles"), "guidance confound"
            )
            require(
                c.pair == ("A" if i in (5, 6) else "B" if i in (7, 8) else None),
                "incomplete rival pairs",
            )
        return self


def episode(case: Case, *, single: bool = False, checker: bool = False):
    control = case.role == "execution"
    return generate_episode(
        case.seed,
        axis_version=2,
        science_family="model-revision-v1",
        theory_level=0 if control else 3,
        discovery_level=0 if control else 5,
        planning_level=0,
        resource_pressure=1,
        ontology_options={
            "guidance": case.guidance,
            "finish_policy": "single" if single else "recoverable",
            "consistency_check": "readings" if checker else "off",
        },
        verifier_secret="operator-td-cycle-preflight",
    )


def length_certificates(mask: int, truth: int):
    """C(L) is null exactly when all legal queries through L leave rivals."""
    prior = compiled()
    values = []
    for length in range(1, 9):
        indices = tuple(q for q, word in enumerate(QUERIES) if len(word) <= length)
        closure = mask
        for q in indices:
            closure &= prior.partitions[q][prior.rows[truth][q]]
        if closure != 1 << truth:
            values.append(None)
        else:
            result = minimum_certificate(mask, truth, query_indices=indices)
            values.append(
                {
                    "readings": result.readings,
                    "queries": result.queries,
                    "search_nodes": result.search_nodes,
                }
            )
    return values


def short_word_first(mask: int, truth: int):
    """Simulate a public chooser; truth is used only to supply returned outputs."""
    prior = compiled()
    path = []
    while mask.bit_count() > 1:
        informative = [
            q
            for q, parts in enumerate(prior.partitions)
            if max((mask & part).bit_count() for part in parts) < mask.bit_count()
        ]
        q = min(
            informative,
            key=lambda q: (
                len(QUERIES[q]),
                max((mask & part).bit_count() for part in prior.partitions[q]),
                q,
            ),
        )
        path.append(QUERIES[q])
        mask &= prior.partitions[q][prior.rows[truth][q]]
    return path


def preflight(cycle: Cycle, output):
    from nexus.evaluation.td_export import TEMPLATE_SHA256

    started = perf_counter()
    report = {
        "version": "td-cycle-preflight-v1",
        "harness_template_sha256": TEMPLATE_SHA256,
        "status": "running",
        "cells": [],
        "source_sha256": source_digest(),
        "matrix_sha256": digest(cycle.model_dump()),
        "empirical_difficulty_calibrated": False,
        "selection_scope": "Purpose-selected contrasts; repeated executions and public rival pairs are not independent population samples.",
    }
    atomic_json(output, report)
    try:
        report["independent_proof"] = prove()
        episodes = {}
        for case in cycle.cases:
            ep = episode(case)
            episodes[case.id] = ep
            spec, truth = ep.public.investigation.data(), ep.investigation_truth.data()
            detail = audit(spec, truth)
            mask = Belief(spec).mask
            horizon = (
                0
                if mask.bit_count() == 1
                else next(
                    i
                    for i, n in enumerate(detail["all_queries_through_length_closure"], 1)
                    if n == 1
                )
            )
            checks = {
                "expected_C": detail["minimum_reading_only_certificate"]
                == case.expected_certificate,
                "expected_L": horizon == case.expected_horizon,
                "common_action_budget": ep.public.initial_state.resources.actions_remaining
                == cycle.common_action_budget,
                "certificate_replay": certificate_witness(ep, detail["certificate_queries"])
                == detail["minimum_supported_actions"],
            }
            old_hard = {
                "C_at_least_four": detail["minimum_reading_only_certificate"] >= 4,
                "unary_study_insufficient": detail["combined_single_mode_all_history_closure"] > 1,
                "ordered_interaction": detail["order_sensitive_witness"] is not None,
                "at_least_six_observable_states": detail["actual_minimal_machine_states"] >= 6,
            }
            if case.role == "horizon-contrast":
                checks["contrast_admission"] = (
                    all(old_hard[k] for k in old_hard if k != "at_least_six_observable_states")
                    and horizon == 5
                )
            if detail["minimum_reading_only_certificate"] >= 4:
                detail["independent_no_three_certificate"] = prove_no_three_reading_certificate(
                    mask, class_id(truth.program)
                )
            elif detail["minimum_reading_only_certificate"] > 0:
                prior = compiled()
                target = class_id(truth.program)
                outcomes = {
                    mask & parts[prior.rows[target][q]] for q, parts in enumerate(prior.partitions)
                }
                require(mask != 1 << target, "unexpected zero-reading certificate")
                for size in range(1, detail["minimum_reading_only_certificate"]):
                    for subset in combinations(outcomes, size):
                        remaining = mask
                        for outcome in subset:
                            remaining &= outcome
                        require(remaining != 1 << target, "independent shorter certificate found")
                detail["independent_lower_certificate_checked"] = True
            baseline_policies = {}
            for name, queries in (
                ("fixed_panel", fixed_panel_bound(mask)),
                ("short_word_first", short_word_first(mask, class_id(truth.program))),
            ):
                # Every selected path is supported, but not necessarily within a
                # live budget. Do not silently turn an over-budget path into proof.
                action_upper = 4 + 2 * len(queries)
                actions = (
                    certificate_witness(ep, queries)
                    if action_upper <= cycle.common_action_budget
                    else None
                )
                baseline_policies[name] = {
                    "queries": queries,
                    "readings": len(queries),
                    "replayed_actions": actions,
                    "fits_common_budget": actions is not None,
                    "scope": "Constructive policy trajectory; not a minimum certificate or cognitive-depth measure.",
                }
            variants = [("baseline", ep)]
            if case.single_shot:
                variants.append(("single-shot", episode(case, single=True)))
            if case.role == "consistency":
                variants.append(("checker", episode(case, checker=True)))
            reference = {}
            for name, variant in variants:
                session = Session(variant)
                result = public_policy(session, variant.public.evidence_files)
                passed = (
                    bool(result.victory_code)
                    and result.performance.decision_diagnostics.escape_classification
                    == "supported_win"
                    and canonical_hash(replay(variant, session.trace))
                    == canonical_hash(session.state)
                )
                require(passed, f"{case.id}/{name}: supported reference/replay failed")
                require(
                    result.current_turn
                    <= variant.generation_metadata.guaranteed_policy_action_count,
                    "reference bound exceeded",
                )
                require(
                    variant.investigation_truth == ep.investigation_truth
                    and variant.public.initial_state == ep.public.initial_state,
                    "intervention changed physical world",
                )
                reference[name] = {"supported_replayed_win": True, "actions": result.current_turn}
            require(all(checks.values()), f"case {case.id}: {checks}")
            report["cells"].append(
                {
                    **case.model_dump(),
                    **detail,
                    "checks": checks,
                    "old_hard_checks": old_hard,
                    "old_hard_tier_admitted": all(old_hard.values()),
                    "L_star": horizon,
                    "C_by_maximum_query_length": length_certificates(mask, class_id(truth.program)),
                    "program": truth.program,
                    "topology_key": topology_key(truth.program),
                    "public_investigation_sha256": canonical_hash(ep.public.investigation),
                    "public_evidence_sha256": canonical_hash(ep.public.evidence_files),
                    "public_policy": reference,
                    "baseline_policies": baseline_policies,
                }
            )
            atomic_json(output, report)
        triple = [episodes[key] for key in ("01", "02", "03")]
        require(
            all(
                ep.public.investigation == triple[0].public.investigation
                and ep.public.evidence_files == triple[0].public.evidence_files
                for ep in triple
            ),
            "balanced triple public evidence differs",
        )
        classes = [class_id(ep.investigation_truth.data().program) for ep in triple]
        require(len(set(classes)) == 3, "balanced triple behaviors duplicate")
        rows = [compiled().rows[target] for target in classes]
        require(
            all(row[:14] == rows[0][:14] for row in rows), "balanced triple short histories differ"
        )
        report["balanced_triple"] = {
            "ids": ["01", "02", "03"],
            "public_evidence_identical": True,
            "all_words_through_length_three_identical": True,
            "distinct_full_behaviors": True,
        }
        pair_checks: list[dict] = []
        for left, right in (("06", "07"), ("08", "09")):
            a, b = episodes[left], episodes[right]
            pa, pb = a.investigation_truth.data().program, b.investigation_truth.data().program
            ra, rb = compiled().rows[class_id(pa)], compiled().rows[class_id(pb)]
            difference = next(word for q, word in enumerate(QUERIES) if ra[q] != rb[q])
            require(
                a.public.investigation == b.public.investigation
                and a.public.evidence_files == b.public.evidence_files,
                "rival pair public evidence differs",
            )
            require(len(difference) == 6, "rival pair does not first diverge at length six")
            pair_checks.append(
                {
                    "ids": [left, right],
                    "public_evidence_identical": True,
                    "shortest_distinguishing_word": difference,
                }
            )
            pair_checks[-1]["distinguishing_query_count_by_length"] = {
                str(length): sum(
                    len(word) == length and ra[q] != rb[q] for q, word in enumerate(QUERIES)
                )
                for length in range(1, 9)
            }
        report["rival_pairs"] = pair_checks
        require(
            topology_key(episodes["04"].investigation_truth.data().program)
            != topology_key(episodes["05"].investigation_truth.data().program),
            "horizon contrasts duplicate topology",
        )
        require(source_digest() == report["source_sha256"], "source changed during preflight")
        report.update(status="passed", seconds=perf_counter() - started)
    except Exception as exc:
        report.update(
            status="blocked", error=f"{type(exc).__name__}: {exc}", seconds=perf_counter() - started
        )
        atomic_json(output, report)
        raise
    atomic_json(output, report)
    return report
