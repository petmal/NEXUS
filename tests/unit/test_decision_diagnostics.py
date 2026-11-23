"""Replay observed failure patterns; distinguish evidence, world state and receipts."""

import json
from pathlib import Path

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.models.actions import ACTION_ADAPTER
from nexus.ontology.compositional.inference import audit
from nexus.ontology.compositional.laws import accepted, population, reading
from nexus.protocol.session import Session
from nexus.protocol.transport import receipt_classification

CASES = json.loads(Path("tests/fixtures/compositional-pilot-actions.json").read_text())["cases"]
EXPECTED = {
    "passive-compatible": [(7, 2, "compatible")],
    "contradicted-retry": [(5, 1, "compatible"), (4, 0, "contradicted")],
    "correct-without-finish": [(9, 4, "compatible")],
    "intervention-compatible": [(6, 2, "compatible")],
    "unsupported-win": [(3, 2, "compatible")],
    "unfinished": [],
    "supported-win": [(2, 2, "guaranteed")],
}


def make_episode(seed, **kwargs):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="compositional-repair-v1",
        theory_level=3,
        discovery_level=5,
        planning_level=1,
        resource_pressure=1,
        **kwargs,
    )


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_observed_traces_and_independent_support_counts(case):
    session = Session(make_episode(case["seed"]))
    worlds = [world for world, _ in population()]
    oracle_submissions = []
    for raw in case["actions"]:
        action = ACTION_ADAPTER.validate_python(raw)
        if action.type == "finish":
            dose = session.state.artifacts["seal"].data().doses
            oracle_submissions.append((len(worlds), sum(accepted(w, dose) for w in worlds)))
        result = session.act(session.state.turn, action)
        assert result.ok
        if result.observation.terminal_status.value == "active":
            assert result.performance is None
        if action.type in ("probe", "operate") and action.machine == "sensor":
            sample = result.events[0]["details"]["result"]["payload"]
            if sample["reading"] is not None:
                worlds = [w for w in worlds if reading(w, sample["settings"]) == sample["reading"]]
        if action.type == "finish" and not result.victory_code:
            worlds = [w for w in worlds if not accepted(w, dose)]
    before = canonical_hash(session.state)
    report = session.operator_snapshot()
    assert canonical_hash(session.state) == before
    diagnostics = report["performance"]["decision_diagnostics"]
    actual = [
        (
            s["evidence"]["remaining_worlds"],
            s["evidence"]["accepting_worlds"],
            s["evidence"]["classification"],
        )
        for s in diagnostics["submissions"]
    ]
    assert actual == EXPECTED[case["id"]]
    assert [(a, b) for a, b, _ in actual] == oracle_submissions
    assert diagnostics["final_evidence"]["remaining_worlds"] == len(worlds)
    assert report["provider_stop_reason"] is None
    if case["id"] == "unsupported-win":
        assert diagnostics["escape_classification"] == "compatible_win"
        assert not diagnostics["final_evidence"]["common_repairs"]
    if case["id"] == "supported-win":
        assert diagnostics["escape_classification"] == "supported_win"
    if case["id"] == "correct-without-finish":
        assert diagnostics["correct_state_without_successful_finish"]
        assert report["performance"]["termination_reason"] == "action_budget"
        assert diagnostics["first_intervention_measurement"] == 8
    if case["id"] == "unfinished":
        assert report["status"]["status"] == "active"
        assert report["performance"]["termination_reason"] == "active_at_snapshot"
        assert diagnostics["measured_contexts"] == [0]
    if case["id"] in ("passive-compatible", "contradicted-retry"):
        assert diagnostics["first_intervention_turn"] is None


def test_compiled_outcome_masks_cover_every_value_including_constant_queries():
    data = audit()
    for row, masks in zip(data.rows, data.outcome_masks, strict=True):
        assert set(masks) == set(row)
        for value, mask in masks.items():
            assert mask == sum(1 << i for i, observed in enumerate(row) if observed == value)
    assert any(len(masks) == 1 for masks in data.outcome_masks)


@pytest.mark.parametrize(
    ("won", "correct", "label"),
    [
        (True, True, "accepted_receipt"),
        (True, False, "won_receipt_mismatch"),
        (False, False, "mission_not_won"),
    ],
)
def test_receipt_classification_preserves_live_win(won, correct, label):
    result = receipt_classification(
        {"correct": correct}, {"terminal_status": "won" if won else "failed"}
    )
    assert result["classification"] == label
    assert result["receipt_match"] == (correct if won else None)


def test_v2_response_still_parses_and_v3_schema_matches():
    from nexus.ontology.compositional.policy import public_policy
    from nexus.protocol.investigation_metrics import AuditedDecisionMissionPerformance
    from nexus.protocol.session import ActionResponse

    session = Session(make_episode(438))
    result = public_policy(session, session.episode.public.evidence_files).model_dump(mode="json")
    # Reconstruct the fields present in an actual historical response.
    for field in ("first_eligible_submission_turn", "first_eligible_submission_correct",
                  "first_eligible_submission_supported_by_evidence"):
        result["performance"].pop(field)
    result["performance"]["version"] = "mission-performance-v3"
    assert ActionResponse.model_validate(result).performance.version == "mission-performance-v3"
    result["performance"].pop("decision_diagnostics")
    result["performance"]["version"] = "mission-performance-v2"
    assert ActionResponse.model_validate(result).performance.version == "mission-performance-v2"
    assert (
        json.loads(Path("schemas/performance-mission-v3.schema.json").read_text())
        == AuditedDecisionMissionPerformance.model_json_schema()
    )


@pytest.mark.parametrize(
    "seed,settings,expected",
    [
        (0, (0, 2, 1, 0, 0, 0, 0, 0), 2),
        (0, (1, 2, 1, 0, 0, 0, 0, 0), 1),
        (250, (0, 2, 1, 0, 0, 0, 0, 0), 2),
        (250, (1, 2, 1, 0, 0, 0, 0, 0), 0),
        (438, (0, 0, 0, 0, 0, 1, 0, 0), 0),
        (463, (0, 0, 0, 0, 0, 1, 0, 0), 1),
        (493, (1, 0, 0, 0, 0, 1, 0, 0), 0),
        (498, (1, 0, 0, 0, 0, 1, 0, 0), 1),
        (542, (1, 0, 0, 0, 0, 1, 0, 0), 1),
        (541, (1, 0, 0, 0, 0, 1, 0, 0), 0),
    ],
)
def test_guide_examples_match_live_experiments(seed, settings, expected):
    from nexus.models.actions import (
        ConfigureAction,
        MoveAction,
        OperateAction,
        ProbeAction,
        TakeAction,
    )

    session = Session(make_episode(seed))
    for action in (
        TakeAction(artifact="stock"),
        MoveAction(target="array"),
        ConfigureAction(machine="stage", settings=settings),
        OperateAction(machine="stage", artifact="stock.1"),
        ProbeAction(machine="sensor", artifact="stock.1"),
    ):
        result = session.act(session.state.turn, action)
        assert result.ok
    assert result.events[0]["details"]["result"]["payload"]["reading"] == expected
    assert reading(population()[seed][0], settings) == expected
