"""Whole-mission physics, recovery, posterior correctness and public-state invariants."""

from itertools import product

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import (
    ConfigureAction,
    DropAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.ontology.assembly.inference import Belief
from nexus.ontology.assembly.laws import (
    BUILDS,
    WORLDS,
    accepted,
    prepare,
    tables,
    target,
)
from nexus.ontology.assembly.policy import construction, public_policy
from nexus.ontology.assembly.proof import oracle_signature, world_audit
from nexus.ontology.assembly.schema import FAMILY, Investigation, Specimen
from nexus.protocol.session import Session


def episode(seed=136, theory=3, discovery=4, planning=0, resource=1, profile="standard"):
    return generate_episode(
        seed,
        axis_version=2,
        science_family=FAMILY,
        theory_level=theory,
        discovery_level=discovery,
        planning_level=planning,
        resource_pressure=resource,
        budget_profile=profile,
        verifier_secret="assembly-test",
    )


def act(session, action):
    result = session.act(session.state.turn, action)
    assert result.ok, result.message
    return result


def test_composed_physics_and_goal_equivalence_do_not_depend_on_inference_cache():
    for world in WORLDS:
        for d in BUILDS:
            assert accepted(world, d) == (oracle_signature(d) == oracle_signature(target(world)))
    assert len(set(tables(True).signatures)) == 96
    # Several different phase assignments are genuinely equivalent for sum laws.
    w = WORLDS[349]
    valid = [d for d in BUILDS if accepted(w, d)]
    assert len(valid) == 3 and len({d[1:4] for d in valid}) == 3


def test_all_locally_valid_phases_are_not_globally_compatible():
    w = WORLDS[136]
    local = [(w.gain_b, a, w.gain_c, b, w.kernel) for a, b in product(range(3), repeat=2)]
    assert 0 < sum(accepted(w, d) for d in local) < len(local)
    spec = Investigation(theory=3, discovery=4)
    detail = world_audit(spec, 136)
    assert detail["minimum_supporting_readings"] == 5
    assert all(not d["supported"] for d in detail["closures"].values())
    assert detail["closures"]["local_only"]["remaining_mission_signatures"] == 10


def test_shortcuts_are_preserved_and_distinguished_from_joint_challenge():
    spec = Investigation(theory=2, discovery=4, known_kernel=0)
    assert world_audit(spec, 349)["closures"]["local_only"]["supported"]
    product_case = world_audit(Investigation(theory=3, discovery=4), 127)
    assert product_case["minimum_supporting_readings"] == 4
    assert product_case["closures"]["b_and_joint"]["supported"]
    assert product_case["closures"]["c_and_joint"]["supported"]
    assert not product_case["closures"]["joint_only"]["supported"]


@pytest.mark.parametrize(
    "theory,discovery,planning,resource,profile",
    [
        (0, 0, 0, 1, "standard"),
        (2, 3, 1, 1, "standard"),
        (2, 4, 0, 1, "standard"),
        (3, 3, 0, 0, "standard"),
        (3, 4, 1, 1, "diagnostic-plus6"),
    ],
)
def test_public_policy_receipt_roundtrip_replay_and_terminal_metrics(
    theory, discovery, planning, resource, profile, caplog
):
    ep = episode(
        theory=theory, discovery=discovery, planning=planning, resource=resource, profile=profile
    )
    ep = PrivateEpisode.model_validate_json(ep.model_dump_json())
    session = Session(ep)
    with caplog.at_level("INFO", logger="nexus.diagnostics"):
        result = public_policy(session, ep.public.evidence_files)
    assert result.victory_code
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    assert result.current_turn <= ep.generation_metadata.guaranteed_policy_action_count
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)
    assert qualify_episode(ep).passed
    assert "assembly_operations" in caplog.text
    assert "first_supporting_reading_ordinal=" in caplog.text


def test_order_matters_and_two_preparations_repair_every_prior_build():
    blank = Specimen()
    bc = prepare(prepare(blank, 0, 1, 1), 1, 2, 2)
    cb = prepare(prepare(blank, 1, 2, 2), 0, 1, 1)
    assert bc != cb and bc.b == (1, 0) and cb.c == (2, 0)
    for old in BUILDS:
        sample = Specimen(b=old[:2], c=old[2:4], kernel=old[4])
        for s, a, t, b, h in BUILDS:
            repaired = prepare(prepare(sample, 0, s, (a - b) % 3), 1, t, b)
            assert repaired.b == (s, a) and repaired.c == (t, b)
            assert repaired.kernel == old[4]


def test_private_solver_physical_optimum_matches_independent_complete_state_search():
    from nexus.ontology.assembly.proof import physical_costs
    from nexus.solver.search import solve

    costs = physical_costs()
    for seed, w in enumerate(WORLDS):
        expected = 2 + min(
            cost
            for build, cost in costs.items()
            if oracle_signature(build) == oracle_signature(target(w))
        )
        result = solve(episode(seed))
        assert result.solvable and result.optimal_action_count == expected
    assert {solve(episode(seed)).optimal_action_count for seed in (0, 136, 349)} <= {6, 7, 8}


