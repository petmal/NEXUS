"""Exact information-only experiment costs for small, fully enumerated research problems.

No navigation, resource mutation, model reasoning, or forced stage order is implied.
Rows refer to the same complete hypothesis order; outputs/predictions are integer symbols.
"""

from dataclasses import dataclass
from functools import cache, cached_property
from itertools import combinations


@dataclass(frozen=True)
class FiniteExperimentProblem:
    hypotheses: tuple[str, ...]
    experiments: tuple[tuple[str, tuple[int, ...]], ...]
    predictions: tuple[int, ...]

    def __post_init__(self):
        size = len(self.hypotheses)
        names = [name for name, _ in self.experiments]
        if not 1 <= size <= 4096 or len(set(self.hypotheses)) != size:
            raise ValueError("expected 1–4096 unique hypotheses")
        if len(names) > 12 or len(set(names)) != len(names):
            raise ValueError("expected at most 12 uniquely named experiments")
        if len(self.predictions) != size or any(len(row) != size for _, row in self.experiments):
            raise ValueError("experiment and prediction rows must align with hypotheses")

    def compatible(self, observations: tuple[tuple[str, int], ...] = ()) -> tuple[int, ...]:
        rows = dict(self.experiments)
        if any(name not in rows for name, _ in observations):
            raise ValueError("unknown experiment")
        result = tuple(
            i
            for i in range(len(self.hypotheses))
            if all(rows[name][i] == value for name, value in observations)
        )
        if not result:
            raise ValueError("observations contradict the complete prior")
        return result

    def possible_predictions(
        self, observations: tuple[tuple[str, int], ...] = ()
    ) -> frozenset[int]:
        return frozenset(self.predictions[i] for i in self.compatible(observations))

    def minimum_guaranteed_measurements(
        self, observations: tuple[tuple[str, int], ...] = ()
    ) -> int | None:
        return self._cost(self.belief_mask(observations))

    @cached_property
    def partitions(self) -> tuple[tuple[tuple[int, int], ...], ...]:
        rows = []
        for _, outcomes in self.experiments:
            groups: dict[int, int] = {}
            for i, value in enumerate(outcomes):
                groups[value] = groups.get(value, 0) | (1 << i)
            rows.append(tuple(groups.items()))
        return tuple(rows)

    @cached_property
    def prediction_masks(self) -> tuple[int, ...]:
        groups: dict[int, int] = {}
        for i, value in enumerate(self.predictions):
            groups[value] = groups.get(value, 0) | (1 << i)
        return tuple(groups.values())

    def belief_mask(self, observations: tuple[tuple[str, int], ...] = ()) -> int:
        lookup = {
            name: dict(partitions)
            for (name, _), partitions in zip(self.experiments, self.partitions, strict=True)
        }
        belief = (1 << len(self.hypotheses)) - 1
        for name, value in observations:
            if name not in lookup:
                raise ValueError("unknown experiment")
            belief &= lookup[name].get(value, 0)
        if not belief:
            raise ValueError("observations contradict the complete prior")
        return belief

    @cached_property
    def _cost(self):
        # Cache belongs to this immutable problem, not a process-wide bound-method cache.
        visited = 0

        @cache
        def cost(belief: int) -> int | None:
            nonlocal visited
            visited += 1
            if visited > 100_000:
                raise ValueError("finite experiment qualification exceeded 100000 beliefs")
            if any(belief & mask == belief for mask in self.prediction_masks):
                return 0
            best = None
            for partitions in self.partitions:
                groups = tuple(mask & belief for _, mask in partitions if mask & belief)
                if len(groups) <= 1:
                    continue
                children = [cost(group) for group in groups]
                if all(value is not None for value in children):
                    candidate = 1 + max(children)
                    best = candidate if best is None else min(best, candidate)
            return best

        return cost

    def best_experiment(self, observations: tuple[tuple[str, int], ...] = ()) -> str | None:
        belief = self.belief_mask(observations)
        optimum = self._cost(belief)
        if optimum is None or optimum == 0:
            return None
        for (name, _), partitions in zip(self.experiments, self.partitions, strict=True):
            groups = tuple(mask & belief for _, mask in partitions if mask & belief)
            if len(groups) <= 1:
                continue
            children = [self._cost(group) for group in groups]
            if all(value is not None for value in children) and 1 + max(children) == optimum:
                return name
        raise RuntimeError("no witness for finite experiment optimum")

    def minimum_fixed_measurements(self) -> int | None:
        """Best predetermined measurement set; no adaptive choice or physical costs."""
        full = (1 << len(self.hypotheses)) - 1
        for size in range(len(self.experiments) + 1):
            for selected in combinations(self.partitions, size):
                beliefs = (full,)
                for partitions in selected:
                    beliefs = tuple(
                        belief & mask
                        for belief in beliefs
                        for _, mask in partitions
                        if belief & mask
                    )
                if all(any(b & mask == b for mask in self.prediction_masks) for b in beliefs):
                    return size
        return None
