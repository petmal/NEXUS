"""Source-bound admission of exact matrix claims, including legal shortcut play."""

import json
from hashlib import sha256
from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.evaluation.goal_information import minimum_supporting_certificate
from nexus.evaluation.matrix import atomic_json
from nexus.generator import generate_episode
from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.inference import Measurement
from nexus.ontology.staged.inference import Belief
from nexus.ontology.staged.laws import WORLD_INDEX, prior_mask, tables
from nexus.ontology.staged.policy import public_policy
from nexus.ontology.staged.proof import prove_all
from nexus.ontology.staged.schema import SEALS
from nexus.protocol.session import Session


class Cell(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    family: Literal["staged-repair-v1", "history-coupled-v1"]
    seed: StrictInt
    theory: Literal[0, 2, 3]
    discovery: Literal[0, 3, 4, 5]
    budget_profile: Literal["standard", "diagnostic-plus6"] = "standard"
    expected_certificate_readings: StrictInt | None
    purpose: str

    @model_validator(mode="after")
    def compatible_profile(self):
        if self.family == "history-coupled-v1":
            valid = (self.theory, self.discovery, self.expected_certificate_readings) == (
                3,
                5,
                None,
            ) and self.seed == 239
        else:
            valid = (
                (self.theory, self.discovery) in ((0, 0), (2, 3), (2, 4), (3, 3), (3, 4))
                and self.expected_certificate_readings is not None
                and 0 <= self.expected_certificate_readings <= 6
            )
        if not valid:
            raise ValueError("unsupported matrix profile or certificate claim")
        return self


class Pilot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["staged-repair-pilot-v1"]
    external_python: Literal[False]
    fresh_context_per_execution: Literal[True]
    recommended_tool_call_limit: int = Field(ge=80)
    runs: tuple[Cell, ...] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def identifiers(self):
        if len({c.id for c in self.runs}) != len(self.runs):
            raise ValueError("duplicate matrix identifiers")
        return self


def fixed_panel_policy(session, panel):
    """Legal public-prior fixed panel, including all configuration and repair costs."""
    spec = session.episode.public.investigation.data()
    posterior = Belief(spec)

    def act(action):
        response = session.act(session.state.turn, action)
        if not response.ok:
            raise ValueError(response.message)
        return response

    for name in SEALS:
        act(TakeAction(artifact=name))
    if session.observe().room != "array":
        act(MoveAction(target="array"))
    settings = None
    for stage, carrier, tag in panel:
        if settings != (stage, carrier):
            settings = (stage, carrier)
            act(ConfigureAction(machine="reader", settings=settings))
        result = act(ProbeAction(machine="reader", artifact=SEALS[tag]))
        payload = next(
            e["details"]["result"]["payload"] for e in result.events if "result" in e["details"]
        )
        posterior.observe(Measurement("reader", payload))
    decisions = posterior.common_decisions()
    if not decisions:
        raise ValueError("fixed panel leaves no guaranteed complete repair")
    for i, name in enumerate(SEALS):
        act(ConfigureAction(machine="trimmer", settings=decisions[0][i * 3 : i * 3 + 3]))
        act(OperateAction(machine="trimmer", artifact=name))
    return act(FinishAction())


def history_shortcut(session):
    """Regression witness from the seed 239 walkthrough, not an optimality claim."""
    actions = [
        TakeAction(artifact="seal"),
        MoveAction(target="array"),
        ProbeAction(machine="h-scope", artifact="seal"),
        ProbeAction(machine="k-scope", artifact="seal"),
        *(OperateAction(machine=m, artifact="seal") for m in ("tor", "tor", "sen", "tor", "tor")),
        FinishAction(),
    ]
    for action in actions:
        result = session.act(session.state.turn, action)
        if not result.ok:
            raise ValueError(result.message)
    return result


def preflight(pilot, output):
    from nexus.ontology.repair.qualification import source_binding

    report = {
        "version": "staged-repair-preflight-v1",
        "status": "running",
        "sources": None,
        "matrix_sha256": sha256(
            json.dumps(pilot.model_dump(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "deep_tier_admitted": False,
        "empirical_difficulty_calibrated": False,
        "cells": [],
    }
    atomic_json(output, report)
    start = perf_counter()
    try:
        sources = source_binding()
        report["sources"] = sources
        proof = prove_all()
        report["proof_sha256"] = sha256(
            json.dumps(proof, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        report["proof_profiles"] = len(proof["profiles"])
        for cell in pilot.runs:
            begin = perf_counter()
            ep = generate_episode(
                cell.seed,
                axis_version=2,
                science_family=cell.family,
                theory_level=cell.theory,
                discovery_level=cell.discovery,
                planning_level=1,
                resource_pressure=1,
                budget_profile=cell.budget_profile,
                verifier_secret="operator-staged-preflight",
            )
            generation = perf_counter() - begin
            session = Session(ep)
            begin = perf_counter()
            result = (
                history_shortcut(session)
                if cell.family == "history-coupled-v1"
                else public_policy(session, ep.public.evidence_files)
            )
            play = perf_counter() - begin
            checks = {
                "public_policy_wins": bool(result.victory_code),
                "supported_win": result.performance.decision_diagnostics.escape_classification
                == "supported_win",
                "within_reference_bound": result.current_turn
                <= ep.generation_metadata.guaranteed_policy_action_count,
                "exact_replay": canonical_hash(replay(ep, session.trace))
                == canonical_hash(session.state),
            }
            extra = {}
            if cell.family == "staged-repair-v1":
                spec = ep.public.investigation.data()
                table = tables(spec.linked)
                prior = prior_mask(spec)
                index = WORLD_INDEX[ep.investigation_truth.data()]
                outcomes = tuple(
                    parts[table.rows[index][q]] & prior for q, parts in enumerate(table.partitions)
                )
                cert = minimum_supporting_certificate(prior, outcomes, (1 << index,))
                checks["exact_positive_certificate"] = (
                    len(cert) == cell.expected_certificate_readings
                )
                extra = {
                    "mechanisms": ep.investigation_truth.data().model_dump(mode="json"),
                    "positive_certificate_readings": len(cert),
                    "positive_certificate_queries": cert,
                    "certificate_scope": "Minimum actual-outcome reading certificate, oracle query choice, excludes failed finishes and preparation costs.",
                }
                if cell.theory:
                    profile = next(
                        p
                        for p in proof["profiles"]
                        if p["mechanisms"] == 3
                        and p["linked"] == spec.linked
                        and p["known_exponents"] == spec.known_exponents
                    )
                    fixed_session = Session(ep)
                    fixed = fixed_panel_policy(fixed_session, profile["fixed_panel"])
                    checks["fixed_panel_legal_within_same_budget"] = bool(fixed.victory_code)
                    checks["fixed_panel_supported"] = (
                        fixed.performance.decision_diagnostics.escape_classification
                        == "supported_win"
                    )
                    checks["fixed_panel_exact_replay"] = canonical_hash(
                        replay(ep, fixed_session.trace)
                    ) == canonical_hash(fixed_session.state)
                    extra.update(
                        fixed_panel_readings_exact=profile["fixed_readings_exact"],
                        fixed_panel_actions=fixed.current_turn,
                    )
            else:
                checks["walkthrough_shortcut_preserved"] = (
                    result.current_turn == 10
                    and result.performance.decision_diagnostics.final_evidence.remaining_worlds
                    == 32
                )
            if not all(checks.values()):
                raise ValueError(f"{cell.id}: failed checks {checks}")
            report["cells"].append(
                {
                    **cell.model_dump(),
                    **extra,
                    "checks": checks,
                    "actions": result.current_turn,
                    "budget": ep.generation_metadata.action_budget,
                    "generation_seconds": generation,
                    "live_policy_seconds": play,
                    "certificate": ep.generation_metadata.investigation_certificate,
                }
            )
            atomic_json(output, report)
        if source_binding() != sources:
            raise ValueError("installed source changed during preflight")
        report.update(status="passed", seconds=perf_counter() - start)
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
