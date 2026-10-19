"""Offline finite information checks; a common winning decision is the goal.

Pairwise-compatible worlds need not have a jointly valid decision. Panel checks
therefore intersect complete winning sets, not parameter modes or target counts.
The fixed-panel optimizer below is deliberately narrower: full identification.
It can qualify a mission only after injective mission signatures are proved.
"""

from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations


@dataclass(frozen=True)
class PanelAssessment:
    worlds: int
    observation_buckets: int
    supported_worlds: int
    unresolved_buckets: int


def assess_panel(
    winning: tuple[int, ...], rows: tuple[tuple[int, ...], ...], panel
) -> PanelAssessment:
    if not winning or len(winning) != len(rows) or any(bits <= 0 for bits in winning):
        raise ValueError("panel requires a nonempty, winnable finite prior")
    groups = defaultdict(list)
    for index, row in enumerate(rows):
        groups[tuple(row[q] for q in panel)].append(index)
    supported = unresolved = 0
    for indices in groups.values():
        common = winning[indices[0]]
        for index in indices[1:]:
            common &= winning[index]
        if common:
            supported += len(indices)
        else:
            unresolved += 1
    return PanelAssessment(len(rows), len(groups), supported, unresolved)


def feedback_success_ceiling(worlds: int, outcomes: int, accepting: int, feedback: int) -> int:
    """Uniform-prior mass upper bound with free setup and arbitrary submissions.

    At each action a measurement has <=outcomes branches, or a finish accepts at most
    accepting worlds and has one rejection branch. Allowing free reconfiguration and
    ignoring costs only strengthens the player. Includes all failed/successful finishes.
    This is not a total-action optimum, cognition bound, or selected-seed probability.
    """
    if worlds < 1 or outcomes < 1 or accepting < 0 or feedback < 0:
        raise ValueError("invalid finite feedback problem")
    covered = 0
    for _ in range(feedback):
        covered = min(worlds, max(outcomes * covered, accepting + covered))
    return covered


def minimum_supporting_certificate(
    prior: int, outcomes: tuple[int, ...], winning: tuple[int, ...], *, max_states=100000
) -> tuple[int, ...]:
    """Exact actual-outcome certificate, with oracle choice of experiments.

    Each outcome mask contains the actual world's observation. Winning masks are
    decisions accepted in that world. Stop when one complete decision covers the
    remaining belief; parameter uniqueness and pairwise agreement are unnecessary.
    This is an evidence lower bound along that world, excluding finish feedback and
    preparation costs. It is not an implementable policy or adaptive-round guarantee.
    """
    if prior <= 0 or not winning or len(outcomes) > 27 or len(winning) > 256:
        raise ValueError("supporting certificate exceeds finite bounds")
    intersection = prior
    for mask in outcomes:
        if mask <= 0 or mask & ~prior:
            raise ValueError("invalid actual-outcome mask")
        intersection &= mask
    if not intersection or any(w <= 0 or w & ~prior for w in winning):
        raise ValueError("inconsistent actual observations or winning sets")
    # Dominated readings cannot improve an information-only certificate.
    candidates = tuple(
        i
        for i, m in enumerate(outcomes)
        if m != prior and not any(n != m and n & m == n for n in outcomes) and m not in outcomes[:i]
    )
    visited = 0

    @cache
    def solve(mask):
        nonlocal visited
        visited += 1
        if visited > max_states:
            raise ValueError("supporting certificate search cap reached; no certificate")
        if any(mask & ~w == 0 for w in winning):
            return ()
        choices = [(i, mask & outcomes[i]) for i in candidates if mask & outcomes[i] != mask]
        if not choices:
            raise ValueError("all available observations leave no guaranteed decision")
        return min(
            (tuple(sorted((i, *solve(child)))) for i, child in choices), key=lambda p: (len(p), p)
        )

    return solve(prior)


@dataclass(frozen=True)
class FixedPanel:
    queries: tuple[int, ...]
    forced_queries: tuple[int, ...]
    residual_constraints: tuple[int, ...]
    subsets_checked: int


def minimum_identifying_panel(rows: tuple[tuple[int, ...], ...]) -> FixedPanel:
    """Exact bounded hitting-set search over every indistinguishable world pair.

    Singleton requirements are forced first. Remaining subsets are checked by size;
    no stochastic search or seed-conditioned pruning. Intended for <=256 worlds and
    <=27 queries. Offline only, never in the per-episode generation path.
    """
    if not rows or len(rows) > 256 or len(rows[0]) > 27:
        raise ValueError("fixed-panel proof exceeds its explicit finite bounds")
    if any(len(r) != len(rows[0]) for r in rows) or len(set(rows)) != len(rows):
        raise ValueError("full legal query domain does not identify every world")
    requirements = {
        sum(1 << q for q, (a, b) in enumerate(zip(left, right)) if a != b)
        for left, right in combinations(rows, 2)
    }
    forced = 0
    for requirement in requirements:
        if requirement.bit_count() == 1:
            forced |= requirement
    residual = tuple(sorted(r for r in requirements if not r & forced))
    available = tuple(q for q in range(len(rows[0])) if any(r & (1 << q) for r in residual))
    checked = 0
    for size in range(len(available) + 1):
        for chosen in combinations(available, size):
            mask = sum(1 << q for q in chosen)
            checked += 1
            if all(mask & r for r in residual):
                return FixedPanel(
                    tuple(q for q in range(len(rows[0])) if (forced | mask) & (1 << q)),
                    tuple(q for q in range(len(rows[0])) if forced & (1 << q)),
                    residual,
                    checked,
                )
    raise ValueError("fixed-panel search failed despite identifying full domain")
