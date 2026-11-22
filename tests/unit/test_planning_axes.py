"""P/R must change public planning/costs without secretly changing the law."""

import json
from copy import deepcopy
from itertools import product
from pathlib import Path

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import FinishAction, MoveAction, ProbeAction, TakeAction, WaitAction
from nexus.models.episode import PrivateEpisode
from nexus.ontology.planning import runtime
from nexus.ontology.planning.generation import certificate
from nexus.ontology.planning.planner import optimal, science_shortest_cost
from nexus.ontology.planning.policy import public_policy
from nexus.ontology.planning.proof import all_world_policy, physical_minimum
from nexus.ontology.stateful.generation import TARGETS, selection
from nexus.protocol.investigation_metrics import summarize
from nexus.protocol.session import Session
from nexus.solver import solve


def episode(seed=21, *, theory=0, planning=3, resource=2):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="stateful-planning-v1",
        theory_level=theory,
        discovery_level=5,
        planning_level=planning,
        resource_pressure=resource,
        verifier_secret="planning-test",
    )


def act(session, action):
    return session.act(expected_turn=session.status().turn, action=action)


@pytest.mark.parametrize("seed", [21, 31, 229])
@pytest.mark.parametrize("planning", range(4))
def test_joint_planner_matches_independent_unit_bfs_and_live_solver(seed, planning):
    ep = episode(seed, planning=planning)
    w, target = selection(seed)
    plan = optimal(w, target, planning)
    assert plan.actions == physical_minimum(w, target, planning)
    assert plan.actions <= science_shortest_cost(w, target, planning)
    assert solve(ep).optimal_action_count == plan.actions
    session = Session(ep)
    result = public_policy(session, ep.public.evidence_files)
    assert result.victory_code and result.current_turn == plan.actions
    assert session.state.resources.actions_remaining == 0
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)


@pytest.mark.parametrize("seed", [21, 31])
def test_extra_transformations_strictly_reduce_total_cost(seed):
    w, target = selection(seed)
    joint = optimal(w, target, 3)
    assert len(joint.modes) > optimal(w, target, 0).actions - 2
    assert joint.actions < science_shortest_cost(w, target, 3)


@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("planning", range(4))
def test_routed_reference_bound_covers_every_possible_law(target, planning):
    proof = all_world_policy(target, planning)
    assert proof["worlds"] == 256 and proof["all_finishes_supported"]


def test_matched_axes_keep_physics_and_public_only_t3_budget():
    baseline = episode()
    for theory in (0, 3):
        for planning in range(4):
            for resource in range(3):
                ep = episode(theory=theory, planning=planning, resource=resource)
                assert ep.investigation_truth == baseline.investigation_truth
                assert (
                    ep.public.investigation.data().target
                    == baseline.public.investigation.data().target
                )
                assert (
                    ep.public.evidence_files
                    == episode(theory=theory, planning=planning, resource=0).public.evidence_files
                )
    # Different private laws sharing the public target produce identical T3
    # contracts, evidence and budget; episode_id is the only public difference.
    first = episode(theory=3)
    seed = next(
        s
        for s in range(100)
        if selection(s)[1] == selection(21)[1] and selection(s)[0] != selection(21)[0]
    )
    other = episode(seed, theory=3)
    assert first.public.model_dump(exclude={"episode_id"}) == other.public.model_dump(
        exclude={"episode_id"}
    )
    assert first.generation_metadata == other.generation_metadata


@pytest.mark.parametrize("theory", [0, 3])
@pytest.mark.parametrize("resource", [0, 1, 2])
def test_public_policy_qualification_and_reference_scope(theory, resource):
    ep = episode(theory=theory, resource=resource)
    report = qualify_episode(ep)
    assert report.passed, report.errors
    spec = ep.public.investigation.data()
    proof = certificate(spec, resource)
    assert (proof["reference_kind"] == "exact-known-law-optimum") == (theory == 0)
    assert ep.generation_metadata.recommended_tool_call_limit >= 3 * proof["reference_action_upper"]


def test_one_wasted_action_makes_exact_known_law_budget_insufficient():
    ep = episode()
    session = Session(ep)
    assert act(session, WaitAction()).ok
    for action in runtime.physical_plan(ep):
        result = act(session, action)
    assert not result.victory_code
    assert session.status().status.value == "failed"
    assert (
        physical_minimum(ep.investigation_truth.data(), ep.public.investigation.data().target, 3)
        == ep.generation_metadata.action_budget
    )


def test_remote_probe_atomicity_nonmutation_and_ineligible_finish_inference():
    ep = episode(theory=3, resource=0)
    session = Session(ep)
    act(session, TakeAction(artifact="seal"))
    before = canonical_hash(session.state)
    assert not act(session, ProbeAction(machine="vek", artifact="seal")).ok
    assert canonical_hash(session.state) == before
    act(session, MoveAction(target="a"))
    specimen = session.state.artifacts["seal"].model_dump()
    probe = act(session, ProbeAction(machine="vek", artifact="seal"))
    assert probe.ok
    assert session.state.artifacts["seal"].model_dump() == specimen

    def diagnostics():
        return summarize(
            ep, session.state, session.trace, invalid=1, duplicates=0, conflicts=0
        ).decision_diagnostics

    before_count = diagnostics().final_evidence.remaining_worlds
    result = act(session, FinishAction())
    assert not result.victory_code
    assert diagnostics().final_evidence.remaining_worlds == before_count
    assert diagnostics().submissions[-1].evidence.classification == "ineligible"
    assert runtime.mission_tracker(ep.public).attempted() is None


