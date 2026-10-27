"""The rejected ternary prototype stays bounded and operator-only."""

from collections import Counter

import pytest

from nexus.evaluation.ternary_feasibility import (
    ATTEMPTS,
    COUNT,
    SEEDS,
    SIZE,
    VARIANTS,
    kernels,
    macro_distances,
    scalar_step,
    tables,
    wiring,
)
from nexus.ontology import structural


@pytest.mark.parametrize("variant", VARIANTS)
def test_matched_degree_and_independent_scalar_transition_contract(variant):
    _, kernel = next(kernels(SEEDS[0]))
    for coupled in (False, True):
        coordinates = wiring(coupled, variant)
        assert Counter(g for g, _ in coordinates) == Counter(range(COUNT))
        assert Counter(s for _, s in coordinates) == Counter(range(COUNT))
        assert all(i != s for i, (_, s) in enumerate(coordinates))
        if not coupled:
            assert all(i // 3 == g // 3 == s // 3 for i, (g, s) in enumerate(coordinates))
        rows = tables(kernel, coupled, variant)
        for state in range(0, SIZE, 127):
            vector = tuple(state // (3**i) % 3 for i in range(COUNT))
            for mode in range(COUNT):
                expected = scalar_step(kernel, coupled, variant, vector, mode)
                assert rows[mode][state] == sum(v * 3**i for i, v in enumerate(expected))
        assert macro_distances(rows) == structural.machine_block_distances(rows)
        for row in rows:
            if variant == "self-guard":
                assert all(row[row[s]] == row[s] for s in range(SIZE))
            else:
                assert all(row[row[row[s]]] == s for s in range(SIZE))


def test_fixed_kernel_cohort_cannot_silently_substitute_seeds():
    assert SEEDS == (67, 79, 101, 103)
    assert ATTEMPTS == 32
    assert SIZE == 19683
    assert list(kernels(67)) == list(kernels(67))
    assert len(list(kernels(67))) == 32
    with pytest.raises(ValueError, match="unknown"):
        wiring(True, "unregistered")
