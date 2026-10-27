"""Bounded operator-only probe of a proposed three-bank grammar.

This module does not register a playable family or export model tasks. Targets
are selected using physical solvers only. Failing a gate is a research result,
not permission to relax a threshold or replace the fixed construction seeds.
"""

from array import array
from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import product
from random import Random
from time import perf_counter
from typing import Literal

from nexus.evaluation.artifacts import atomic_json
from nexus.ontology import structural
from nexus.ontology.repair.qualification import source_binding

SEEDS = (67, 79, 101, 103)
ATTEMPTS = 32
COUNT, MODULUS, SIZE = 9, 3, 3**9
PLACES = tuple(3**i for i in range(COUNT))
VARIANTS = ("spill-ring", "boundary-crossguard", "all-crossguard", "self-guard")
type Variant = Literal["spill-ring", "boundary-crossguard", "all-crossguard", "self-guard"]


@dataclass(frozen=True)
class Kernel:
    guards: tuple[int, ...]
    gains: tuple[int, ...]
    spill_gains: tuple[int, ...]


def kernels(seed: int):
    rng = Random(f"nexus-interference-v2:{seed}")
    for attempt in range(1, ATTEMPTS + 1):
        guards = [rng.randrange(3) for _ in range(COUNT)]
        for bank in range(3):
            guards[bank * 3 + rng.randrange(3)] = 0
        yield (
            attempt,
            Kernel(
                tuple(guards),
                tuple(rng.randrange(1, 3) for _ in range(COUNT)),
                tuple(rng.randrange(1, 3) for _ in range(COUNT)),
            ),
        )


def wiring(coupled: bool, variant: Variant):
    if variant not in VARIANTS:
        raise ValueError("unknown ternary feasibility grammar")
    result = []
    for mode in range(COUNT):
        bank, register = divmod(mode, 3)
        guard = mode if variant == "self-guard" else bank * 3 + (register + 1) % 3
        spill = bank * 3 + (register + 2) % 3
        if coupled:
            if register == 2:
                spill = ((bank + 1) % 3) * 3 + 1
                if variant == "boundary-crossguard":
                    guard = ((bank + 2) % 3) * 3
            if variant == "all-crossguard":
                guard = ((bank + 1) % 3) * 3 + (register + 1) % 3
        result.append((guard, spill))
    return tuple(result)


def tables(kernel: Kernel, coupled: bool, variant: Variant):
    rows = []
    for mode, (guard, spill) in enumerate(wiring(coupled, variant)):
        row = array("H")
        for state in range(SIZE):
            if state // PLACES[guard] % 3 != kernel.guards[mode]:
                row.append(state)
                continue
            own, other = state // PLACES[mode] % 3, state // PLACES[spill] % 3
            row.append(
                state
                + ((own + kernel.gains[mode]) % 3 - own) * PLACES[mode]
                + ((other + kernel.spill_gains[mode]) % 3 - other) * PLACES[spill]
            )
        rows.append(row)
    return tuple(rows)


def macro_distances(rows):
    """Independent whole-block BFS over complete same-machine orbits.

    No assumption of reversibility or fixed operator period is needed.
    """
    costs = [-1] * SIZE
    costs[0] = 0
    queue = deque([0])
    while queue:
        state = queue.popleft()
        for row in rows:
            after = state
            orbit = {state}
            while (after := row[after]) not in orbit:
                orbit.add(after)
                if costs[after] < 0:
                    costs[after] = costs[state] + 1
                    queue.append(after)
    return tuple(None if v < 0 else v for v in costs)


def scalar_step(kernel, coupled, variant, vector, mode):
    bank, register = divmod(mode, 3)
    guard_bank = bank
    if coupled and variant == "all-crossguard":
        guard_bank = (bank + 1) % 3
    elif coupled and variant == "boundary-crossguard" and register == 2:
        guard_bank = (bank + 2) % 3
    guard = mode if variant == "self-guard" else guard_bank * 3 + (register + 1) % 3
    destination = (
        ((bank + 1) % 3) * 3 + 1 if coupled and register == 2 else bank * 3 + (register + 2) % 3
    )
    after = list(vector)
    if vector[guard] == kernel.guards[mode]:
        after[mode] = (vector[mode] + kernel.gains[mode]) % 3
        after[destination] = (vector[destination] + kernel.spill_gains[mode]) % 3
    return tuple(after)


def prove_transitions(kernel, coupled, variant, rows):
    """Scalar tuple-state oracle independent of compiled arithmetic and wiring()."""
    for vector in product(range(3), repeat=COUNT):
        encoded = sum(v * p for v, p in zip(vector, PLACES, strict=True))
        for mode in range(COUNT):
            after = scalar_step(kernel, coupled, variant, vector, mode)
            expected = sum(v * p for v, p in zip(after, PLACES, strict=True))
            if rows[mode][encoded] != expected:
                raise ValueError("ternary compiled transition disagrees with scalar oracle")
    return SIZE * COUNT


def scalar_bank_reopenings(kernel, variant, target):
    initial = (0,) * COUNT
    costs = {initial: 0}
    queue = [(0, initial)]
    while queue:
        cost, vector = heappop(queue)
        if cost != costs[vector]:
            continue
        if vector == target:
            return cost
        for mode in range(COUNT):
            after = scalar_step(kernel, True, variant, vector, mode)
            weight = int(
                any(
                    vector[b : b + 3] == target[b : b + 3] and after[b : b + 3] != target[b : b + 3]
                    for b in (0, 3, 6)
                )
            )
            if cost + weight < costs.get(after, SIZE):
                costs[after] = cost + weight
                heappush(queue, (cost + weight, after))
    return None


