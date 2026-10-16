"""Independent set-based oracle for overlapping repair certificate bounds."""

import random
from itertools import combinations_with_replacement

from nexus.solver.decision_audit import DecisionAudit


def test_positive_certificate_matches_small_exhaustive_set_oracle():
    rng = random.Random(20261016)
    for _ in range(60):
        worlds = 6
        rows = tuple(bytes(rng.randrange(3) for _ in range(worlds)) for _ in range(5))
        # Singleton decisions ensure solvability, overlapping sets prevent a partition assumption.
        winning = tuple(1 << i for i in range(worlds)) + tuple(
            rng.randrange(1, 1 << worlds) for _ in range(4)
        )
        data = DecisionAudit(worlds, rows, winning)
        for actual in range(worlds):
            expected = 3
            for depth in range(3):
                for chosen in combinations_with_replacement(range(len(rows)), depth):
                    possible = {
                        i
                        for i in range(worlds)
                        if all(rows[q][i] == rows[q][actual] for q in chosen)
                    }
                    if any(all(win >> i & 1 for i in possible) for win in winning):
                        expected = depth
                        break
                if expected < 3:
                    break
            assert data.positive_reading_lower(actual) == expected
