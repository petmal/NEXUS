"""Public-only memory-program posterior; preserve multiplicities of equivalent programs."""

from functools import lru_cache

from nexus.ontology.discovery.inference import DecisionBelief
from nexus.ontology.representation.laws import QUERIES, QUERY_INDEX, prior_mask, tables


@lru_cache(maxsize=2048)
def choose(mask):
    table, _rows, partitions = tables()
    if any(not mask & ~win for win in table.accepting):
        return None
    q = min(
        range(len(QUERIES)),
        key=lambda i: (
            max((mask & p).bit_count() for p in partitions[i]),
            sum((mask & p).bit_count() ** 2 for p in partitions[i]),
            len(QUERIES[i]),
            QUERIES[i],
        ),
    )
    if max((mask & p).bit_count() for p in partitions[q]) == mask.bit_count():
        raise ValueError("reader grammar leaves unresolved mission behavior")
    return QUERIES[q]


class Belief(DecisionBelief):
    def __init__(self, spec):
        super().__init__(spec, prior_mask(spec), tables()[0])

    def observe(self, measurement):
        q = QUERY_INDEX[tuple(measurement.sample["query"])]
        values = tuple(measurement.sample["values"])
        if len(values) != 1 or values[0] not in (0, 1, 2):
            raise ValueError("invalid memory reading")
        self.restrict(self.mask & tables()[2][q][values[0]])

    def choose_query(self):
        return choose(self.mask)
