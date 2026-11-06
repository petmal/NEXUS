"""Independent checks of receipts, cost certificates and performance inputs."""

import base64
import hashlib
import hmac
import json
from collections import Counter
from itertools import combinations, product

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.engine.replay import execute_with_trace, replay
from nexus.generator import generate_episode
from nexus.models.actions import ACTION_ADAPTER, FinishAction, ObserveAction, TakeAction, WaitAction
from nexus.models.goals import GoalPredicate
from nexus.models.world import TerminalStatus
from nexus.ontology.catalog import runtime_for
from nexus.protocol.session import Session
from nexus.protocol.transport import _validation_result
from nexus.verification.receipt import victory_receipt


def test_receipt_matches_independent_standard_hmac_and_binds_every_identity_field():
    episode = generate_episode(17, planning_level=0, verifier_secret="audit-secret-λ")
    episode.public.episode_id = "audit-世界"
    payload = {"protocol_version": episode.public.protocol_version,
               "episode_id": episode.public.episode_id,
               "goal": episode.public.goal.model_dump(mode="json"), "status": "VICTORY"}
    wire = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    digest = hmac.digest("audit-secret-λ".encode(), wire, hashlib.sha256)[:10]
    token = base64.b32encode(digest).decode()
    expected = "NX-" + "-".join(token[i:i + 4] for i in range(0, 16, 4))
    assert victory_receipt(episode) == expected
    assert victory_receipt(type(episode).model_validate_json(episode.model_dump_json())) == expected
    for field in ("secret", "episode", "protocol", "goal"):
        changed = episode.model_copy(deep=True)
        if field == "secret":
            changed.verifier_secret += "changed"
        elif field == "episode":
            changed.public.episode_id += "changed"
        elif field == "protocol":
            changed.public.protocol_version += "changed"
        else:
            changed.public.goal = GoalPredicate(kind="phase_equals", value=0)
        assert victory_receipt(changed) != expected
        assert not _validation_result(expected, "won", victory_receipt(changed))["correct"]


def test_only_successful_finish_issues_receipt_even_at_exact_budget_boundary():
    episode = generate_episode(17, planning_level=0, verifier_secret="terminal-audit")
    plan = [ACTION_ADAPTER.validate_python(a) for a in episode.reference_plan]
    episode.public.initial_state.resources.actions_remaining = len(plan)
    final, trace = execute_with_trace(episode, plan)
    assert final.terminal_status == TerminalStatus.WON
    assert final.resources.actions_remaining == 0
    assert all(record.victory_code is None for record in trace[:-1])
    receipt = trace[-1].victory_code
    assert receipt == victory_receipt(episode)
    assert _validation_result(receipt, "won", receipt)["correct"]
    for status in ("active", "failed"):
        assert not _validation_result(receipt, status, receipt)["correct"]
    for action in (FinishAction(), WaitAction(), ObserveAction()):
        result = step(final, action, episode)
        assert not result.ok and not result.victory_code
        assert canonical_hash(result.state) == canonical_hash(final)
    damaged = [*trace[:-1], trace[-1].model_copy(update={"victory_code": "NX-FORGED"})]
    with pytest.raises(ValueError, match="victory-code"):
        replay(episode, damaged)
    episode.public.initial_state.resources.actions_remaining = len(plan) - 1
    failed, prefix = execute_with_trace(episode, plan[:-1])
    assert failed.terminal_status == TerminalStatus.FAILED
    assert all(record.victory_code is None for record in prefix)
    assert not step(failed, plan[-1], episode).victory_code


CASES = [
    ("stateful-planning-v1", 21, 0, 5, 3, 2),
    ("stateful-interference-v1", 67, 0, 0, 0, 2),
    ("stateful-coordination-v1", 41, 0, 0, 0, 2),
    ("compositional-repair-v1", 438, 3, 5, 1, 1),
    ("model-revision-v1", 5866, 3, 5, 0, 1),
]


