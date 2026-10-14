import json
from dataclasses import asdict, replace
from fractions import Fraction
from itertools import combinations, product

import pytest
from pydantic import TypeAdapter

from nexus.solver.finite_game import (
    FiniteGame,
    PolicyProof,
    Program,
    SearchBudget,
    Transition,
    analyze,
)
from nexus.solver.policy_check import InvalidProof, check_proof


def query_game(targets, queries, *, repairs=None, weights=None, recover=False, query_cost=1):
    """Independent static-test compiler; failed guesses optionally remain live."""
    n = len(targets)
    if repairs is None:
        repairs = tuple(
            frozenset(i for i, target in enumerate(targets) if target == value)
            for value in sorted(set(targets))
        )
    weights = weights or (1,) * n
    rows = []
    for h in range(n):
        row = [Transition(h, str(q[h]), query_cost) for q in queries]
        row += [
            Transition(
                n if h in repair else h if recover else n + 1, "won" if h in repair else "rejected"
            )
            for repair in repairs
        ]
        rows.append(tuple(row))
    actions = tuple(f"query-{i}" for i in range(len(queries))) + tuple(
        f"commit-{i}" for i in range(len(repairs))
    )
    rows.extend(tuple(Transition(s, "terminal", 0) for _ in actions) for s in (n, n + 1))
    return FiniteGame(
        "static-test-v1",
        "complete-static-prior",
        actions,
        ("active",) * n + ("won", "failed"),
        tuple(rows),
        tuple(enumerate(weights)),
    )


def exact(game, budget, rounds):
    result = analyze(game, budget=budget, rounds=rounds)
    assert result.status == "exact", result.reason
    assert result.proof is not None
    check_proof(game, result.proof)
    return result.proof


def test_three_readings_do_not_prove_three_feedback_rounds():
    worlds = tuple(product((0, 1), repeat=5))
    targets = tuple((w[0], w[1 + 2 * w[0]], w[2 + 2 * w[0]]) for w in worlds)
    queries = tuple(tuple(w[q] for w in worlds) for q in range(5))
    game = query_game(targets, queries)
    two = exact(game, 4, 2)  # Three readings plus the actual final commitment.
    assert two.success_mass == two.total_mass
    one = exact(game, 4, 1)
    assert one.success_mass < one.total_mass


def test_original_routing_fixture_fails_shallow_success_ceiling_and_extra_action():
    addresses = tuple(p for d in range(3) for p in product((0, 1), repeat=d))
    index = {p: i for i, p in enumerate(addresses)}
    worlds = tuple(product((0, 1), repeat=7))
    targets = []
    for world in worlds:
        path = ()
        for _ in range(3):
            path += (world[index[path]],)
        targets.append(path)
    game = query_game(targets, tuple(tuple(w[q] for w in worlds) for q in range(7)))
    two = exact(game, 4, 2)
    assert Fraction(two.success_mass, two.total_mass) == Fraction(3, 4)
    assert exact(game, 5, 2).success_mass == 128
    assert exact(game, 4, 3).success_mass == 128


def test_overlapping_repair_obstruction_is_not_pairwise_identification():
    repairs = ({0, 1}, {0, 2}, {1, 2})
    assert all(any(set(pair) <= r for r in repairs) for pair in combinations(range(3), 2))
    game = query_game((0, 1, 2), (), repairs=repairs)
    proof = exact(game, 1, 0)
    assert Fraction(proof.success_mass, proof.total_mass) == Fraction(2, 3)
    universal = query_game((0, 1, 2), (), repairs=(*repairs, {0, 1, 2}))
    assert exact(universal, 1, 0).success_mass == 3


def test_fixed_guess_sequence_and_terminal_halt_use_no_feedback_rounds():
    game = query_game((0, 1, 2), (), recover=True)
    assert exact(game, 2, 0).success_mass == 2
    assert exact(game, 3, 0).success_mass == 3


def test_zero_cost_informative_response_and_noop_cycle_are_included():
    game = query_game((0, 1), ((0, 0), (0, 1)), query_cost=0)
    assert exact(game, 1, 0).success_mass == 1
    assert exact(game, 1, 1).success_mass == 2


def test_changed_prior_reoptimizes_and_preserves_mass():
    game = query_game((0, 1, 1), (), weights=(6, 2, 2))
    proof = exact(game, 1, 0)
    assert (proof.success_mass, proof.total_mass) == (6, 10)
    shifted = replace(game, initial=((0, 4), (1, 3), (2, 3)))
    assert exact(shifted, 1, 0).success_mass == 6
    with pytest.raises(InvalidProof, match="identity"):
        check_proof(shifted, proof)


