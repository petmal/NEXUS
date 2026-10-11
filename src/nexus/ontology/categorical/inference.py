"""Small exact posterior, intentionally separate from bounded minimax solver."""

from functools import lru_cache

from nexus.ontology.categorical.laws import reading, target, worlds
from nexus.ontology.categorical.schema import SYMBOLS


@lru_cache(maxsize=2)
def predictions(depth):
    return tuple(target(w) for w in worlds(depth))


class CategoricalBelief:
    def __init__(self, depth):
        self.worlds = worlds(depth)
        self.targets = predictions(depth)
        self.indices = set(range(len(self.worlds)))

    def counts(self):
        return len(self.indices), len({self.targets[i] for i in self.indices})

    def observe(self, measurement):
        stage = int(measurement.instrument.removeprefix("instrument"))
        value = SYMBOLS.index(measurement.sample["symbol"])
        output = measurement.sample["reading"]
        output = None if output is None else SYMBOLS.index(output)
        self.indices = {
            i
            for i in self.indices
            if reading(self.worlds[i], stage, value, measurement.tuning) == output
        }

    def exclude_target(self, target):
        self.indices = {i for i in self.indices if self.targets[i] != target}
