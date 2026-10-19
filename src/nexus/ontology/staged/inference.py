"""Public-only joint posterior; failed finish excludes the committed full repair."""

from nexus.ontology.staged.laws import prior_mask, tables


class Belief:
    def __init__(self, spec):
        self.mask = prior_mask(spec)
        self.table = tables(spec.linked)

    def counts(self):
        # Injectivity is checked independently before family qualification.
        count = self.mask.bit_count()
        return count, count

    def observe(self, measurement):
        sample = measurement.sample
        q = sample["stage"] * 9 + sample["carrier"] * 3 + sample["tag"]
        self.mask &= self.table.partitions[q][sample["reading"]]
        if not self.mask:
            raise ValueError("staged observation contradicts the public prior")

    def common_decisions(self):
        return (
            (self.table.decisions[self.mask.bit_length() - 1],)
            if self.mask.bit_count() == 1
            else ()
        )

    def accepting_count(self, attempted):
        return (
            0
            if attempted is None
            else (self.mask & self.table.accepting.get(attempted, 0)).bit_count()
        )

    def supports(self, attempted):
        return bool(self.mask) and self.accepting_count(attempted) == self.mask.bit_count()

    def exclude_target(self, attempted):
        self.mask &= ~self.table.accepting.get(attempted, 0)
        if not self.mask:
            raise ValueError("failed finish contradicts all publicly possible mechanisms")