def test_preview_does_not_commit_and_reader_is_reference_not_build_residual():
    s = Session(episode(resource=0))
    act(s, TakeAction(artifact="carrier"))
    baseline = act(s, ProbeAction(machine="reader", artifact="carrier")).events[0]["details"][
        "result"
    ]["payload"]["reading"]
    act(s, ConfigureAction(machine="forge", settings=(0, 2, 1)))
    preview = act(s, ProbeAction(machine="forge", artifact="carrier"))
    assert preview.events[0]["details"]["result"]["payload"]["b"] == [2, 1]
    assert s.state.artifacts["carrier"].data().b is None
    act(s, OperateAction(machine="forge", artifact="carrier"))
    act(s, ConfigureAction(machine="forge", settings=(1, 1, 2)))
    act(s, OperateAction(machine="forge", artifact="carrier"))
    assert s.state.artifacts["carrier"].data().b == (2, 0)
    act(s, ProbeAction(machine="assembler", artifact="carrier"))
    assert s.state.artifacts["carrier"].data().kernel is None
    after = act(s, ProbeAction(machine="reader", artifact="carrier")).events[0]["details"][
        "result"
    ]["payload"]["reading"]
    assert after == baseline


def test_only_actual_complete_carried_device_can_exclude_a_failed_finish():
    ep = episode(resource=0)
    s = Session(ep)
    wrong = next(d for d in BUILDS if not accepted(ep.investigation_truth.data(), d))
    act(s, TakeAction(artifact="carrier"))
    for a in construction(wrong):
        act(s, a)
    act(s, DropAction(artifact="carrier"))
    act(s, FinishAction())
    report = s.operator_snapshot()["performance"]["decision_diagnostics"]
    assert report["final_evidence"]["remaining_worlds"] == 432
    assert report["submissions"][-1]["evidence"]["classification"] == "ineligible"
    act(s, TakeAction(artifact="carrier"))
    act(s, FinishAction())
    posterior = Belief(ep.public.investigation.data())
    posterior.exclude_target(wrong)
    assert (
        s.operator_snapshot()["performance"]["decision_diagnostics"]["final_evidence"][
            "remaining_worlds"
        ]
        == posterior.counts()[0]
    )
    # A lucky correct build does not become retrospectively supported by its win.
    for a in construction(target(ep.investigation_truth.data())):
        act(s, a)
    result = act(s, FinishAction())
    assert (
        result.victory_code
        and result.performance.decision_diagnostics.escape_classification == "compatible_win"
    )


def test_copy_cannot_substitute_for_mission_and_recovery_is_within_moderate_budget():
    from nexus.evaluation.assembly import recovery_check

    ep = episode()
    assert recovery_check(ep) <= ep.generation_metadata.action_budget
    s = Session(episode(resource=0))
    act(s, TakeAction(artifact="blank-stock"))
    copy = next(iter(s.observe().carried_artifacts)).id
    for a in construction(target(s.episode.investigation_truth.data()), copy):
        act(s, a)
    result = act(s, FinishAction())
    assert not result.victory_code
    assert (
        s.operator_snapshot()["performance"]["decision_diagnostics"]["final_evidence"][
            "remaining_worlds"
        ]
        == 432
    )


@pytest.mark.parametrize(
    "machine,settings",
    [
        ("reader", (3, 0, 0)),
        ("forge", (0, 0, 1)),
        ("forge", (2, 1, 0)),
        ("assembler", (4,)),
        ("assembler", (0, 0)),
        ("reader", (0, 0)),
    ],
)
def test_invalid_configuration_is_free_atomic_and_truth_independent(machine, settings):
    messages = set()
    for seed in (0, 136, 349, 431):
        s = Session(episode(seed))
        before = canonical_hash(s.state)
        r = s.act(0, ConfigureAction(machine=machine, settings=settings))
        assert not r.ok and canonical_hash(s.state) == before
        messages.add(r.message)
    assert len(messages) == 1


@pytest.mark.parametrize(
    "change", ["truth", "disclosure", "initial", "evidence", "goal", "metadata"]
)
def test_private_episode_rejects_contract_tampering(change):
    raw = episode(theory=2).model_dump(mode="json")
    if change == "truth":
        raw["investigation_truth"]["payload"]["offset"] = (
            raw["investigation_truth"]["payload"]["offset"] + 1
        ) % 3
    elif change == "disclosure":
        raw["public"]["investigation"]["payload"]["known_kernel"] = 2
    elif change == "initial":
        raw["public"]["initial_state"]["artifacts"]["carrier"]["payload"]["b"] = [1, 0]
    elif change == "evidence":
        raw["public"]["evidence_files"]["theory.json"] = "{}"
    elif change == "goal":
        raw["public"]["phase_modulus"] = 2
    else:
        raw["generation_metadata"]["guaranteed_policy_action_count"] -= 1
    with pytest.raises(ValueError):
        PrivateEpisode.model_validate(raw)


@pytest.mark.slow
def test_every_world_has_a_supported_live_policy_for_every_science_profile():
    for seed in range(432):
        for t, d in ((2, 3), (2, 4), (3, 3), (3, 4)):
            ep = episode(seed, theory=t, discovery=d)
            session = Session(ep)
            result = public_policy(session, ep.public.evidence_files)
            assert result.victory_code
            assert result.performance.decision_diagnostics.escape_classification == "supported_win"
            assert result.current_turn <= ep.generation_metadata.guaranteed_policy_action_count
