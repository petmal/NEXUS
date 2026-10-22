"""Independent scalar conservation and product-machine oracle for revision.

The oracle below does not call runtime transfer, advance, display or minimization.
Production data is read only as the object under test. Checks use exceptions, not
assertions, so optimized Python cannot disable the qualification proof.
"""

from __future__ import annotations

from collections import deque
from functools import lru_cache
from itertools import combinations, product
from time import perf_counter


def require(condition, message):
    if not condition:
        raise ValueError(message)


def scalar_step(program, state, mode):
    values = list(state)
    for code in program[mode * 2 : mode * 2 + 2]:
        source = code // 3
        destination = code % 3
        destination += destination >= source
        demand = 2 if values[destination] & 1 else 1
        moved = demand if values[source] >= demand else values[source]  # noqa: FURB136 -- independent scalar oracle
        values[source] = values[source] - moved
        values[destination] = values[destination] + moved
    return tuple(values)


def scalar_counterexample(left, right, modes=(0, 1)):
    initial = (2, 1, 1, 1)
    pending = deque([((initial, initial), ())])
    seen = {(initial, initial)}
    while pending:
        (a, b), history = pending.popleft()
        if a[0] % 3 != b[0] % 3:
            return history
        for mode in modes:
            pair = scalar_step(left, a, mode), scalar_step(right, b, mode)
            if pair not in seen:
                seen.add(pair)
                pending.append((pair, (*history, mode)))
    return None


@lru_cache(maxsize=32)
def prove_no_three_reading_certificate(mask, truth):
    """Independent exhaustive check, without the certificate search's pruning.

    The complete observation table is separately checked against scalar physics.
    This checks every distinct 0/1/2/3-reading actual-outcome intersection. It
    deliberately makes no claim about binary finish feedback or adaptive rounds.
    """
    from nexus.ontology.revision.laws import compiled

    prior = compiled()
    goal = 1 << truth
    require(bool(mask & goal) and mask != goal, "zero-reading certificate exists")
    survivors = tuple(
        sorted({parts[prior.rows[truth][q]] & mask for q, parts in enumerate(prior.partitions)})
    )
    require(goal not in survivors, "one-reading certificate exists")
    require(
        all(a & b != goal for a, b in combinations(survivors, 2)), "two-reading certificate exists"
    )
    triples = 0
    for a, b, c in combinations(survivors, 3):
        require(a & b & c != goal, "three-reading certificate exists")
        triples += 1
    return {
        "passed": True,
        "distinct_outcome_masks": len(survivors),
        "triples_checked": triples,
        "scope": "reading-only; no finish feedback",
    }


def prove():
    from nexus.ontology.revision.laws import (
        INITIAL,
        PROGRAMS,
        QUERIES,
        STATES,
        compiled,
        machine,
    )

    start = perf_counter()
    prior = compiled()
    require(PROGRAMS == tuple(product(range(12), repeat=4)), "incomplete wiring grammar")
    transition_checks = equivalence_checks = 0
    for index, program in enumerate(PROGRAMS):
        m = machine(program)
        for state_index, state in enumerate(STATES):
            for mode in (0, 1):
                expected = scalar_step(program, state, mode)
                require(min(expected) >= 0 and sum(expected) == 5, "conservation failure")
                require(
                    STATES[m.transitions[mode][state_index]] == expected,
                    "compiled transition mismatch",
                )
                transition_checks += 1
        representative = prior.representatives[prior.program_classes[index]]
        require(scalar_counterexample(program, representative) is None, "false behavioral merge")
        equivalence_checks += 1
    reading_checks = 0
    for program, row in zip(prior.representatives, prior.rows):
        histories = {(): INITIAL}
        for index, word in enumerate(QUERIES):
            state = scalar_step(program, histories[word[:-1]], word[-1])
            histories[word] = state
            require(row[index] == state[0] % 3, "observation table mismatch")
            reading_checks += 1
    # Distinct finite rows supply actual counterexamples between every pair of
    # representatives. Product traversal above proves equivalence within classes.
    require(len(set(prior.rows)) == len(prior.rows), "laboratory identifiability failure")
    require(len(set(prior.program_classes)) == len(prior.rows), "class coverage mismatch")
    return {
        "passed": True,
        "programs": len(PROGRAMS),
        "states": len(STATES),
        "behavior_classes": len(prior.rows),
        "independent_transitions": transition_checks,
        "independent_all_history_equivalence_checks": equivalence_checks,
        "independent_reading_checks": reading_checks,
        "laboratory_horizon_identifies_all_history_classes": True,
        "seconds": perf_counter() - start,
    }
