"""Public archive-conditioned inference over exact observable behavior classes."""

from functools import lru_cache

from nexus.ontology.discovery.inference import DecisionBelief, DecisionTables
from nexus.ontology.revision.laws import (
    QUERIES,
    QUERY_INDEX,
    class_id,
    compiled,
    prior_mask,
    validate_build,
)


@lru_cache(maxsize=1)
def decision_table():
    prior = compiled()
    return DecisionTables(prior.representatives, tuple(1 << i for i in range(len(prior.rows))))


@lru_cache(maxsize=4096)
def choose(mask):
    if not mask:
        raise ValueError("cannot choose an experiment for an empty prior")
    if mask.bit_count() == 1:
        return None
    partitions = compiled().partitions
    query = min(
        range(len(QUERIES)),
        key=lambda q: (
            max((mask & part).bit_count() for part in partitions[q]),
            sum((mask & part).bit_count() ** 2 for part in partitions[q]),
            len(QUERIES[q]),
            QUERIES[q],
        ),
    )
    if max((mask & part).bit_count() for part in partitions[query]) == mask.bit_count():
        raise ValueError("no legal experiment resolves the remaining mission behaviors")
    return QUERIES[query]


class Belief(DecisionBelief):
    def __init__(self, spec):
        super().__init__(spec, prior_mask(spec), decision_table())

    def counts(self):
        # Worlds here are behavioral classes, not multiplicities of hidden wiring.
        return self.mask.bit_count(), self.mask.bit_count()

    def common_decisions(self):
        return (
            (self.table.builds[self.mask.bit_length() - 1],) if self.mask.bit_count() == 1 else ()
        )

    def accepting_count(self, attempted):
        return int(bool(self.mask & (1 << class_id(attempted)))) if validate_build(attempted) else 0

    def exclude_target(self, attempted):
        if validate_build(attempted):
            self.restrict(self.mask & ~(1 << class_id(attempted)))

    def observe(self, measurement):
        query = QUERY_INDEX[tuple(measurement.sample["query"])]
        values = tuple(measurement.sample["values"])
        if len(values) != 1 or type(values[0]) is not int or values[0] not in (0, 1, 2):
            raise ValueError("invalid revision-family reading")
        self.restrict(self.mask & compiled().partitions[query][values[0]])

    def choose_query(self):
        return choose(self.mask)
