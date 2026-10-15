"""An independent exhaustive set oracle checks every claimed certificate bound."""

from functools import cache
from itertools import combinations, product
from random import Random

import pytest

from nexus.solver.observation_audit import AuditLimitError, ObservationAudit, labels


def brute_force(problem, world, maximum):
    for size in range(maximum + 1):
        for queries in combinations(range(len(problem.rows)), size):
            possible = {
                problem.predictions[i]
                for i in range(len(problem.predictions))
                if all(problem.rows[q][i] == problem.rows[q][world] for q in queries)
            }
            if len(possible) == 1:
                return size
    return None


def test_certificates_match_independent_exhaustion_with_target_equivalence():
    rng = Random(10415)
    for _ in range(100):
        worlds, queries = rng.randrange(2, 13), rng.randrange(1, 8)
        problem = ObservationAudit(
            tuple(rng.randrange(4) for _ in range(worlds)),
            tuple(bytes(rng.randrange(3) for _ in range(worlds)) for _ in range(queries)),
        )
        for maximum in (1, 2, 3):
            for world in range(worlds):
                result = problem.certificate(world, max_readings=maximum)
                exact = brute_force(problem, world, maximum)
                assert result.exact_minimum == exact
                assert result.lower_bound == (exact if exact is not None else maximum + 1)
                if exact is not None:
                    possible = {
                        problem.predictions[i]
                        for i in range(worlds)
                        if all(
                            problem.rows[q][i] == problem.rows[q][world]
                            for q in result.witness_rows
                        )
                    }
                    assert possible == {problem.predictions[world]}


def test_four_independent_bits_need_four_readings_even_for_an_oracle():
    worlds = tuple(product((0, 1), repeat=4))
    problem = ObservationAudit(
        tuple(range(16)), tuple(bytes(w[q] for w in worlds) for q in range(4))
    )
    for world in range(16):
        assert problem.certificate(world).lower_bound == 4
    assert problem.population_summary()["worst_case_reading_lower_bound"] == 4
    assert problem.best_guess_mass(problem.all_data_groups((0,))) == 2


def test_direct_query_and_equivalent_targets_defeat_false_depth():
    problem = ObservationAudit(
        (0, 1, 2, 3), (bytes((0, 0, 1, 1)), bytes((0, 1, 0, 1)), bytes(range(4)))
    )
    assert all(problem.certificate(i).exact_minimum == 1 for i in range(4))
    resolved = ObservationAudit((7, 7, 7), (bytes((0, 1, 2)),))
    assert resolved.certificate(1).exact_minimum == 0
    assert labels(((1, 2), (2, 1), (1, 2))) == (0, 1, 0)


def test_incomplete_search_and_misaligned_data_never_certify(monkeypatch):
    with pytest.raises(ValueError):
        ObservationAudit((1, 2), (b"\x00",))
    with pytest.raises(ValueError):
        ObservationAudit((True,), (b"\x00",))
    problem = ObservationAudit(tuple(range(4)), (bytes((0, 0, 1, 1)), bytes((0, 1, 0, 1))))
    with pytest.raises(ValueError):
        problem.certificate(True)
    with pytest.raises(ValueError):
        problem.all_data_groups((-1,))
    ticks = iter(range(100))
    monkeypatch.setattr("nexus.solver.observation_audit.monotonic", lambda: next(ticks))
    with pytest.raises(AuditLimitError):
        problem.certificate(0, max_seconds=0.1)


def test_guessing_bound_includes_interleaved_absorbing_success_branches():
    @cache
    def leaves(guesses, readings, fanout):
        if guesses == 0:
            return 0
        options = [1 + leaves(guesses - 1, readings, fanout)]
        if readings:
            options.append(fanout * leaves(guesses, readings - 1, fanout))
        return max(options)

    for guesses, readings, fanout in product(range(6), range(5), range(2, 5)):
        assert leaves(guesses, readings, fanout) <= guesses * fanout**readings
    # Nonuniform target classes must be weighted, not counted uniformly.
    problem = ObservationAudit((0, 0, 0, 1, 1, 2, 3), (bytes((0, 0, 0, 1, 1, 0, 1)),))
    assert (
        problem.guess_success_upper(maximum_guesses=1, maximum_readings=0)["correct_mass_upper"]
        == 3
    )
    assert (
        problem.guess_success_upper(maximum_guesses=1, maximum_readings=1)["correct_mass_upper"]
        == 5
    )
    assert (
        problem.guess_success_upper(maximum_guesses=0, maximum_readings=5)["correct_mass_upper"]
        == 0
    )
