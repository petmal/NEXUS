"""Fail-closed operator preflight for transfer/evidence fixtures and paired controls."""

from time import monotonic
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from nexus.engine.canonical import canonical_hash
from nexus.evaluation.matrix import atomic_json
from nexus.generator import generate_episode, qualify_episode
from nexus.models.domain import DomainTruth
from nexus.ontology.transfer.laws import QUERIES, accepted, displayed, physical, selection
from nexus.ontology.transfer.tables import N, compile_tables
from nexus.ontology.transfer.inference import counts


class Cell(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    family: Literal["coupled-transfer-v1", "coupled-evidence-v1"]
    seed: StrictInt
    control: bool = False
    budget_profile: Literal["standard", "diagnostic-plus6"] = "standard"
    survey_rival: StrictInt | None = None
    passive_rival: StrictInt | None = None


class Pilot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["transfer-pilot-v1"]
    external_python: Literal[False]
    fresh_context_per_execution: Literal[True]
    recommended_tool_call_limit: int = Field(ge=80)
    runs: tuple[Cell, ...] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def identifiers(self):
        if len({c.id for c in self.runs}) != len(self.runs):
            raise ValueError("duplicate cell identifiers")
        return self


def two_reading_obstruction(seed, coupled, seconds=10):
    """Oracle-chosen positive certificates, all queries; no failed guesses included."""
    table = compile_tables(coupled)
    program_index = seed % N
    index = program_index + ((seed // N) % 3) * N if coupled else program_index
    rival = table.full ^ table.target_by_world[index]
    if not rival:
        return False
    started = monotonic()
    outcomes = {next(p for p in parts if p >> index & 1) & rival for parts in table.outcomes}
    if 0 in outcomes:
        return False
    retained = []
    for mask in sorted(outcomes, key=int.bit_count):
        if monotonic() - started > seconds:
            raise TimeoutError("shortcut certificate incomplete")
        if not any(old & mask == old for old in retained):
            retained.append(mask)
    for i, left in enumerate(retained):
        if monotonic() - started > seconds:
            raise TimeoutError("shortcut certificate incomplete")
        if any(not left & right for right in retained[:i]):
            return False
    return True


def fixture_checks(cell):
    program, offset = selection(cell.seed)
    result = {}
    if cell.survey_rival is not None:
        rival, other_offset = selection(cell.survey_rival)
        result["structural_survey_rival"] = (
            program[-1] == rival[-1]
            and offset == other_offset
            and not accepted(program, rival)
            and all(
                displayed(program, offset, q, "survey", True)
                == displayed(rival, offset, q, "survey", True)
                for q in QUERIES
            )
        )
    if cell.passive_rival is not None:
        rival, _ = selection(cell.passive_rival)
        result["passive_physical_rival"] = not accepted(program, rival) and all(
            physical(program, q) == physical(rival, q) for q in QUERIES if q[4:] == (0, 0)
        )
    if not cell.control:
        result["more_than_two_readings_for_evidence_supported_program"] = two_reading_obstruction(
            cell.seed, cell.family == "coupled-evidence-v1"
        )
    if not all(result.values()):
        raise ValueError(f"{cell.id}: fixture claims fail: {result}")
    return result


def restricted_closures(cell):
    coupled = cell.family == "coupled-evidence-v1"
    table = compile_tables(coupled)
    index = cell.seed % N + (((cell.seed // N) % 3) * N if coupled else 0)
    result = {}
    for name, predicate in (
        ("all_passive_observations", lambda q: q[4:] == (0, 0)),
        ("context_0_only", lambda q: q[0] == 0),
        ("context_1_only", lambda q: q[0] == 1),
    ):
        mask = table.full
        for i, parts in enumerate(table.outcomes):
            if predicate(QUERIES[i % len(QUERIES)]):
                mask &= next(p for p in parts if p >> index & 1)
        result[name] = {
            "remaining_joint_worlds": mask.bit_count(),
            "physical_behavior_classes": counts(mask, coupled)[1],
        }
    return result


def preflight(pilot, output):
    from nexus.ontology.repair.qualification import source_binding

    report = {
        "version": "transfer-preflight-v1",
        "status": "running",
        "sources": source_binding(),
        "empirical_difficulty_calibrated": False,
        "cells": [],
        "scope": "Targeted coverage, public reference wins/replay, positive-certificate obstruction through two readings. No cognitive/adaptive-round or matrix success-rate guarantee; arbitrary failed guesses excluded from per-fixture bound.",
    }
    atomic_json(output, report)
    for cell in pilot.runs:
        claims = fixture_checks(cell)
        closures = None if cell.control else restricted_closures(cell)
        ep = generate_episode(
            cell.seed,
            axis_version=2,
            science_family=cell.family,
            theory_level=0 if cell.control else 3,
            discovery_level=0 if cell.control else 5,
            planning_level=1,
            resource_pressure=1,
            budget_profile=cell.budget_profile,
            verifier_secret="operator-transfer-preflight",
        )
        qualified = qualify_episode(ep)
        if not isinstance(ep.investigation_truth, DomainTruth):
            raise ValueError("transfer preflight requires a registered domain truth")
        if not qualified.passed:
            raise ValueError(f"{cell.id}: {qualified.errors}")
        report["cells"].append(
            {
                **cell.model_dump(),
                "checks": claims,
                "complete_observation_closures": closures,
                "qualification": qualified.model_dump(),
                "program": list(selection(cell.seed)[0]),
                "reader_offset": selection(cell.seed)[1]
                if cell.family == "coupled-evidence-v1"
                else 0,
                "budget": ep.generation_metadata.action_budget,
                "reference_action_upper": ep.generation_metadata.guaranteed_policy_action_count,
                "scientific_identity": canonical_hash(
                    {"truth": ep.investigation_truth.payload, "evidence": ep.public.evidence_files}
                ),
            }
        )
        atomic_json(output, report)
    report["status"] = "passed"
    atomic_json(output, report)
    return report
