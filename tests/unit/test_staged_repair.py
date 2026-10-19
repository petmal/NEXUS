"""Semantic contracts, physical recovery, evidence scope and failure classification."""

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
from nexus.ontology.staged import runtime
from nexus.ontology.staged.inference import Belief
from nexus.ontology.staged.laws import WORLDS, decision, remaining, repair
from nexus.ontology.staged.policy import public_policy
from nexus.ontology.staged.proof import oracle_loads, oracle_repair, prove_profile
from nexus.ontology.staged.schema import FAMILY, SEALS
from nexus.protocol.session import Session


def episode(seed=41, theory=3, discovery=4, planning=0, resource=1, profile="standard"):
    return generate_episode(
        seed,
        axis_version=2,
        science_family=FAMILY,
        theory_level=theory,
        discovery_level=discovery,
        planning_level=planning,
        resource_pressure=resource,
        budget_profile=profile,
        verifier_secret="staged-test",
    )


def act(session, action):
    result = session.act(session.state.turn, action)
    assert result.ok, result.message
    return result


def take_all(session):
    for seal in SEALS:
        act(session, TakeAction(artifact=seal))


def apply_repair(session, target):
    for seal, desired in zip(SEALS, repair(target)):
        old = session.state.artifacts[seal].data().doses
        act(
            session,
            ConfigureAction(
                machine="trimmer", settings=tuple((n - o) % 3 for n, o in zip(desired, old))
            ),
        )
        act(session, OperateAction(machine="trimmer", artifact=seal))


def test_independent_physical_oracle_and_all_mission_signatures():
    assert len(set(map(decision, WORLDS))) == 216
    for world in WORLDS:
        raw = tuple((m.shift, m.exponent) for m in world.mechanisms)
        assert decision(world) == oracle_repair(raw)
        for tag in range(3):
            for doses in product(range(3), repeat=3):
                assert remaining(world, tag, doses) == oracle_loads(raw, tag, doses)


@pytest.mark.parametrize(
    "theory,discovery,planning,resource,profile",
    [
        (0, 0, 1, 1, "standard"),
        (2, 3, 0, 1, "standard"),
        (2, 4, 1, 1, "diagnostic-plus6"),
        (3, 3, 1, 1, "standard"),
        (3, 4, 0, 0, "standard"),
    ],
)
def test_live_policy_roundtrip_replay_and_supported_evidence(
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
    assert result.current_turn <= ep.generation_metadata.guaranteed_policy_action_count
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    assert result.performance.decision_diagnostics.final_evidence.remaining_worlds == 1
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)
    assert qualify_episode(ep).passed
    assert "staged_operations" in caplog.text


def test_probe_is_not_applied_treatment_and_baseline_reading_is_not_residual():
    session = Session(episode(resource=0))
    take_all(session)
    act(session, ConfigureAction(machine="reader", settings=(2, 1)))
    first = act(session, ProbeAction(machine="reader", artifact="seal-0"))
    baseline = first.events[0]["details"]["result"]["payload"]["reading"]
    act(session, ConfigureAction(machine="trimmer", settings=(1, 2, 1)))
    preview = act(session, ProbeAction(machine="trimmer", artifact="seal-0"))
    assert preview.events[0]["details"]["result"]["payload"]["doses"] == [1, 2, 1]
    assert session.state.artifacts["seal-0"].data().doses == (0, 0, 0)
    act(session, OperateAction(machine="trimmer", artifact="seal-0"))
    second = act(session, ProbeAction(machine="reader", artifact="seal-0"))
    assert second.events[0]["details"]["result"]["payload"]["reading"] == baseline
    assert session.state.artifacts["seal-0"].data().doses == (1, 2, 1)
    before = session.state.turn
    act(session, OperateAction(machine="anneal", artifact="seal-0"))
    assert session.state.turn == before + 1 and session.state.artifacts["seal-0"].data().doses == (
        0,
        0,
        0,
    )
    assert session.state.artifacts["seal-0"].data().reading is None


