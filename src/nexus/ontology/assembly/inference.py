"""Public-only joint law/reader posterior; accepted builds may overlap in spelling."""

from nexus.ontology.assembly.laws import (
    BUILD_INDEX,
    BUILDS,
    QUERY_INDEX,
    normalize_query,
    prior_mask,
    tables,
)


class Belief:
    def __init__(self, spec):
        self.spec = spec
        self.mask = prior_mask(spec)
        self.table = tables(spec.coupled_reader)

    def counts(self):
        indices = (i for i in range(len(self.table.rows)) if self.mask >> i & 1)
        return self.mask.bit_count(), len({self.table.signatures[i] for i in indices})

    def observe(self, measurement):
        r = measurement.sample
        q = QUERY_INDEX[normalize_query(r["channel"], r["x"], r["y"])]
        updated = self.mask & self.table.partitions[q][r["value"]]
        if not updated:
            raise ValueError("assembly reading contradicts the public prior")
        self.mask = updated

    def common_decisions(self):
        return tuple(
            d for d, win in zip(BUILDS, self.table.accepting) if self.mask and not self.mask & ~win
        )

    def accepting_count(self, attempted):
        index = BUILD_INDEX.get(attempted)
        return 0 if index is None else (self.mask & self.table.accepting[index]).bit_count()

    def supports(self, attempted):
        return bool(self.mask) and self.accepting_count(attempted) == self.mask.bit_count()

    def exclude_target(self, attempted):
        index = BUILD_INDEX.get(attempted)
        if index is not None:
            updated = self.mask & ~self.table.accepting[index]
            if not updated:
                raise ValueError("failed finish contradicts all remaining assembly worlds")
            self.mask = updated

    def choose_query(self):
        if self.common_decisions():
            return None
        sizes = [
            tuple((self.mask & p).bit_count() for p in parts) for parts in self.table.partitions
        ]
        chosen = min(
            range(len(sizes)), key=lambda q: (max(sizes[q]), sum(n * n for n in sizes[q]), q)
        )
        if max(sizes[chosen]) == self.mask.bit_count():
            raise ValueError("complete assembly observation domain leaves no common build")
        return chosen
