"""Independent physics and proof limits, exact joint inference and committed state."""

import json
import runpy
from collections import Counter
from itertools import product
from pathlib import Path

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
from nexus.ontology.history import runtime
from nexus.ontology.history.inference import Belief, common, indices, partitions
from nexus.ontology.history.laws import (
    LAWS,
    PULSES,
    READERS,
    STATES,
    WORLDS,
    accepted,
    decisions,
    observed,
    pulse,
    shortest,
    word_index,
    words,
)
from nexus.ontology.history.policy import bound, choose, public_policy
from nexus.protocol.session import Session

ORACLE = runpy.run_path(str(Path(__file__).parents[2] / "scripts/history_oracle.py"))


def episode(seed=0, control=False, planning=0, resource=1, profile="standard"):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="history-coupled-v1",
        theory_level=0 if control else 3,
        discovery_level=0 if control else 5,
        planning_level=planning,
        resource_pressure=resource,
        budget_profile=profile,
        verifier_secret="history-test",
    )


def act(session, action):
    response = session.act(expected_turn=session.state.turn, action=action)
    assert response.ok, response.message
    return response


def test_every_transition_independent_and_reversible_all_worlds_reachable():
    for gates in LAWS:
        for mode in range(4):
            row = [ORACLE["pulse"](gates, state, mode) for state in STATES]
            assert len(set(row)) == 81
            assert row == [pulse(gates, state, mode) for state in STATES]
        paths = ORACLE["explore"](gates)
        assert len(paths) == 81
        for a, b in product((1, 2), repeat=2):
            assert len(paths[(a, 2 * b % 3, 1, 2)]) <= 8
    assert dict(Counter(len(shortest(w)) for w in WORLDS)) == {2: 128, 3: 280, 4: 483, 5: 131, 6: 2}


def test_all_word_indexing_and_orientation_disjoint_winning_sets():
    table = decisions()
    assert all(word_index(word) == i for i, word in enumerate(words()))
    assert len(set(table.winning)) == 1024
    for law in range(256):
        for a, b in product(range(4), repeat=2):
            if a != b:
                assert not table.winning[law * 4 + a] & table.winning[law * 4 + b]
    assert max(mask.bit_count() for mask in table.accepting) == 96


def test_compiled_observations_match_independent_physical_clamps():
    # Every normalized physical state: clamps are physical H/K=1, not h/k=1.
    for law, gates in enumerate(LAWS):
        for state, history in ORACLE["explore"](gates).items():
            if len(history) > 8:
                continue
            for a, b in product((1, 2), repeat=2):
                wi = law * 4 + (a - 1) * 2 + b - 1
                for channel in range(3):
                    copied = state
                    if channel:
                        h, k, x, y = state
                        copied = (a if channel == 1 else h, b if channel == 2 else k, x, y)
                        copied = ORACLE["pulse"](gates, ORACLE["pulse"](gates, copied, 2), 3)
                    x, y = copied[2:]
                    assert partitions(history, channel)[x * 3 + y] >> wi & 1


def test_public_reference_all_worlds_against_independent_equations():
    assert bound((1 << 1024) - 1) == (5, 31)
    for wi, world in enumerate(WORLDS):
        mask = (1 << 1024) - 1
        count = cost = 0
        while (query := choose(mask)) is not None:
            history, channel = query
            state = (0, 0, 0, 0)
            for n, mode in enumerate(history, start=1):
                state = ORACLE["pulse"](world.gates, state, mode)
                mask &= partitions(history[:n], 0)[state[2] * 3 + state[3]]
                assert mask >> wi & 1
            if channel:
                h, k, x, y = state
                state = (world.a if channel == 1 else h, world.b if channel == 2 else k, x, y)
                state = ORACLE["pulse"](world.gates, ORACLE["pulse"](world.gates, state, 2), 3)
            mask &= partitions(history, channel)[state[2] * 3 + state[3]]
            assert mask >> wi & 1
            count += 1
            cost += len(history) + 2
        word = words()[next(indices(common(mask)))]
        assert accepted(world, word)
        assert count <= 5 and cost + len(word) <= 31


def test_reachable_unique_marginal_modes_can_be_jointly_impossible():
    mask = (1 << 1024) - 1
    truth = WORLDS[260]
    for history, channel in (((0, 1, 0, 3), 2), ((0, 2, 2, 2), 0), ((0, 2, 1), 1)):
        # Include every publicly emitted preparation result, not just final readout.
        for h, c in [*((history[:n], 0) for n in range(1, len(history) + 1)), (history, channel)]:
            x, y = observed(truth, h, c)
            mask &= partitions(h, c)[x * 3 + y]
    vectors = [(*WORLDS[i].gates, WORLDS[i].a, WORLDS[i].b) for i in indices(mask)]
    modal = []
    for values in zip(*vectors):
        counts = Counter(values).most_common()
        assert len(counts) == 1 or counts[0][1] > counts[1][1]
        modal.append(counts[0][0])
    assert len(vectors) == 14 and tuple(modal) == (1, 3, 0, 3, 1, 1)
    assert tuple(modal) not in vectors