def run(output, *, variants=VARIANTS):
    if (
        not variants
        or len(set(variants)) != len(variants)
        or any(v not in VARIANTS for v in variants)
    ):
        raise ValueError("choose distinct known feasibility variants")
    started = perf_counter()
    sources = source_binding()
    targets = tuple(
        sum(v * p for v, p in zip(vector, PLACES, strict=True))
        for vector in product((1, 2), repeat=COUNT)
    )
    report = {
        "version": "ternary-feasibility-v1",
        "status": "running",
        "sources": sources,
        "state_bound": SIZE,
        "seeds": list(SEEDS),
        "kernel_attempt_limit_per_seed": ATTEMPTS,
        "variants": list(variants),
        "paired_target_gate": "all nine coordinates nonzero and reachable from zero under both conditions",
        "first_admission_gate": {"minimum_machine_blocks": 16},
        "second_admission_gate": {"minimum_whole_bank_reopening_operations": 2},
        "later_gates_not_waived": [
            "long minus short block minimum at least four",
            "required dependency operations",
            "bank-contiguous obstruction",
        ],
        "live_tasks_exported": 0,
        "kernels": [],
        "scope": "Solver-only feasibility. Spill-ring changes write placement only. Crossguard variants also change read placement and are not matched-guard controls. Self-guard changes the guard grammar in both arms, retains matched read/write placement control, and creates irreversible dead ends. Degree equality does not equate graph structure. No model outcomes are used.",
    }
    atomic_json(output, report)
    try:
        for seed in SEEDS:
            for attempt, kernel in kernels(seed):
                independent_cases = {}
                for variant in variants:
                    ind_variant = "self-guard" if variant == "self-guard" else "spill-ring"
                    if ind_variant not in independent_cases:
                        independent = tables(kernel, False, ind_variant)
                        independent_cases[ind_variant] = (
                            structural.distances(independent),
                            prove_transitions(kernel, False, ind_variant, independent),
                        )
                    ind_distance, ind_checks = independent_cases[ind_variant]
                    coupled = tables(kernel, True, variant)
                    distance = structural.distances(coupled)
                    blocks = structural.machine_block_distances(coupled)
                    if blocks != macro_distances(coupled):
                        raise ValueError("ternary block searches disagree")
                    checked = prove_transitions(kernel, True, variant, coupled)
                    paired = [
                        s
                        for s in targets
                        if ind_distance[s] is not None and distance[s] is not None
                    ]
                    candidates = [s for s in paired if blocks[s] >= 16]
                    candidate_proofs = []
                    for goal in candidates:
                        target = tuple(goal // p % 3 for p in PLACES)
                        bank_masks = tuple(
                            sum(
                                (state // PLACES[b] % 27 == goal // PLACES[b] % 27) << (b // 3)
                                for b in (0, 3, 6)
                            )
                            for state in range(SIZE)
                        )
                        bank_minimum = structural.minimum_mask_breaks(coupled, goal, bank_masks)
                        if bank_minimum != scalar_bank_reopenings(kernel, variant, target):
                            raise ValueError("whole-bank reopening searches disagree")
                        candidate_proofs.append(
                            {
                                "target": list(target),
                                "state": goal,
                                "minimum_operations": distance[goal],
                                "minimum_machine_blocks": blocks[goal],
                                "minimum_whole_bank_reopening_operations": bank_minimum,
                                "second_gate_passed": bank_minimum >= 2,
                            }
                        )
                    report["kernels"].append(
                        {
                            "seed": seed,
                            "attempt": attempt,
                            "variant": variant,
                            "guards": list(kernel.guards),
                            "gains": list(kernel.gains),
                            "spill_gains": list(kernel.spill_gains),
                            "paired_targets": len(paired),
                            "independent_reachable_states": sum(
                                d is not None for d in ind_distance
                            ),
                            "coupled_reachable_states": sum(d is not None for d in distance),
                            "maximum_paired_operations": max(
                                (distance[s] for s in paired), default=None
                            ),
                            "maximum_paired_minimum_machine_blocks": max(
                                (blocks[s] for s in paired), default=None
                            ),
                            "maximum_unpaired_minimum_machine_blocks": max(
                                v for v in blocks if v is not None
                            ),
                            "targets_passing_first_gate": candidates,
                            "candidate_proofs": candidate_proofs,
                            "reachable_absorbing_dead_ends": sum(
                                distance[state] is not None
                                and all(row[state] == state for row in coupled)
                                for state in range(SIZE)
                            ),
                            "independent_transition_checks": ind_checks,
                            "coupled_transition_checks": checked,
                            "independent_block_oracle_agrees": True,
                        }
                    )
                atomic_json(output, report)
        if source_binding() != sources:
            raise ValueError("source changed during feasibility probe")
        passed = sum(len(k["targets_passing_first_gate"]) for k in report["kernels"])
        second = sum(
            p["second_gate_passed"] for k in report["kernels"] for p in k["candidate_proofs"]
        )
        report.update(
            status="completed",
            first_gate_candidate_count=passed,
            second_gate_candidate_count=second,
            admission="no-target-passes-tested-gates"
            if not second
            else "later-gates-required-no-admission",
            seconds=perf_counter() - started,
        )
        atomic_json(output, report)
        return report
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