def test_failed_finish_uses_only_eligible_committed_joint_repair():
    session = Session(episode(seed=1, resource=0))
    take_all(session)
    apply_repair(session, WORLDS[0])
    act(session, DropAction(artifact="seal-2"))
    act(session, FinishAction())
    report = session.operator_snapshot()["performance"]["decision_diagnostics"]
    assert report["final_evidence"]["remaining_worlds"] == 216
    assert report["submissions"][0]["evidence"]["classification"] == "ineligible"
    act(session, TakeAction(artifact="seal-2"))
    act(session, FinishAction())
    report = session.operator_snapshot()["performance"]["decision_diagnostics"]
    assert report["final_evidence"]["remaining_worlds"] == 215
    assert report["submissions"][-1]["evidence"]["accepting_worlds"] == 1
    apply_repair(session, WORLDS[1])
    result = act(session, FinishAction())
    assert result.victory_code
    assert result.performance.decision_diagnostics.escape_classification == "compatible_win"
    assert result.performance.decision_diagnostics.final_evidence.remaining_worlds == 215


def test_control_and_dependent_independent_profiles_preserve_physics_and_budget():
    episodes = [episode(theory=t, discovery=d) for t, d in ((0, 0), (2, 3), (2, 4), (3, 3), (3, 4))]
    assert len({ep.investigation_truth.model_dump_json() for ep in episodes}) == 1
    assert len({ep.generation_metadata.action_budget for ep in episodes}) == 1
    assert len({runtime.expected(ep) for ep in episodes}) == 1
    assert len({ep.public.initial_state.model_dump_json() for ep in episodes}) == 1
    assert Belief(episodes[1].public.investigation.data()).counts() == (27, 27)
    assert Belief(episodes[-1].public.investigation.data()).counts() == (216, 216)


@pytest.mark.parametrize(
    "change", ["exponents", "repair", "truth", "budget", "evidence", "goal", "location"]
)
def test_episode_validation_rejects_tampered_public_private_contract(change):
    raw = episode(
        theory=0 if change == "repair" else 2, discovery=0 if change == "repair" else 4
    ).model_dump(mode="json")
    if change == "exponents":
        raw["public"]["investigation"]["payload"]["known_exponents"] = [1, 1, 1]
    elif change == "repair":
        raw["public"]["investigation"]["payload"]["repair"] = [[0, 0, 0]] * 3
    elif change == "truth":
        raw["investigation_truth"]["payload"]["mechanisms"][0]["shift"] = 2
    elif change == "budget":
        raw["public"]["initial_state"]["resources"]["actions_remaining"] += 1
    elif change == "evidence":
        raw["public"]["evidence_files"]["theory.json"] = "{}"
    elif change == "goal":
        raw["public"]["phase_modulus"] = 2
    else:
        raw["public"]["initial_state"]["artifacts"]["seal-0"]["location"] = "inventory"
    with pytest.raises(ValueError):
        PrivateEpisode.model_validate(raw)


@pytest.mark.parametrize("settings", [(3, 0), (0, 3), (0,), (0, 0, 0)])
def test_invalid_reader_setting_is_free_atomic_and_truth_independent(settings):
    responses = []
    for seed in (0, 1, 41, 215):
        session = Session(episode(seed=seed))
        before = canonical_hash(session.state)
        response = session.act(0, ConfigureAction(machine="reader", settings=settings))
        assert not response.ok and canonical_hash(session.state) == before
        responses.append(response.message)
    assert len(set(responses)) == 1


def test_fixed_panel_and_positive_certificate_are_separate_quantities():
    report = prove_profile(3, True)
    assert report["fixed_readings_exact"] == 15
    assert report["adaptive_reading_upper"] == 6
    assert report["positive_certificate_histogram"] == {3: 108, 4: 108}


@pytest.mark.slow
def test_public_policy_every_world_all_supported_profiles():
    for seed in range(216):
        for theory, discovery in ((0, 0), (2, 3), (2, 4), (3, 3), (3, 4)):
            ep = episode(seed=seed, theory=theory, discovery=discovery)
            session = Session(ep)
            result = public_policy(session, ep.public.evidence_files)
            assert (
                result.victory_code
                and result.current_turn <= ep.generation_metadata.guaranteed_policy_action_count
            )
            assert result.performance.decision_diagnostics.escape_classification == "supported_win"