def test_checker_rejects_missing_payload_despite_matching_digest():
    game = query_game((0, 1, 2, 3), ((0, 0, 1, 1),))
    proof = exact(game, 2, 1)
    assert proof.success_mass == 2
    partial = replace(proof, bounds=tuple(b for b in proof.bounds if b.rounds == 1))
    with pytest.raises(InvalidProof, match="missing continuation"):
        check_proof(game, partial)
    with pytest.raises(InvalidProof):
        check_proof(game, replace(proof, rounds=0))


def test_checker_rejects_omitted_witness_branch_and_forged_upper_bound():
    game = query_game((0, 1, 2, 3), ((0, 0, 1, 1),))
    proof = exact(game, 2, 1)
    assert proof.witness.branches
    bad = replace(proof, witness=replace(proof.witness, branches=proof.witness.branches[:1]))
    with pytest.raises(InvalidProof, match="branches"):
        check_proof(game, bad)
    # Claim no win with a no-op witness: replay alone would accept this false upper bound.
    bad = replace(
        proof,
        success_mass=0,
        witness=Program(),
        bounds=tuple(replace(b, success_mass=0) for b in proof.bounds),
    )
    with pytest.raises(InvalidProof, match="inequality"):
        check_proof(game, bad)


def test_proof_payload_round_trip_and_explicit_unknown():
    game = query_game((0, 1), ((0, 1),))
    proof = exact(game, 2, 1)
    restored = TypeAdapter(PolicyProof).validate_json(json.dumps(asdict(proof)))
    check_proof(game, restored)
    unknown = analyze(game, budget=2, rounds=1, limits=SearchBudget(max_states=1))
    assert unknown.status == "unknown" and unknown.proof is None and unknown.reason


def test_table_requires_every_state_request_pair_and_last_action_can_win():
    game = query_game((0,), ())
    assert exact(game, 1, 0).success_mass == 1
    assert exact(game, 0, 0).success_mass == 0
    with pytest.raises(ValueError, match="every state/request"):
        replace(game, transitions=((), *game.transitions[1:]))
    with pytest.raises(ValueError, match="prior mass"):
        replace(game, initial=((0, True),))


def test_recovery_must_use_one_public_policy_for_indistinguishable_successors():
    game = query_game((0, 1), ())
    assert all(any(game.terminal[t.state] == "won" for t in game.transitions[h]) for h in (0, 1))
    proof = exact(game, 1, 10)
    assert proof.success_mass == 1


def test_destructive_preparation_preserves_hidden_world_and_prior_mass():
    # Preparation is necessary, measurement erases its source, but its earlier
    # reply still identifies the correct repair. No resampling after changes.
    rows = []
    for state in range(8):
        h = state % 2
        rows.append(tuple(Transition(7, "invalid") for _ in range(4)))
        if state < 6:
            rows[state] = (
                Transition(2 + h, "prepared") if state < 2 else Transition(7, "spent"),
                Transition(4 + h, str(h)) if state in (2, 3) else Transition(7, "unprepared"),
                Transition(6 if state == 4 else 7, "accepted" if state == 4 else "rejected"),
                Transition(6 if state == 5 else 7, "accepted" if state == 5 else "rejected"),
            )
    game = FiniteGame(
        "destructive",
        "same-public-start",
        ("prepare", "read", "repair-0", "repair-1"),
        ("active",) * 6 + ("won", "failed"),
        tuple(rows),
        ((0, 1), (0, 1), (1, 5)),
    )
    assert exact(game, 3, 0).success_mass == 5
    assert exact(game, 3, 1).success_mass == 7
    assert exact(game, 2, 2).success_mass == 0


def test_time_limit_includes_duplicate_successors(monkeypatch):
    from nexus.solver import finite_game
    from nexus.solver.finite_game import SearchLimit

    game = FiniteGame(
        "wide",
        "same",
        tuple(map(str, range(100))),
        ("active",),
        (tuple(Transition(0, "same", 0) for _ in range(100)),),
        ((0, 1),),
    )
    proof = exact(game, 1, 0)
    clock = iter(i / 100 for i in range(10000))
    monkeypatch.setattr(finite_game, "monotonic", lambda: next(clock))
    result = analyze(game, budget=1, rounds=0, limits=SearchBudget(max_seconds=0.03))
    assert result.status == "unknown" and result.proof is None
    with pytest.raises(SearchLimit):
        check_proof(game, proof, limits=SearchBudget(max_seconds=0.03))


def test_recursion_exhaustion_is_unknown():
    game = FiniteGame(
        "cycle",
        "same",
        ("switch",),
        ("active", "active"),
        ((Transition(1, "same", 0),), (Transition(0, "same", 0),)),
        ((0, 1),),
    )
    result = analyze(game, budget=1, rounds=1000)
    assert result.status == "unknown" and result.proof is None