@pytest.mark.parametrize("family,seed,theory,discovery,planning,resource", CASES)
def test_terminal_metrics_count_committed_actions_and_preserve_world(
    family, seed, theory, discovery, planning, resource,
):
    episode = generate_episode(seed, axis_version=2, science_family=family,
                               theory_level=theory, discovery_level=discovery,
                               planning_level=planning, resource_pressure=resource)
    session = Session(episode)
    assert session.act(0, ObserveAction()).ok
    assert not session.act(0, TakeAction(artifact="missing")).ok
    actions = runtime_for(episode.public.investigation).physical_plan(episode)
    assert actions
    for turn, action in enumerate(actions):
        result = session.act(turn, action)
        assert result.ok
        if turn == 0:
            assert session.act(turn, action).duplicate
            assert not session.act(turn, WaitAction()).ok
    assert result.victory_code and result.performance
    before = canonical_hash(session.state)
    snapshot = session.operator_snapshot()
    assert canonical_hash(session.state) == before
    metrics = snapshot["performance"]
    assert metrics["terminal_status"] == "won"
    assert metrics["actions_used"] == len(actions) == len(session.trace) == session.state.turn
    assert metrics["action_counts"] == dict(Counter(action.type for action in actions))
    assert metrics["invalid_actions"] == metrics["duplicate_requests"] == metrics["protocol_conflicts"] == 1
    assert metrics["initial_action_budget"] - metrics["budget_remaining"] == len(actions)
    assert metrics["measurements_used"] == metrics["informative_measurements"] + metrics["redundant_measurements"]
    assert metrics["mission_submissions"] == 1 and metrics["failed_finishes"] == 0
    assert metrics["first_submission_correct"] and metrics["final_submission_correct"]
    assert canonical_hash(replay(episode, session.trace)) == before


@pytest.mark.parametrize("coupling", ["independent", "coupled"])
def test_interference_continuation_certifies_all_vectors_with_scalar_bellman_equations(coupling):
    from nexus.ontology.interference.planner import continuation_distances
    from nexus.ontology.interference.proof import scalar_step

    episode = generate_episode(67, axis_version=2, science_family="stateful-interference-v1",
                               theory_level=0, discovery_level=0, planning_level=0,
                               resource_pressure=2, ontology_options={"coupling": coupling})
    spec = episode.public.investigation.data()
    costs = continuation_distances(spec)

    def cost(vector):
        value = costs[sum(v * 5**i for i, v in enumerate(vector))]
        return float("inf") if value == -1 else value

    for vector in product(range(5), repeat=6):
        value = cost(vector)
        assert value == (0 if vector == spec.target else
                         1 + min(cost(scalar_step(spec, vector, mode)) for mode in range(6)))


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


def test_every_two_state_binary_machine_pair_matches_bounded_word_oracle():
    from nexus.solver.finite_machine import FiniteMachine

    machines = [FiniteMachine(outputs, transitions)
                for outputs in product(range(2), repeat=2)
                for transitions in product(tuple(product(range(2), repeat=2)), repeat=2)]
    words = [word for length in range(4) for word in product(range(2), repeat=length)]

    def read(machine, word):
        state = 0
        for symbol in word:
            state = machine.transitions[symbol][state]
        return machine.outputs[state]

    signatures = [machine.signature() for machine in machines]
    observations = [[read(machine, word) for word in words] for machine in machines]
    # A shortest distinguishing word cannot revisit a product state. There
    # are four product states, so length <= 3 covers all-history inequivalence.
    for i, left in enumerate(machines):
        for j, right in enumerate(machines):
            differing = next((word for word, a, b in zip(words, observations[i], observations[j])
                              if a != b), None)
            assert left.counterexample(right) == differing
            assert (signatures[i] == signatures[j]) == (differing is None)


def test_supporting_certificate_matches_all_subsets_on_small_overlapping_priors():
    from nexus.evaluation.goal_information import minimum_supporting_certificate

    # Each mask contains actual world zero. Other worlds can share overlapping
    # accepted decisions; identifying the entire truth need not be necessary.
    for outcomes in product((1, 3, 5, 7), repeat=3):
        for winning in product((1, 3, 5, 7), repeat=2):
            minimum = None
            for size in range(4):
                for chosen in combinations(range(3), size):
                    remaining = 7
                    for index in chosen:
                        remaining &= outcomes[index]
                    if any(remaining & decision == remaining for decision in winning):
                        minimum = size
                        break
                if minimum is not None:
                    break
            if minimum is None:
                with pytest.raises(ValueError, match="no guaranteed decision"):
                    minimum_supporting_certificate(7, outcomes, winning)
            else:
                witness = minimum_supporting_certificate(7, outcomes, winning)
                assert len(witness) == minimum
                remaining = 7
                for index in witness:
                    remaining &= outcomes[index]
                assert any(remaining & decision == remaining for decision in winning)
