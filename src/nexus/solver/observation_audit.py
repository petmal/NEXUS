"""Exact evidence certificates in a finite observation model.

This deliberately grants free arbitrary experiment preparation. A negative result
therefore covers every adaptive choice of that many measurement outcomes, even an
oracle's choices. It does NOT cover guess success, finish feedback, physical cost,
feedback-round complexity, or cognitive/model difficulty.
"""

from dataclasses import dataclass
from functools import cached_property
from math import isfinite
from time import monotonic


class AuditLimitError(RuntimeError):
    """An incomplete search cannot certify absence of a shortcut."""


@dataclass(frozen=True)
class CertificateAudit:
    lower_bound: int
    exact_minimum: int | None
    witness_rows: tuple[int, ...]
    pair_checks: int


@dataclass(frozen=True)
class ObservationAudit:
    predictions: tuple[int, ...]
    rows: tuple[bytes, ...]

    def __post_init__(self):
        n = len(self.predictions)
        if not 1 <= n <= 16384 or any(type(p) is not int for p in self.predictions):
            raise ValueError("expected 1..16384 integer target labels")
        if not self.rows or len(self.rows) > 50000:
            raise ValueError("expected 1..50000 experiment rows")
        if n * len(self.rows) > 16_000_000:
            raise ValueError("observation audit exceeds the 16 MB outcome limit")
        if any(type(row) is not bytes or len(row) != n for row in self.rows):
            raise ValueError("byte outcome rows must align exactly with target labels")

    @cached_property
    def target_masks(self) -> tuple[int, ...]:
        masks: dict[int, int] = {}
        for i, label in enumerate(self.predictions):
            masks[label] = masks.get(label, 0) | (1 << i)
        return tuple(masks.values())

    @cached_property
    def targets_by_world(self) -> tuple[int, ...]:
        lookup = {
            label: mask for label, mask in zip(dict.fromkeys(self.predictions), self.target_masks)
        }
        return tuple(lookup[label] for label in self.predictions)

    @cached_property
    def partitions(self) -> tuple[tuple[int, ...], ...]:
        result = []
        for row in self.rows:
            masks: dict[int, int] = {}
            for i, value in enumerate(row):
                masks[value] = masks.get(value, 0) | (1 << i)
            result.append(tuple(masks.values()))
        return tuple(result)

    def target_count(self, mask: int) -> int:
        return sum(bool(mask & target) for target in self.target_masks)

    def all_data_groups(self, selected: tuple[int, ...]) -> tuple[int, ...]:
        """Posterior after receiving every outcome in a specified experiment class."""
        if any(type(i) is not int or not 0 <= i < len(self.rows) for i in selected):
            raise ValueError("invalid experiment index")
        groups: dict[bytes, int] = {}
        rows = tuple(self.rows[i] for i in selected)
        for i in range(len(self.predictions)):
            signature = bytes(row[i] for row in rows)
            groups[signature] = groups.get(signature, 0) | (1 << i)
        return tuple(groups.values())

    def best_guess_mass(self, groups: tuple[int, ...]) -> int:
        """Uniform full-prior correct mass; target equivalents are counted together."""
        return sum(max((group & t).bit_count() for t in self.target_masks) for group in groups)

    def population_summary(self) -> dict:
        count = len(self.target_masks)
        fanout = max(map(len, self.partitions))
        lower, capacity = 0, 1
        if fanout < 2 and count > 1:
            lower = None
        else:
            while capacity < count:
                lower += 1
                capacity *= fanout
        return {
            "worlds": len(self.predictions),
            "target_classes": count,
            "experiments": len(self.rows),
            "distinct_partitions": len({tuple(sorted(p)) for p in self.partitions}),
            "measurement_fanout": fanout,
            "worst_case_reading_lower_bound": lower,
            "one_reading_best_correct_mass": max(self.best_guess_mass(p) for p in self.partitions),
            "probability_scope": "uniform disclosed prior; not a stratified matrix success rate",
        }

    def guess_success_upper(self, *, maximum_guesses: int, maximum_readings: int) -> dict:
        """Relaxed uniform-prior bound including adaptive failed submissions.

        A guess has one absorbing success and one continuing failure branch.
        A reading has at most `fanout` children. Induction therefore bounds
        successful target leaves by guesses * fanout**readings, regardless of
        their ordering. Giving those leaves the largest target classes relaxes
        every restriction imposed by actual experiments and preparation costs.
        The caller must prove the guess budget and response-channel assumptions.
        """
        if any(type(n) is not int or n < 0 for n in (maximum_guesses, maximum_readings)):
            raise ValueError("guess and reading limits must be nonnegative integers")
        if maximum_readings > 100:
            raise ValueError("reading limit exceeds audit bound")
        fanout = max(map(len, self.partitions))
        capacity = min(len(self.target_masks), maximum_guesses * fanout**maximum_readings)
        mass = sum(sorted((m.bit_count() for m in self.target_masks), reverse=True)[:capacity])
        return {
            "maximum_guesses": maximum_guesses,
            "maximum_readings": maximum_readings,
            "successful_target_capacity": capacity,
            "correct_mass_upper": mass,
            "worlds": len(self.predictions),
            "probability_upper": mass / len(self.predictions),
        }

    def certificate(
        self, world: int, *, max_readings: int = 3, max_seconds: float = 30
    ) -> CertificateAudit:
        """Exact minimum through three readings, otherwise a proved lower bound.

        Keep only undominated actual-outcome rival sets. A superset cannot improve
        any intersection. The third-query test uses the transpose of retained
        rival masks to find a query excluding every remaining rival at once.
        """
        if type(world) is not int or not 0 <= world < len(self.predictions):
            raise ValueError("world index outside the admitted prior")
        if (
            type(max_readings) is not int
            or max_readings not in (1, 2, 3)
            or not isfinite(max_seconds)
            or max_seconds <= 0
        ):
            raise ValueError("use 1..3 readings and a positive time cap")
        deadline = monotonic() + max_seconds
        rival = ((1 << len(self.predictions)) - 1) ^ self.targets_by_world[world]
        if not rival:
            return CertificateAudit(0, 0, (), 0)
        unique = {}
        # Build only the realized outcome masks, checking the deadline between
        # rows. Do not hide an uninterruptible lazy full-partition compilation
        # inside the timed search.
        for j, row in enumerate(self.rows):
            if monotonic() > deadline:
                raise AuditLimitError("certificate preprocessing exceeded time cap")
            outcome = row[world]
            mask = 0
            for i, value in enumerate(row):
                if value == outcome:
                    mask |= 1 << i
            mask &= rival
            unique.setdefault(mask, j)
        if 0 in unique:
            return CertificateAudit(1, 1, (unique[0],), 0)
        if max_readings == 1:
            return CertificateAudit(2, None, (), 0)
        candidates = []
        for mask in sorted(unique, key=int.bit_count):
            if monotonic() > deadline:
                raise AuditLimitError("certificate dominance search exceeded time cap")
            if not any(old & mask == old for old in candidates):
                candidates.append(mask)
        checks = 0
        for j, left in enumerate(candidates):
            for k in range(j):
                if k % 256 == 0 and monotonic() > deadline:
                    raise AuditLimitError("certificate search exceeded time cap")
                checks += 1
                intersection = left & candidates[k]
                if not intersection:
                    return CertificateAudit(2, 2, (unique[left], unique[candidates[k]]), checks)
            if monotonic() > deadline:
                raise AuditLimitError("two-reading certificate search exceeded time cap")
        if max_readings == 2:
            return CertificateAudit(3, None, (), checks)
        retained_by_world = [0] * len(self.predictions)
        for j, mask in enumerate(candidates):
            while mask:
                bit = mask & -mask
                retained_by_world[bit.bit_length() - 1] |= 1 << j
                mask ^= bit
        all_queries = (1 << len(candidates)) - 1
        # Recompute intersections: materializing all pairs needlessly grows memory
        # quadratically, while two integer ANDs are cheap.
        for j, left in enumerate(candidates):
            for k in range(j):
                if k % 256 == 0 and monotonic() > deadline:
                    raise AuditLimitError("three-reading certificate search exceeded time cap")
                mask, bad = left & candidates[k], 0
                while mask and bad != all_queries:
                    bit = mask & -mask
                    bad |= retained_by_world[bit.bit_length() - 1]
                    mask ^= bit
                available = all_queries ^ bad
                if available:
                    third = (available & -available).bit_length() - 1
                    return CertificateAudit(
                        3, 3, tuple(unique[candidates[q]] for q in (j, k, third)), checks
                    )
            if monotonic() > deadline:
                raise AuditLimitError("three-reading certificate search exceeded time cap")
        return CertificateAudit(4, None, (), checks)


def labels(values: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    """Stable equivalence labels, without requiring identification of latent laws."""
    assigned = {}
    return tuple(assigned.setdefault(value, len(assigned)) for value in values)
