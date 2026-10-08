"""Exact information-only experiment costs for small, fully enumerated research problems.

No navigation, resource mutation, model reasoning, or forced stage order is implied.
Rows refer to the same complete hypothesis order; outputs/predictions are integer symbols.
"""
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class FiniteExperimentProblem:
    hypotheses: tuple[str, ...]
    experiments: tuple[tuple[str, tuple[int, ...]], ...]
    predictions: tuple[int, ...]

    def __post_init__(self):
        size = len(self.hypotheses)
        names = [name for name, _ in self.experiments]
        if not 1 <= size <= 64 or len(set(self.hypotheses)) != size:
            raise ValueError("expected 1–64 unique hypotheses")
        if len(names) > 12 or len(set(names)) != len(names):
            raise ValueError("expected at most 12 uniquely named experiments")
        if len(self.predictions) != size or any(len(row) != size for _, row in self.experiments):
            raise ValueError("experiment and prediction rows must align with hypotheses")

    def compatible(self, observations: tuple[tuple[str, int], ...] = ()) -> tuple[int, ...]:
        rows = dict(self.experiments)
        if any(name not in rows for name, _ in observations):
            raise ValueError("unknown experiment")
        result = tuple(i for i in range(len(self.hypotheses))
                       if all(rows[name][i] == value for name, value in observations))
        if not result:
            raise ValueError("observations contradict the complete prior")
        return result

    def possible_predictions(self, observations: tuple[tuple[str, int], ...] = ()) -> frozenset[int]:
        return frozenset(self.predictions[i] for i in self.compatible(observations))

    def minimum_guaranteed_measurements(self, observations: tuple[tuple[str, int], ...] = ()) -> int | None:
        @lru_cache(maxsize=None)
        def cost(belief: tuple[int, ...]) -> int | None:
            if len({self.predictions[i] for i in belief}) == 1:
                return 0
            best = None
            for _, outcomes in self.experiments:
                groups: dict[int, list[int]] = {}
                for i in belief:
                    groups.setdefault(outcomes[i], []).append(i)
                if len(groups) == 1:
                    continue
                children = [cost(tuple(group)) for group in groups.values()]
                if all(value is not None for value in children):
                    candidate = 1 + max(children)
                    best = candidate if best is None else min(best, candidate)
            return best
        return cost(self.compatible(observations))
