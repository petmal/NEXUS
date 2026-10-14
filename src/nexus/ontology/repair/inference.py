"""Immutable cached public-prior tables; each session owns only its belief mask."""

from functools import lru_cache
from types import MappingProxyType

from nexus.ontology.repair.laws import response, solution, worlds


@lru_cache(maxsize=1)
def tables():
    targets = {}
    readings = {}
    for i, w in enumerate(worlds()):
        bit = 1 << i
        target = solution(w.a, w.b, w.c, w.degree)
        targets[target] = targets.get(target, 0) | bit
        queries = [("reference", None, (w.a,))]
        queries += [
            ("reader", (plane, x), response(w, (plane, x))) for plane in (0, 1) for x in range(7)
        ]
        for key in queries:
            readings[key] = readings.get(key, 0) | bit
    return MappingProxyType(targets), MappingProxyType(readings)


class RepairBelief:
    def __init__(self):
        self.mask = (1 << len(worlds())) - 1

    def counts(self):
        return self.mask.bit_count(), sum(bool(mask & self.mask) for mask in tables()[0].values())

    def observe(self, measurement):
        s = measurement.sample
        if s["reading"] is None:
            return  # Physically insensitive pairings have truth-independent null output.
        context = tuple(s["context"]) if measurement.instrument == "reader" else None
        key = measurement.instrument, context, tuple(s["reading"])
        self.mask &= tables()[1].get(key, 0)
        if not self.mask:
            raise ValueError("public response is inconsistent with the declared repair grammar")

    def exclude_target(self, target):
        if target is not None:
            self.mask &= ~tables()[0].get(tuple(target), 0)
