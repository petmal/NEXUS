"""Stateful inference must use committed physics and cannot benefit from a reset."""

from collections import deque
from itertools import product

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import (
    ConfigureAction,
    DropAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.ontology.stateful import runtime
from nexus.ontology.stateful.generation import TARGETS
from nexus.ontology.stateful.laws import DEAD, MODES, STATES, WORLD_INDEX, WORLDS, tables
from nexus.ontology.stateful.policy import public_policy
from nexus.ontology.stateful.proof import prove_kernel, prove_public_policy, scalar_step
from nexus.ontology.stateful.search import Planner, SearchLimit
from nexus.protocol.session import Session


def episode(seed=229, *, theory=3, discovery=5, planning=1, resource=1):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="stateful-discovery-v1",
        theory_level=theory,
        discovery_level=discovery,
        planning_level=planning,
        resource_pressure=resource,
        verifier_secret="stateful-test",
    )


def act(session, action):
    return session.act(expected_turn=session.status().turn, action=action)


def setup(session):
    assert act(session, TakeAction(artifact="seal")).ok
    if session.observe().room != "array":
        assert act(session, MoveAction(target="array")).ok


def test_complete_independent_kernel_and_all_world_public_policies():
    assert prove_kernel()["independent_transition_checks"] == 256 * 4 * 626
    for target in TARGETS:
        proof = prove_public_policy(target)
        assert proof["worlds"] == 256 and proof["all_finishes_supported"]
        assert proof["maximum_realized_actions"] + 2 <= 64


@pytest.mark.parametrize(
    "theory,discovery,planning,resource", [(0, 0, 1, 1), (0, 5, 1, 1), (3, 5, 1, 1), (3, 5, 0, 0)]
)
def test_live_policy_serialization_replay_and_private_qualification(
    theory, discovery, planning, resource
):
    ep = episode(theory=theory, discovery=discovery, planning=planning, resource=resource)
    ep = PrivateEpisode.model_validate_json(ep.model_dump_json())
    session = Session(ep)
    result = public_policy(session, ep.public.evidence_files)
    assert result.victory_code
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)
    assert qualify_episode(ep).passed


def test_probe_is_a_hypothetical_next_step_and_handling_cannot_reset():
    ep = episode(resource=0)
    session = Session(ep)
    setup(session)
    world = ep.investigation_truth.data()
    expected = (0, 0, 0, 0)
    for mode in (3, 2, 1, 0, 2, 1, 0):
        before = session.state.artifacts["seal"].model_dump()
        preview = act(session, ProbeAction(machine=MODES[mode], artifact="seal"))
        projected = scalar_step(world, expected, mode)
        payload = next(
            e["details"]["result"]["payload"] for e in preview.events if "result" in e["details"]
        )
        assert payload["reading"] == (5 if projected is None else projected[0])
        assert session.state.artifacts["seal"].model_dump() == before
        assert act(session, OperateAction(machine=MODES[mode], artifact="seal")).ok
        expected = projected
    before = session.state.artifacts["seal"].data()
    act(session, DropAction(artifact="seal"))
    act(session, TakeAction(artifact="seal"))
    assert session.state.artifacts["seal"].data() == before
    assert session.state.resources.actions_remaining is None
    assert not session.state.stocks


def test_invalid_controls_are_atomic_and_public_payload_contains_no_latent_registers():
    session = Session(episode())
    setup(session)
    for action in (
        TakeAction(artifact="stock"),
        ConfigureAction(machine="vek", settings=(1,)),
        OperateAction(machine="anneal", artifact="seal"),
    ):
        before = canonical_hash(session.state)
        assert not act(session, action).ok
        assert canonical_hash(session.state) == before
    assert set(session.state.artifacts["seal"].payload) == {"history", "reading"}
    public = episode().public.model_dump_json()
    assert "construction_seed" not in public and "verifier_secret" not in public
    assert episode().public.investigation.data().resolved is None


def test_display_match_is_not_the_joint_goal_and_rejected_finish_does_not_reset():
    session = Session(episode())  # gain0=2, target register0=1
    setup(session)
    for _ in range(3):
        act(session, OperateAction(machine="vek", artifact="seal"))
    assert session.state.artifacts["seal"].data().reading == 1
    before = session.state.artifacts["seal"].model_dump()
    result = act(session, FinishAction())
    assert not result.victory_code
    assert session.state.artifacts["seal"].model_dump() == before