@pytest.mark.parametrize(
    "control,planning,resource,profile",
    [
        (False, 0, 1, "standard"),
        (False, 1, 1, "diagnostic-plus6"),
        (True, 1, 1, "standard"),
        (False, 0, 0, "standard"),
    ],
)
def test_live_policy_replay_and_supported_terminal_diagnostics(
    control, planning, resource, profile, caplog
):
    ep = episode(control=control, planning=planning, resource=resource, profile=profile)
    session = Session(ep)
    with caplog.at_level("INFO", logger="nexus.diagnostics"):
        result = public_policy(session, ep.public.evidence_files)
    assert (
        result.victory_code
        and result.current_turn <= ep.generation_metadata.guaranteed_policy_action_count
    )
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    assert "history_operations" in caplog.text
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)
    assert qualify_episode(ep).passed


def test_probe_reader_anneal_and_invalid_pulses_are_transactional():
    ep = episode(resource=0)
    session = Session(ep)
    act(session, TakeAction(artifact="seal"))
    for name in PULSES:
        before = session.state.artifacts["seal"].model_dump(mode="json")
        result = act(session, ProbeAction(machine=name, artifact="seal"))
        assert session.state.artifacts["seal"].model_dump(mode="json") == before
        assert result.performance is None
    for mode in (0, 2, 1, 3):
        act(session, OperateAction(machine=PULSES[mode], artifact="seal"))
    before = session.state.artifacts["seal"].data()
    for name in READERS:
        act(session, OperateAction(machine=name, artifact="seal"))
        after = session.state.artifacts["seal"].data()
        assert (after.history, after.visible) == (before.history, before.visible)
        assert set(after.model_dump()) == {"history", "visible", "reading", "channel"}
    for _ in range(4):
        act(session, OperateAction(machine="vek", artifact="seal"))
    before = canonical_hash(session.state)
    for action in (
        OperateAction(machine="vek", artifact="seal"),
        ProbeAction(machine="tor", artifact="seal"),
        ConfigureAction(machine="vek", settings=(0,)),
    ):
        result = session.act(expected_turn=session.state.turn, action=action)
        assert not result.ok and canonical_hash(session.state) == before
    act(
        session, ProbeAction(machine="h-scope", artifact="seal")
    )  # reader internals remain legal at limit
    act(session, OperateAction(machine="anneal", artifact="seal"))
    assert session.state.artifacts["seal"].data().history == ()
    assert session.state.artifacts["seal"].data().visible == (0, 0)


def test_tracker_ignores_counterfactuals_and_ineligible_failure_does_not_refute():
    ep = episode()
    session = Session(ep)
    tracker = runtime.mission_tracker(ep.public)
    act(session, TakeAction(artifact="seal"))
    act(session, ProbeAction(machine="tor", artifact="seal"))
    for record in session.trace:
        tracker.observe(record)
    assert tracker.attempted() == ()
    for mode in runtime.expected(ep):
        act(session, OperateAction(machine=PULSES[mode], artifact="seal"))
    act(session, DropAction(artifact="seal"))
    assert not act(session, FinishAction()).victory_code
    act(session, TakeAction(artifact="seal"))
    result = act(session, FinishAction())
    assert result.victory_code
    submissions = result.performance.decision_diagnostics.submissions
    assert submissions[0].evidence.classification == "ineligible"
    assert submissions[1].evidence.classification in ("guaranteed", "compatible")


def test_failed_finish_excludes_all_accepting_worlds_and_preserves_true_world():
    ep = episode(resource=0)
    truth = ep.investigation_truth.data()
    belief = Belief(ep.public.investigation.data())
    wrong = next(
        word
        for word, mask in zip(words(), decisions().accepting)
        if mask and not accepted(truth, word)
    )
    before = belief.mask
    belief.exclude_target(wrong)
    assert belief.mask == before & ~decisions().accepting[word_index(wrong)]
    assert belief.accepting_count(wrong) == 0
    assert belief.mask >> WORLDS.index(truth) & 1


def test_controls_generous_profile_and_strict_episode_contract():
    regular = episode()
    control = episode(control=True)
    generous = episode(profile="diagnostic-plus6")
    assert (
        regular.investigation_truth == control.investigation_truth == generous.investigation_truth
    )
    assert regular.generation_metadata.action_budget == control.generation_metadata.action_budget
    assert (
        generous.generation_metadata.action_budget == regular.generation_metadata.action_budget + 6
    )
    assert regular.public.evidence_files == generous.public.evidence_files
    data = regular.model_dump(mode="json")
    data["public"]["initial_state"]["artifacts"]["seal"]["payload"]["H"] = 1
    with pytest.raises(ValueError):
        PrivateEpisode.model_validate(data)
    assert "configure" not in {x["type"] for x in runtime.public_contract(None)["reference"]}
    assert (
        json.loads(regular.public.evidence_files["theory.json"])["specification"]["resolved"]
        is None
    )


def test_public_action_schema_matches_supported_controls():
    contract = runtime.public_contract(None)
    assert set(contract["schema"]["discriminator"]["mapping"]) == {
        item["type"] for item in contract["reference"]
    }
