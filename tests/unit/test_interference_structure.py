"""Structural claims remain separate from observed action words and public inputs."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from nexus.evaluation.interference import Pilot
from nexus.evaluation.interference_comparison import export_tasks, preflight
from nexus.generator import generate_episode
from nexus.models.actions import FinishAction, ProbeAction, WaitAction
from nexus.ontology.interference.planner import actions_for, optimal
from nexus.ontology.interference.structure import metrics, trajectory
from nexus.ontology.interference.structure_proof import scalar_metrics
from nexus.protocol.session import Session

ROOT = Path(__file__).parents[2]


def episode(seed=101, coupling="coupled", horizon="long", resource=1):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="stateful-interference-v1",
        theory_level=0,
        discovery_level=0,
        planning_level=0,
        resource_pressure=resource,
        ontology_options={"coupling": coupling, "horizon": horizon},
        verifier_secret="structural-test-only",
    )


def test_block_minimum_does_not_assume_primitive_optimality():
    spec = episode(67, horizon="short").public.investigation.data()
    actual = metrics(spec)
    assert actual["minimum_machine_blocks"] == 7
    assert actual["minimum_machine_blocks_on_optimal_paths"] == 8
    assert actual["minimum_whole_bank_reopening_operations"] == 0
    assert all(actual[k] == v for k, v in scalar_metrics(spec).items())


def test_seed101_requires_one_whole_bank_reopening():
    spec = episode().public.investigation.data()
    actual = metrics(spec)
    assert actual["minimum_machine_blocks"] == 11
    assert actual["minimum_whole_bank_reopening_operations"] == 1
    assert all(actual[k] == v for k, v in scalar_metrics(spec).items())


@pytest.mark.parametrize("extra", ["none", "wait", "probe", "failed_finish"])
def test_live_trace_costs_include_nonoperation_actions_and_finish(extra):
    ep = episode(67, "independent", "short")
    spec = ep.public.investigation.data()
    session = Session(ep)
    plan = list(actions_for(spec, optimal(spec).modes))
    if extra == "wait":
        plan.insert(1, WaitAction())
    elif extra == "probe":
        plan.insert(1, ProbeAction(artifact="seal", machine=spec.topology[0].machine))
    elif extra == "failed_finish":
        plan.insert(0, FinishAction())
    for action in plan:
        response = session.act(expected_turn=session.state.turn, action=action)
        assert response.ok
    assert response.victory_code
    values = trajectory(spec, session.trace)
    assert values["success_excess_actions"] == (extra != "none")
    assert values["avoidable_actions_so_far"] == (extra != "none")
    assert values["remaining_minimum_actions"] == 0
    assert values["first_loss_of_optimality_turn"] == (
        None if extra == "none" else 1 if extra == "failed_finish" else 2
    )


def test_partial_trace_reports_regret_without_claiming_success():
    ep = episode(67, "independent", "short")
    session = Session(ep)
    session.act(expected_turn=0, action=WaitAction())
    values = trajectory(ep.public.investigation.data(), session.trace)
    assert values["success_excess_actions"] is None
    assert values["avoidable_actions_so_far"] == 1
    assert values["remaining_minimum_actions"] == 8


def test_source_bound_comparison_exports_unchanged_tasks_and_rejects_forged_metrics(tmp_path):
    pilot = Pilot.model_validate_json((ROOT / "docs/interference-matrix.json").read_text())
    report = preflight(pilot, tmp_path / "preflight.json")
    export_tasks(pilot, report, tmp_path)
    original = json.loads(
        (ROOT / "docs/research/interference-preflight-2026-10-26.json").read_text()
    )
    for cell, previous in zip(report["cells"], original["cells"], strict=True):
        assert cell["public_evidence_sha256"] == previous["public_evidence_sha256"]
        assert cell["certificate"] == previous["certificate"]
    for suite in ("core", "slack"):
        assert (tmp_path / f"nexus-interference-comparison-{suite}-tasks.yaml").read_bytes() == (
            ROOT / f"examples/mindtrial/nexus-interference-{suite}-tasks.yaml"
        ).read_bytes()
    for field in (
        "minimum_machine_blocks",
        "minimum_machine_blocks_on_optimal_paths",
        "minimum_whole_bank_reopening_operations",
    ):
        forged = deepcopy(report)
        forged["cells"][0]["structural"][field] += 1
        with pytest.raises(ValueError, match="recomputed"):
            export_tasks(pilot, forged, tmp_path)
    forged = deepcopy(report)
    forged["cells"][0]["structural_checks"].clear()
    with pytest.raises(ValueError, match="recomputed"):
        export_tasks(pilot, forged, tmp_path)


@pytest.mark.parametrize("extra", ["drop_retake", "unchanged", "rejected"])
def test_live_accounting_handles_drops_noops_and_rejected_requests(extra):
    from nexus.models.actions import DropAction, OperateAction, TakeAction

    ep = episode(67, "independent", "short")
    spec = ep.public.investigation.data()
    session = Session(ep)
    plan = list(actions_for(spec, optimal(spec).modes))
    if extra == "rejected":
        rejected = session.act(
            expected_turn=0, action=OperateAction(machine=spec.topology[0].machine, artifact="seal")
        )
        assert not rejected.ok and session.state.turn == 0 and not session.trace
    elif extra == "drop_retake":
        plan[1:1] = [DropAction(artifact="seal"), TakeAction(artifact="seal")]
    else:
        mode = next(i for i, guard in enumerate(spec.resolved.guards) if guard != 0)
        plan.insert(1, OperateAction(machine=spec.topology[mode].machine, artifact="seal"))
    for action in plan:
        response = session.act(expected_turn=session.state.turn, action=action)
        assert response.ok
    assert response.victory_code
    values = trajectory(spec, session.trace)
    assert (
        values["success_excess_actions"] == {"drop_retake": 2, "unchanged": 1, "rejected": 0}[extra]
    )
    assert values["first_loss_of_optimality_turn"] == (None if extra == "rejected" else 2)
    assert values["unchanged_operations"] == (extra == "unchanged")


def test_exhausted_exact_budget_retains_physical_shortfall_without_success():
    from nexus.models.actions import TakeAction

    ep = episode(67, "independent", "short", resource=2)
    session = Session(ep)
    response = session.act(expected_turn=0, action=TakeAction(artifact="seal"))
    while session.state.resources.actions_remaining:
        response = session.act(expected_turn=session.state.turn, action=WaitAction())
        assert response.ok
    assert response.victory_code is None
    values = trajectory(ep.public.investigation.data(), session.trace)
    assert values["success_excess_actions"] is None
    assert values["remaining_minimum_actions"] == values["avoidable_actions_so_far"] == 7
    assert values["first_loss_of_optimality_turn"] == 2
