"""Public belief and bounded witness with overlapping winning repairs."""

import logging
from functools import lru_cache
from time import perf_counter

from nexus.ontology.compositional.laws import QUERIES, REPAIRS, population, rows, winning_masks
from nexus.solver.decision_audit import DecisionAudit


@lru_cache(maxsize=1)
def audit():
    started = perf_counter()
    result = DecisionAudit(len(population()), rows(), winning_masks())
    logging.getLogger("nexus.generation").info(
        "compositional_compile worlds=%s normalized_queries=%s seconds=%.6f",
        len(population()),
        len(rows()),
        perf_counter() - started,
    )
    return result


@lru_cache(maxsize=8192)
def choose(mask):
    data = audit()
    if not mask:
        raise ValueError("observations contradict public prior")
    if data.common(mask):
        return None
    selected = min(
        range(len(data.partitions)),
        key=lambda i: (
            max((mask & p).bit_count() for p in data.partitions[i]),
            sum((mask & p).bit_count() ** 2 for p in data.partitions[i]),
            i,
        ),
    )
    if any(mask & p == mask for p in data.partitions[selected]):
        raise ValueError("mission cannot be resolved by complete query domain")
    return selected


@lru_cache(maxsize=8192)
def reading_bound(mask):
    index = choose(mask)
    if index is None:
        return 0
    return 1 + max(reading_bound(mask & p) for p in audit().partitions[index] if mask & p)


class Belief:
    def __init__(self, spec):
        self.mask = audit().full
        if spec.resolved is not None:
            selected = REPAIRS.index(spec.resolved)
            self.mask = sum(
                1 << i
                for i, (_, wins) in enumerate(population())
                if (wins & -wins).bit_length() - 1 == selected
            )

    def counts(self):
        # Second count is a signature count, NOT the number of exclusive targets.
        return self.mask.bit_count(), len(
            {wins for i, (_, wins) in enumerate(population()) if self.mask >> i & 1}
        )

    def common_decisions(self):
        return audit().common(self.mask)

    def supports(self, doses):
        return doses is not None and REPAIRS.index(tuple(doses)) in self.common_decisions()

    def accepting_count(self, doses):
        return (self.mask & winning_masks()[REPAIRS.index(tuple(doses))]).bit_count()

    def observe(self, measurement):
        sample = measurement.sample
        if sample["reading"] is None:
            return
        mode, x, y, z, a, b, c, d = sample["settings"]
        query = QUERIES.index((mode, (x, y, z), (a, b)))
        normalized = (sample["reading"] - c - mode * d) % 3
        self.mask &= audit().outcome_masks[query].get(normalized, 0)
        if not self.mask:
            raise ValueError("observations contradict public prior")

    def exclude_target(self, doses):
        self.mask &= ~winning_masks()[REPAIRS.index(tuple(doses))]