def test_collapse_is_absorbing_even_in_r0():
    ep = episode(resource=0)
    w = WORLD_INDEX[ep.investigation_truth.data()]
    queue = deque([(0, ())])
    seen = {0}
    while queue:
        state, word = queue.popleft()
        if state == DEAD:
            break
        for a in range(4):
            child = tables()[w][a][state]
            if child not in seen:
                seen.add(child)
                queue.append((child, (*word, a)))
    else:
        pytest.fail("fixture has no collapse trajectory")
    session = Session(ep)
    setup(session)
    for a in word[:-1]:
        act(session, OperateAction(machine=MODES[a], artifact="seal"))
    mode = MODES[word[-1]]
    preview = act(session, ProbeAction(machine=mode, artifact="seal"))
    assert "would collapse" in preview.message and session.state.artifacts["seal"].payload["reading"] != 5
    applied = act(session, OperateAction(machine=mode, artifact="seal"))
    assert "has collapsed" in applied.message
    for mode in MODES:
        result = act(session, ProbeAction(machine=mode, artifact="seal"))
        assert (
            next(
                e["details"]["result"]["payload"]["reading"]
                for e in result.events
                if "result" in e["details"]
            )
            == 5
        )
        act(session, OperateAction(machine=mode, artifact="seal"))
    assert session.state.artifacts["seal"].data().reading == 5
    assert not act(session, FinishAction()).victory_code


def test_truth_aware_lucky_escape_remains_compatible_not_supported():
    ep = episode()
    session = Session(ep)
    for action in runtime.physical_plan(ep):
        result = act(session, action)
    assert result.victory_code
    assert result.performance.decision_diagnostics.escape_classification == "compatible_win"


def test_known_law_minima_match_physical_oracle_and_unknown_search_fails_closed():
    for w in (0, 219, 255):
        p = Planner((1, 2, 1, 2), WORLDS[w])
        assert p.supported_minimum(w) == p.distance[w][0] + 1
        assert p.supported_trace(w, operations_only=True)[0] == p.distance[w][0]
    p = Planner((1, 2, 1, 2))
    with pytest.raises(SearchLimit):
        p.blind_possible(p.initial, 20, max_nodes=1)


def test_blind_qualification_includes_success_aware_repeated_finish():
    # World0 can finish now; world1 needs vek. Moving first destroys world0's
    # goal. A single final guess is weaker than finish -> vek -> finish.
    target = (1, 2, 1, 2)
    p = Planner(target)
    belief = ((0, 182), (1, 432))
    assert STATES[182] == target
    assert scalar_step(WORLDS[1], STATES[432], 0) == target
    for length in range(3):
        for word in product(range(4), repeat=length):
            outcomes = []
            for world, state in belief:
                value = STATES[state]
                for mode in word:
                    value = scalar_step(WORLDS[world], value, mode)
                outcomes.append(value)
            assert any(value != target for value in outcomes)
    assert not p.blind_possible(belief, 2)
    assert p.blind_possible(belief, 3)
    assert p.strong(belief, 3)


@pytest.mark.parametrize("discovery", [0, 5])
def test_known_law_control_with_nine_operation_route(discovery):
    ep = episode(21, theory=0, discovery=discovery)
    assert len(runtime.expected(ep)) == 9
    session = Session(ep)
    result = public_policy(session, ep.public.evidence_files)
    assert result.victory_code and result.current_turn == 12
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)


@pytest.mark.parametrize("field", ["description", "evidence", "stock", "truth", "certificate"])
def test_tampered_compiled_contract_is_rejected(field):
    data = episode().model_dump(mode="json")
    if field == "description":
        data["public"]["description"] += " changed"
    elif field == "evidence":
        data["public"]["evidence_files"]["theory.json"] = "{}"
    elif field == "stock":
        data["public"]["initial_state"]["artifacts"]["seal"]["payload"]["reading"] = 1
    elif field == "truth":
        data["investigation_truth"]["payload"]["gains"][0] = 1
    else:
        data["generation_metadata"]["guaranteed_policy_action_count"] = 1
    with pytest.raises(ValueError):
        PrivateEpisode.model_validate(data)


def test_matrix_cannot_disguise_resource_or_disclosure_changes():
    import json
    from pathlib import Path

    from nexus.evaluation.stateful import Pilot

    data = json.loads((Path(__file__).parents[2] / "docs/stateful-matrix.json").read_text())
    assert len(Pilot.model_validate(data).runs) == 10
    data["runs"][3]["theory"] = 0
    with pytest.raises(ValueError):
        Pilot.model_validate(data)
