"""Exact correlated public posterior; mission resolution permits equivalent programs."""

from functools import lru_cache

from nexus.ontology.transfer.laws import PROGRAM_INDEX, QUERY_INDEX, QUERIES, targets
from nexus.ontology.transfer.tables import N, compile_tables


@lru_cache(maxsize=8192)
def counts(mask, coupled):
    projection = mask & ((1 << N) - 1)
    if coupled:
        projection |= (mask >> N) & ((1 << N) - 1)
        projection |= mask >> (2 * N)
    labels = set()
    while projection:
        bit = projection & -projection
        labels.add(targets()[bit.bit_length() - 1])
        projection ^= bit
    return mask.bit_count(), len(labels)


@lru_cache(maxsize=5184)
def equivalents(label):
    return tuple(i for i, target in enumerate(targets()) if target == label)


class Belief:
    def __init__(self, spec):
        self.coupled = spec.coupled
        self.table = compile_tables(spec.coupled)
        self.mask = self.table.full
        if spec.resolved is not None:
            self.mask = self.table.target_by_world[PROGRAM_INDEX[spec.resolved]]

    def counts(self):
        return counts(self.mask, self.coupled)

    def common_decisions(self):
        if not self.mask or not self.table.common(self.mask):
            return ()
        first = ((self.mask & -self.mask).bit_length() - 1) % N
        label = targets()[first]
        return equivalents(label)

    def accepting_count(self, program):
        if program is None or tuple(program) not in PROGRAM_INDEX:
            return 0
        return (self.mask & self.table.target_by_world[PROGRAM_INDEX[tuple(program)]]).bit_count()

    def supports(self, program):
        return bool(self.mask) and self.accepting_count(program) == self.mask.bit_count()

    def observe(self, measurement):
        sample = measurement.sample
        if sample["reading"] is None:
            return
        if not self.coupled and sample["material"] == "reference":
            if sample["reading"] != 0:
                raise ValueError("calibrated reference must read zero")
            return
        query = QUERY_INDEX[tuple(sample["settings"])]
        if sample["material"] == "reference":
            query += len(QUERIES)
        self.mask &= self.table.outcomes[query][sample["reading"]]
        if not self.mask:
            raise ValueError("observations contradict public prior")

    def exclude_target(self, program):
        if program is not None and tuple(program) in PROGRAM_INDEX:
            self.mask &= ~self.table.target_by_world[PROGRAM_INDEX[tuple(program)]]
