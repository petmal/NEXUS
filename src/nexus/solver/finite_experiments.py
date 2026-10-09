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
        mask = self.belief_mask(observations)
        indices = []
        while mask:
            bit = mask & -mask
            indices.append(bit.bit_length() - 1)
            mask ^= bit
        return tuple(indices)

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
    def target_mask_by_world(self) -> tuple[int, ...]:
        masks = [0] * len(self.hypotheses)
        for mask in self.prediction_masks:
            remaining = mask
            while remaining:
                bit = remaining & -remaining
                masks[bit.bit_length() - 1] = mask
                remaining ^= bit
        return tuple(masks)

    def _resolved(self, belief: int) -> bool:
        target = self.target_mask_by_world[(belief & -belief).bit_length() - 1]
        return belief & target == belief

    @cached_property
    def _cost(self):
        # Bounds prune search only; every returned cost still has an exact witness.
        visited = 0
        fanout = max(map(len, self.partitions), default=1)

        @cache
        def cost(belief: int) -> int | None:
            nonlocal visited
            visited += 1
            if visited > 100_000:
                raise ValueError("finite experiment qualification exceeded 100000 beliefs")
            if self._resolved(belief):
                return 0
            if fanout < 2:
                return None
            targets = set()
            remaining = belief
            while remaining:
                bit = remaining & -remaining
                targets.add(self.predictions[bit.bit_length() - 1])
                remaining ^= bit
            lower, capacity = 0, 1
            while capacity < len(targets):
                lower += 1
                capacity *= fanout
            best = None
            seen = set()
            for partitions in self.partitions:
                groups = tuple(sorted(mask & belief for _, mask in partitions if mask & belief))
                if len(groups) <= 1 or groups in seen:
                    continue
                seen.add(groups)
                worst = 0
                for child in sorted(groups, key=int.bit_count, reverse=True):
                    value = cost(child)
                    if value is None:
                        worst = None
                        break
                    worst = max(worst, value)
                    if best is not None and 1 + worst >= best:
                        break
                if worst is not None:
                    best = 1 + worst if best is None else min(best, 1 + worst)
                if best == lower:
                    return best
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
        """Exact fixed-set cost, learning necessary separators from counterexamples."""
        full = (1 << len(self.hypotheses)) - 1
        constraints: list[int] = []
        rows = tuple(row for _, row in self.experiments)
        for size in range(len(rows) + 1):
            for selected in combinations(range(len(rows)), size):
                chosen = sum(1 << i for i in selected)
                if any(not chosen & required for required in constraints):
                    continue
                beliefs = (full,)
                for i in selected:
                    beliefs = tuple(
                        belief & mask
                        for belief in beliefs
                        for _, mask in self.partitions[i]
                        if belief & mask
                    )
                for belief in beliefs:
                    left = (belief & -belief).bit_length() - 1
                    different = belief & ~self.target_mask_by_world[left]
                    if different:
                        right = (different & -different).bit_length() - 1
                        separator = sum(
                            1 << i for i, row in enumerate(rows) if row[left] != row[right]
                        )
                        if not separator:
                            return None
                        # Every valid fixed set must separate this target-distinct pair.
                        constraints.append(separator)
                        break
                else:
                    return size
        return None

    @cached_property
    def policy_leaf_masks(self) -> tuple[int, ...]:
        """Disjoint terminal beliefs for the same tie-broken optimal measurement policy.

        Worlds within a leaf produce the same transcript and target, so a physical
        planner depending only on that transcript needs one witness per leaf.
        """

        def leaves(belief):
            optimum = self._cost(belief)
            if optimum == 0:
                return (belief,)
            if optimum is None:
                raise ValueError("unidentifiable experiment problem has no complete policy")
            for partitions in self.partitions:
                groups = tuple(mask & belief for _, mask in partitions if mask & belief)
                if len(groups) <= 1:
                    continue
                costs = [self._cost(group) for group in groups]
                if all(value is not None for value in costs) and 1 + max(costs) == optimum:
                    return tuple(leaf for group in groups for leaf in leaves(group))
            raise RuntimeError("no witness for policy leaf")

        return leaves((1 << len(self.hypotheses)) - 1)
