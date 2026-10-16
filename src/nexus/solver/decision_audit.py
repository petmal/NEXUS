"""Finite information audits for overlapping acceptable decisions.

Queries partition worlds; decisions need not. A resolved belief has a decision
accepted by *every* remaining world. Distinct repair sets are not target classes.
Costs are relaxed to zero here, so reported query/guess success ceilings must not
be presented as live-action or cognitive-depth certificates.
"""

from functools import cache
from time import monotonic


class DecisionAudit:
    def __init__(self, worlds: int, rows: tuple[bytes, ...], winning: tuple[int, ...]):
        if not 1 <= worlds <= 16384 or len(rows) * worlds > 16_000_000:
            raise ValueError("decision audit size limit")
        self.full = (1 << worlds) - 1
        if not 1 <= len(winning) <= 256 or any(
            type(w) is not int or w < 0 or w & ~self.full for w in winning
        ):
            raise ValueError("invalid decision acceptance masks")
        covered = 0
        for mask in winning:
            covered |= mask
        if covered != self.full:
            raise ValueError("every admitted world must have an accepted decision")
        if not 1 <= len(rows) <= 50000 or any(len(row) != worlds for row in rows):
            raise ValueError("invalid observation table")
        self.worlds, self.rows, self.winning = worlds, rows, winning
        self.partitions = tuple(
            tuple(
                sum(1 << i for i, v in enumerate(row) if v == outcome)
                for outcome in sorted(set(row))
            )
            for row in rows
        )

    def common(self, mask):
        return tuple(i for i, win in enumerate(self.winning) if mask and mask & ~win == 0)

    def best_mass(self, mask):
        return max((mask & win).bit_count() for win in self.winning)

    def closure(self, world: int, query_indices):
        mask = self.full
        for index in query_indices:
            outcome = self.rows[index][world]
            mask &= sum(1 << i for i, value in enumerate(self.rows[index]) if value == outcome)
        return mask

    def positive_reading_lower(self, world: int) -> int:
        """Exact 0/1/2 certificate search; 3 means only 'at least three'.

        The query chooser is granted the actual world. For every repair accepted
        there, test whether zero, one, or two actual outcomes exclude ALL rivals
        rejecting that repair. This includes every query and overlapping winning
        region. It excludes guesses/rejected finishes and is not cognitive depth.
        """
        if type(world) is not int or not 0 <= world < self.worlds:
            raise ValueError("world index outside prior")
        if self.common(self.full):
            return 0
        outcomes = [next(mask for mask in row if mask >> world & 1) for row in self.partitions]
        best = 3
        for winning in self.winning:
            if not winning >> world & 1:
                continue
            rivals = self.full & ~winning
            remaining = {mask & rivals for mask in outcomes}
            if 0 in remaining:
                return 1
            if best == 3 and any(not left & right for left in remaining for right in remaining):
                best = 2
        return best

    def success_mass(self, readings: int, guesses: int = 1, *, max_seconds=120):
        """Exact adaptive query/guess interleavings, for bounded small horizons."""
        if readings < 0 or guesses < 1 or readings > 2 or guesses > 2 or readings + guesses > 3:
            raise ValueError("supported audit horizon: <=2 queries, <=2 guesses, sum<=3")
        deadline = monotonic() + max_seconds
        pair_masks = tuple({a | b for a in self.winning for b in self.winning})

        @cache
        def value(mask, r, g):
            if monotonic() > deadline:
                raise TimeoutError("decision audit time limit; no certificate")
            if not mask or not g:
                return 0
            if self.common(mask):
                return mask.bit_count()
            if not r:
                candidates = self.winning if g == 1 else pair_masks
                return max((mask & w).bit_count() for w in candidates)
            best = max(
                sum(value(mask & p, r - 1, g) for p in row if mask & p) for row in self.partitions
            )
            if g > 1:
                best = max(
                    best,
                    max((mask & w).bit_count() + value(mask & ~w, r, g - 1) for w in self.winning),
                )
            return best

        return value(self.full, readings, guesses)
