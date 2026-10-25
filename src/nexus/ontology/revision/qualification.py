"""Exact goal-relevant certificates and scoped shortcuts for model revision.

An actual-outcome certificate is optimistic, not a worst-case adaptive policy.
Search caps raise; they never admit a world or masquerade as an impossibility.

For r distinct informative reads and g rejected behavioral classes, replace each
rejection with one legal query separating that class from truth. Distinct compiled
rows guarantee such a query. Thus the minimum certificate C <= r+g. Reads cost
configure+read (the default query is already archived); distinct rejected builds
cost at least install+finish. Final take/install/finish costs three, plus a final
configuration unless the default build is correct. Therefore total actions are
at least base+2*(r+g) >= base+2*C; certificate_witness attains this bound. This is
an optimistic evidence-supported branch, not a worst-case policy minimum.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache, lru_cache

from nexus.ontology.revision.inference import choose
from nexus.ontology.revision.laws import (
    QUERIES,
    QUERY_INDEX,
    class_id,
    compiled,
    machine,
    prior_mask,
)
from nexus.solver.finite_machine import FiniteMachine


class QualificationLimit(RuntimeError):
    pass


@dataclass(frozen=True)
class Certificate:
    readings: int
    queries: tuple[tuple[int, ...], ...]
    search_nodes: int


def minimum_certificate(
    mask: int,
    truth: int,
    *,
    max_nodes: int = 200_000,
    query_indices: tuple[int, ...] | None = None,
) -> Certificate:
    """Exact minimum set of truthful legal observations supporting one behavior."""
    prior = compiled()
    goal = 1 << truth
    if not mask & goal:
        raise ValueError("truth is outside the public prior")
    rivals = mask & ~goal
    indices = tuple(range(len(QUERIES))) if query_indices is None else query_indices
    if len(set(indices)) != len(indices) or any(
        type(q) is not int or not 0 <= q < len(QUERIES) for q in indices
    ):
        raise ValueError("query indices must be distinct legal indices")
    choices = {}
    closure = mask
    for q in indices:
        parts = prior.partitions[q]
        closure &= parts[prior.rows[truth][q]]
        remaining = parts[prior.rows[truth][q]] & rivals
        choices.setdefault(remaining, q)
    if closure != goal:
        raise ValueError("allowed queries do not identify the target behavior")
    ordered = sorted(choices, key=lambda m: (m.bit_count(), choices[m]))
    useful = []
    for candidate in ordered:
        if not any(candidate & better == better for better in useful):
            useful.append(candidate)
    nodes = 0

    @cache
    def search(remaining, depth):
        nonlocal nodes
        nodes += 1
        if nodes > max_nodes:
            raise QualificationLimit("certificate search node cap reached; no admission")
        if remaining == 0:
            return ()
        if depth == 0:
            return None
        projected = {}
        for candidate in useful:
            reduced = remaining & candidate
            if reduced != remaining:
                projected.setdefault(reduced, choices[candidate])
        if not projected:
            return None
        if 0 in projected:
            return (projected[0],)
        maximum_gain = max((remaining ^ reduced).bit_count() for reduced in projected)
        if (remaining.bit_count() + maximum_gain - 1) // maximum_gain > depth:
            return None
        # Every cover must remove this rival. Query order is irrelevant for an
        # actual-outcome certificate, so consider a covering query first.
        bits = [1 << i for i in range(remaining.bit_length()) if remaining >> i & 1]
        pivot = min(bits, key=lambda bit: sum(not reduced & bit for reduced in projected))
        for reduced in sorted(projected, key=int.bit_count):
            if reduced & pivot:
                continue
            suffix = search(reduced, depth - 1)
            if suffix is not None:
                return (projected[reduced], *suffix)
        return None

    # The seven-reading proof uses all queries. A restricted alphabet can need
    # more readings; one useful query per rival is always a finite upper bound.
    upper = 7 if query_indices is None else min(len(indices), rivals.bit_count())
    for depth in range(upper + 1):
        result = search(rivals, depth)
        if result is not None:
            return Certificate(depth, tuple(QUERIES[q] for q in result), nodes)
    raise QualificationLimit("no certificate within the proved public-policy bound")


@lru_cache(maxsize=1)
def unary_signatures():
    result = []
    for program in compiled().representatives:
        m = machine(program)
        result.append(
            tuple(FiniteMachine(m.outputs, (row,), m.initial).signature() for row in m.transitions)
        )
    return tuple(result)


@lru_cache(maxsize=4096)
def policy_reading_bound(mask):
    query = choose(mask)
    if query is None:
        return 0
    return 1 + max(
        policy_reading_bound(mask & part)
        for part in compiled().partitions[QUERY_INDEX[query]]
        if mask & part
    )


def audit(spec, world):
    prior = compiled()
    truth = class_id(world.program)
    mask = prior_mask(spec)
    certificate = minimum_certificate(mask, truth)
    unary = unary_signatures()
    compatible = [i for i in range(len(prior.rows)) if mask >> i & 1]
    single = [sum(unary[i][mode] == unary[truth][mode] for i in compatible) for mode in range(2)]
    joint = sum(unary[i] == unary[truth] for i in compatible)
    provisional = spec.provisional
    counterexample = (
        None if provisional is None else machine(world.program).counterexample(machine(provisional))
    )
    after_counterexample = None
    remaining_readings = None
    if counterexample is not None and 1 <= len(counterexample) <= 8:
        q = QUERY_INDEX[counterexample]
        reduced = mask & prior.partitions[q][prior.rows[truth][q]]
        after_counterexample = reduced.bit_count()
        remaining_readings = minimum_certificate(reduced, truth).readings
    length_closures = []
    closure = mask
    for length in range(1, 9):
        for q, word in enumerate(QUERIES):
            if len(word) == length:
                closure &= prior.partitions[q][prior.rows[truth][q]]
        length_closures.append(closure.bit_count())
    histograms = {}
    order_witness = None
    for q, word in enumerate(QUERIES):
        histogram = (word.count(0), word.count(1))
        previous = histograms.setdefault(histogram, (word, prior.rows[truth][q]))
        if previous[1] != prior.rows[truth][q]:
            order_witness = (previous[0], word)
            break
    return {
        "prior_behavior_classes": mask.bit_count(),
        "actual_minimal_machine_states": len(prior.signatures[truth]),
        "minimum_reading_only_certificate": certificate.readings,
        "minimum_supported_actions": (3 if class_id((0, 0, 0, 0)) == truth else 4)
        + 2 * certificate.readings,
        "minimum_scope": "Optimistic actual-outcome supported finish, not guaranteed worst-case policy cost. Includes take, reader configuration/read pairs, installation and finish; binary rejected builds cannot lower this minimum.",
        "certificate_queries": certificate.queries,
        "certificate_search_nodes": certificate.search_nodes,
        "reference_worst_case_readings": policy_reading_bound(mask),
        "single_mode_all_history_closure": single,
        "combined_single_mode_all_history_closure": joint,
        "provisional_matches_archive": provisional is None
        or tuple(prior.rows[class_id(provisional)][:2]) == spec.archive,
        "provisional_is_globally_valid": None if provisional is None else counterexample is None,
        "provisional_counterexample": counterexample,
        "counterexample_is_legal_query": counterexample is not None
        and 1 <= len(counterexample) <= 8,
        "classes_after_provisional_counterexample": after_counterexample,
        "minimum_additional_reading_certificate_after_counterexample": remaining_readings,
        "all_queries_through_length_closure": length_closures,
        "order_sensitive_witness": order_witness,
        "blind_supported_build_exists": mask.bit_count() == 1,
        "blind_guess_probability": None,
        "blind_guess_note": "No probability is assigned to arbitrary hidden wirings or behavioral classes. One unsupported guess may win; this does not establish evidence support.",
        "full_grammar_programs": len(prior.program_classes),
        "full_grammar_behavior_classes": len(prior.rows),
        "empirical_difficulty_calibrated": False,
        "deep_tier_admitted": False,
    }
