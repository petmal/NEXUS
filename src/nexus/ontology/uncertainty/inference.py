"""Exact factored posterior for 120 mechanisms and all 8! balanced assignments.

After k distinct fixture IDs, each surviving mechanism has exactly (8-k)!
compatible assignments. Full joint readings are injective within each mechanism.
No partial-channel queries are admitted; they would require a matching posterior.
"""

from math import factorial

from nexus.ontology.discovery.inference import DecisionBelief
from nexus.ontology.uncertainty.laws import MODELS, loading, prior_mask, tables


class Belief(DecisionBelief):
    def __init__(self, spec):
        super().__init__(spec, prior_mask(spec), tables()[0])
        self.fixtures = {}

    @property
    def compatible_schedules(self):
        return self.mask.bit_count() * factorial(8 - len(self.fixtures))

    def observe(self, measurement):
        mode, fixture = measurement.sample["query"]
        values = tuple(measurement.sample["values"])
        if mode == 0:
            if fixture in self.fixtures and self.fixtures[fixture] != values:
                raise ValueError("persistent fixture produced inconsistent readings")
            if fixture not in self.fixtures and values in self.fixtures.values():
                raise ValueError("distinct fixtures cannot duplicate a balanced support point")
            possible = sum(1 << i for i, outcomes in enumerate(tables()[1]) if values in outcomes)
            self.restrict(self.mask & possible)
            self.fixtures[fixture] = values
        else:
            possible = 0
            for i, model in enumerate(MODELS):
                mean = tuple(loading(model.pattern, j) for j in range(5))
                expected = (
                    mean if mode == 1 else (*mean, *(1 for _ in range(5)), *(0 for _ in range(10)))
                )
                if expected == values:
                    possible |= 1 << i
            self.restrict(self.mask & possible)

    def choose_query(self):
        if self.common_decisions():
            return None
        return (0, next(i for i in range(8) if i not in self.fixtures))