@pytest.mark.parametrize("field", ["layout", "budget", "truth", "evidence", "metadata"])
def test_compiled_contract_tampering_rejected(field):
    data = episode().model_dump(mode="json")
    if field == "layout":
        data["public"]["initial_state"]["machines"]["vek"]["room_id"] = "array"
    elif field == "budget":
        data["public"]["initial_state"]["resources"]["actions_remaining"] -= 1
    elif field == "truth":
        gains = data["investigation_truth"]["payload"]["gains"]
        gains[0] = 3 - gains[0]
    elif field == "evidence":
        data["public"]["evidence_files"]["layout.json"] = "{}"
    else:
        data["generation_metadata"]["recommended_tool_call_limit"] = 1
    with pytest.raises(ValueError):
        PrivateEpisode.model_validate(data)


def test_public_contract_contains_map_but_no_private_solution():
    ep = episode(theory=3)
    public = ep.public.model_dump_json()
    for key in ("construction_seed", "verifier_secret", "physical_plan", "investigation_truth"):
        assert key not in public
    theory = json.loads(ep.public.evidence_files["theory.json"])
    assert theory["specification"]["resolved"] is None
    assert "procedure" not in theory["specification"]
    layout = json.loads(ep.public.evidence_files["layout.json"])
    assert set(layout["rooms"]) == set(ep.public.rooms)
    assert {k: v.room_id for k, v in ep.public.initial_state.machines.items()} == layout["machines"]


@pytest.fixture(scope="module")
def pilot_report(tmp_path_factory):
    from nexus.evaluation.planning import Pilot, preflight

    pilot = Pilot.model_validate_json(Path("docs/planning-resource-matrix.json").read_text())
    return pilot, preflight(pilot, tmp_path_factory.mktemp("planning") / "preflight.json")


def test_export_matches_matrix_and_common_harness_limits(pilot_report, tmp_path):
    from nexus.evaluation.planning import export_tasks

    pilot, report = pilot_report
    output = tmp_path / "tasks.yaml"
    export_tasks(pilot, report, output)
    config = json.loads(output.read_text())["task-config"]
    assert config["tool-selector"]["tools"][0]["max-calls"] == 600
    assert len(config["tasks"]) == 16
    for cell, task in zip(pilot.runs, config["tasks"], strict=True):
        args = task["tool-selector"]["service-inputs"]["nexus"]
        assert args["seed"] == str(cell.seed)
        assert args["planning-level"] == cell.planning
        assert args["resource-pressure"] == cell.resource


@pytest.mark.parametrize(
    "corruption",
    [
        "source",
        "matrix",
        "status",
        "version",
        "kernel",
        "cells",
        "identity",
        "check",
        "tradeoff",
        "prior",
        "missing_bounds",
        "missing_costs",
    ],
)
def test_task_export_rejects_incomplete_stale_or_failed_evidence(
    pilot_report, tmp_path, corruption
):
    from nexus.evaluation.planning import export_tasks

    pilot, original = pilot_report
    report = deepcopy(original)
    if corruption in ("source", "matrix", "status", "version"):
        key = {
            "source": "sources",
            "matrix": "matrix_sha256",
            "status": "status",
            "version": "version",
        }[corruption]
        report[key] = "invalid"
    elif corruption == "kernel":
        report["kernel"] = {}
    elif corruption == "cells":
        report["cells"] = [{} for _ in pilot.runs]
    elif corruption == "identity":
        report["cells"][0]["seed"] += 1
    elif corruption == "check":
        report["cells"][0]["checks"]["exact_replay"] = False
    elif corruption == "tradeoff":
        del report["cells"][3]["checks"]["strict_joint_planning_tradeoff"]
    elif corruption == "missing_bounds":
        del report["cells"][5]["certificate"]
        del report["cells"][5]["all_world_reference"]["maximum_actions"]
    elif corruption == "missing_costs":
        del report["cells"][0]["physical_minimum"]
    else:
        report["cells"][5]["all_world_reference"]["worlds"] = 1
    output = tmp_path / "tasks.yaml"
    with pytest.raises(ValueError):
        export_tasks(pilot, report, output)
    assert not output.exists()


def test_matrix_refuses_unmatched_profiles_or_reused_fixtures(pilot_report):
    from nexus.evaluation.planning import Pilot

    pilot, _ = pilot_report
    data = pilot.model_dump()
    data["runs"][4]["resource"] = 2
    with pytest.raises(ValueError):
        Pilot.model_validate(data)
    data = pilot.model_dump()
    for row in data["runs"][8:]:
        row["seed"] = data["runs"][0]["seed"]
    with pytest.raises(ValueError):
        Pilot.model_validate(data)


@pytest.mark.parametrize("planning", range(4))
def test_planning_continuation_certifies_all_vectors_and_rooms_with_scalar_bellman_equations(planning):
    from nexus.ontology.planning.layout import LAYOUTS
    from nexus.ontology.planning.planner import continuation_distances
    from nexus.ontology.stateful.generation import selection
    from nexus.ontology.stateful.proof import scalar_step

    world, target = selection(21)
    layout = LAYOUTS[planning]
    costs = continuation_distances(world, target, planning)

    def cost(vector, room):
        if vector is None:
            return float("inf")
        return costs.get((sum(v * 5**(3 - i) for i, v in enumerate(vector)), room), float("inf"))

    for vector, room in product(product(range(5), repeat=4), layout.rooms):
        after = [cost(vector, b if a == room else a)
                 for a, b in layout.edges if room in (a, b)]
        after += [cost(scalar_step(world, vector, mode), room)
                  for mode, location in enumerate(layout.mode_rooms) if location == room]
        assert cost(vector, room) == (0 if (vector, room) == (target, layout.finish)
                                      else 1 + min(after, default=float("inf")))
