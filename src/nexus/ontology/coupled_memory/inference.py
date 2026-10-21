"""Exact joint posterior over physical dynamics and the observation encoder."""

from functools import lru_cache

from nexus.ontology.discovery.inference import DecisionBelief
from nexus.ontology.coupled_memory.laws import QUERIES, QUERY_INDEX, prior_mask, tables


@lru_cache(maxsize=2048)
def choose(mask):
    table, _rows, parts = tables()
    if any(not mask & ~win for win in table.accepting):
        return None
    q = min(
        range(len(QUERIES)),
        key=lambda i: (
            max((mask & part).bit_count() for part in parts[i]),
            sum((mask & part).bit_count() ** 2 for part in parts[i]),
            len(QUERIES[i]),
            QUERIES[i],
        ),
    )
    if max((mask & part).bit_count() for part in parts[q]) == mask.bit_count():
        raise ValueError("legal experiments cannot resolve mission behavior")
    return QUERIES[q]


class Belief(DecisionBelief):
    def __init__(self, spec):
        super().__init__(spec, prior_mask(spec), tables()[0])

    def observe(self, measurement):
        q = QUERY_INDEX[tuple(measurement.sample["query"])]
        values = tuple(measurement.sample["values"])
        if len(values) != 1 or type(values[0]) is not int or values[0] not in (0, 1, 2):
            raise ValueError("invalid coupled-memory reading")
        self.restrict(self.mask & tables()[2][q][values[0]])

    def choose_query(self):
        return choose(self.mask)
