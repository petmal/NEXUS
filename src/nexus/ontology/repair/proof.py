"""Recomputable upper proof for the degree-revealed immutable-query relaxation.

Every query subset and response branch is covered. The live-to-query simulation
is a separate obligation documented in docs/repair-construction-proof.md. This
module does not turn arbitrary live games into static experiments.
"""

from dataclasses import asdict, dataclass
from functools import lru_cache
from itertools import combinations, product

from nexus.solver.finite_game import SearchBudget

Q = 7
VERSION = "repair-query-upper-v1"


@dataclass(frozen=True)
class QueryUpperProof:
    version: str
    field: int
    worlds: int
    prior: str
    budget: int
    query_costs: tuple[int, ...]
    attempt_cost: int
    feedback_rounds: int
    # Complete first-batch subset -> optimized remaining success mass.
    choices: tuple[tuple[tuple[int, ...], int], ...]
    upper_mass: int


def model():
    # Adjacent groups of seven worlds share a repair target; r is nuisance.
    worlds = tuple((*abc, r) for abc in product(range(Q), repeat=3) for r in range(Q))
    rows = [tuple(a for a, b, c, r in worlds)]
    rows += [tuple((b + r * (a - x)) % Q for a, b, c, r in worlds) for x in range(Q)]
    rows += [tuple((c + r * (b - y)) % Q for a, b, c, r in worlds) for y in range(Q)]
    partitions = []
    for row in rows:
        bins = [0] * Q
        for i, value in enumerate(row):
            bins[value] |= 1 << i
        partitions.append(tuple(v for v in bins if v))
    return tuple(partitions)


def batches(costs, budget, attempt):
    # Duplicate immutable readings are dominated; query order cannot change replies.
    for n in range(len(costs) + 1):
        if sum(sorted(costs)[:n]) + attempt > budget:
            break
        for selected in combinations(range(len(costs)), n):
            cost = sum(costs[i] for i in selected)
            if cost + attempt <= budget:
                yield cost, selected


def prove(*, budget=15, limits=None) -> QueryUpperProof:
    limits = limits or SearchBudget(max_states=2_000_000, max_seconds=60)
    limits.start()
    partitions = model()
    costs = (1,) + (4,) * 14
    available = tuple(batches(costs, budget, 3))

    @lru_cache(maxsize=1024)
    def refine(mask, selected):
        cells = (mask,)
        for query in selected:
            cells = tuple(v for cell in cells for group in partitions[query] if (v := cell & group))
        return cells

    @lru_cache(maxsize=8192)
    def guesses(mask, count):
        values = []
        while mask:
            first = (mask & -mask).bit_length() - 1
            target = ((1 << Q) - 1) << ((first // Q) * Q)
            values.append((mask & target).bit_count())
            mask &= ~target
        return sum(sorted(values, reverse=True)[:count])

    @lru_cache(maxsize=8192)
    def last(mask, left):
        limits.tick()
        best = 0
        for cost, selected in available:
            limits.poll()
            if cost + 3 <= left:
                best = max(
                    best, sum(guesses(cell, (left - cost) // 3) for cell in refine(mask, selected))
                )
        return best

    full = (1 << (Q**4)) - 1
    choices = []
    for cost, selected in available:
        limits.poll()
        choices.append(
            (selected, sum(last(cell, budget - cost) for cell in refine(full, selected)))
        )
    limits.poll()
    return QueryUpperProof(
        VERSION,
        Q,
        Q**4,
        "uniform-a-b-c-r-degree-granted",
        budget,
        costs,
        3,
        2,
        tuple(choices),
        max(v for _, v in choices),
    )


def check(proof: QueryUpperProof, *, limits=None):
    """Independent literal-partition enumeration; never trust a coverage flag.

    Reconstructs actual world rows, enumerates each first/second query subset and
    derives target masses directly, without the producer's bitset/refine helpers.
    Tiny masks use simple tuple atoms; bounded LRU only memoizes complete values.
    """
    limits = limits or SearchBudget(max_states=2_000_000, max_seconds=120)
    limits.start()
    if (
        proof.version,
        proof.field,
        proof.worlds,
        proof.prior,
        proof.query_costs,
        proof.attempt_cost,
        proof.feedback_rounds,
    ) != (VERSION, 7, 2401, "uniform-a-b-c-r-degree-granted", (1,) + (4,) * 14, 3, 2):
        raise ValueError("unsupported query proof scope")
    if type(proof.budget) is not int or not 3 <= proof.budget <= 16:
        raise ValueError("unsupported certified query budget")
    # Direct tabulation is intentionally independent of model()/refine().
    atoms = tuple(product(range(7), repeat=4))
    values = tuple(
        (a, *((b + r * (a - x)) % 7 for x in range(7)), *((c + r * (b - y)) % 7 for y in range(7)))
        for a, b, c, r in atoms
    )
    choices = []
    for size in range(16):
        if sum(sorted(proof.query_costs)[:size]) + 3 > proof.budget:
            break
        for selected in combinations(range(15), size):
            cost = sum(proof.query_costs[i] for i in selected)
            if cost + 3 <= proof.budget:
                choices.append((cost, selected))
    claimed = dict(proof.choices)
    if len(claimed) != len(proof.choices) or set(claimed) != {s for _, s in choices}:
        raise ValueError("incomplete or duplicate query-choice coverage")

    @lru_cache(maxsize=1024)
    def partition(indices, selected):
        groups = {}
        for i in indices:
            signature = tuple(values[i][q] for q in selected)
            groups.setdefault(signature, []).append(i)
        return tuple(tuple(g) for g in groups.values())

    @lru_cache(maxsize=8192)
    def commits(indices, count):
        masses = {}
        for i in indices:
            target = atoms[i][:3]
            masses[target] = masses.get(target, 0) + 1
        return sum(sorted(masses.values(), reverse=True)[:count])

    @lru_cache(maxsize=8192)
    def second(indices, left):
        limits.tick()
        optimum = 0
        for cost, selected in choices:
            limits.poll()
            if cost + 3 <= left:
                value = sum(
                    commits(group, (left - cost) // 3) for group in partition(indices, selected)
                )
                optimum = max(optimum, value)
        return optimum

    root = tuple(range(2401))
    for cost, selected in choices:
        limits.poll()
        actual = sum(second(group, proof.budget - cost) for group in partition(root, selected))
        if type(claimed[selected]) is not int or claimed[selected] != actual:
            raise ValueError("query success bound fails independent enumeration")
    if proof.upper_mass != max(claimed.values()):
        raise ValueError("incorrect query success aggregate")
    limits.poll()


def payload(proof):
    return asdict(proof)
