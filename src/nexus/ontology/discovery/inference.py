"""Exact mission-acceptance sets shared by two concrete discovery adapters."""

from dataclasses import dataclass
from functools import cached_property


@dataclass(frozen=True)
class DecisionTables:
    builds: tuple[tuple[int, ...], ...]
    accepting: tuple[int, ...]

    @cached_property
    def build_index(self):
        return {build: i for i, build in enumerate(self.builds)}

    @cached_property
    def mission_signatures(self):
        worlds = max(mask.bit_length() for mask in self.accepting)
        return tuple(
            sum(1 << j for j, mask in enumerate(self.accepting) if mask >> i & 1)
            for i in range(worlds)
        )


class DecisionBelief:
    def __init__(self, spec, mask, table):
        self.spec = spec
        self.mask = mask
        self.table = table

    def counts(self):
        return self.mask.bit_count(), len(
            {s for i, s in enumerate(self.table.mission_signatures) if self.mask >> i & 1}
        )

    def common_decisions(self):
        return tuple(
            b
            for b, win in zip(self.table.builds, self.table.accepting)
            if self.mask and not self.mask & ~win
        )

    def accepting_count(self, attempted):
        index = self.table.build_index.get(attempted)
        return 0 if index is None else (self.mask & self.table.accepting[index]).bit_count()

    def supports(self, attempted):
        return bool(self.mask) and self.accepting_count(attempted) == self.mask.bit_count()

    def exclude_target(self, attempted):
        index = self.table.build_index.get(attempted)
        if index is not None:
            self.restrict(self.mask & ~self.table.accepting[index])

    def restrict(self, mask):
        if not mask:
            raise ValueError("observation contradicts the complete public prior")
        self.mask = mask
