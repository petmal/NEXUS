"""Operator-only finite W4 and two-module qualifications, not playable families.

All limits and relaxed costs are explicit. No model performance is inferred from
these construction, observability and shortcut checks.
"""

from __future__ import annotations

from functools import cache
from itertools import product
from time import perf_counter

from nexus.evaluation.artifacts import atomic_json
from nexus.ontology.revision.laws import INITIAL, PROGRAMS, advance, display
from nexus.ontology.revision.proof import require, scalar_step
from nexus.provenance import source_digest
from nexus.solver.decision_audit import DecisionAudit
from nexus.solver.finite_machine import FiniteMachine

Program = tuple[int, ...]
State = tuple[int, ...]
WORDS = tuple(w for n in range(1, 7) for w in product((0, 1), repeat=n))
CONTROLS = ((),) + tuple(w for n in range(1, 8) for w in product((0, 1), repeat=n))


def one_link_changes(program: Program) -> tuple[Program, ...]:
    return tuple(
        sorted(
            {program}
            | {program[:i] + (value,) + program[i + 1 :] for i in range(4) for value in range(12)}
        )
    )


def execute(program: Program, state: State, word: tuple[int, ...], *, oracle=False) -> State:
    step = scalar_step if oracle else advance
    for mode in word:
        state = step(program, state, mode)
    return state


def reachable(program: Program, initial: State) -> tuple[State, ...]:
    states = [initial]
    seen = {initial}
    for state in states:
        for mode in (0, 1):
            target = advance(program, state, mode)
            require(target == scalar_step(program, state, mode), "reachability scalar mismatch")
            if target not in seen:
                seen.add(target)
                states.append(target)
    return tuple(states)


def policy_summary(rows: tuple[bytes, ...], winning: tuple[int, ...], worlds: int) -> dict:
    """Public minimax-split heuristic, fully traversed; not a minimum-depth claim."""
    audit = DecisionAudit(worlds, rows, winning)
    nodes = 0
    blocked = []

    @cache
    def visit(mask: int):
        nonlocal nodes
        nodes += 1
        if nodes > 20_000:
            raise RuntimeError("prototype policy node cap; qualification incomplete")
        if audit.common(mask):
            return 0
        q = min(
            range(len(rows)),
            key=lambda q: (
                max((mask & p).bit_count() for p in audit.partitions[q]),
                sum((mask & p).bit_count() ** 2 for p in audit.partitions[q]),
                q,
            ),
        )
        children = tuple(mask & part for part in audit.partitions[q] if mask & part)
        if len(children) == 1:
            blocked.append([i for i in range(worlds) if mask >> i & 1])
            return None
        depths = [visit(child) for child in children]
        return None if None in depths else 1 + max(depths)

    depth = visit(audit.full)
    lowers = [audit.positive_reading_lower(i) for i in range(worlds)]
    return {
        "public_policy_exists_within_declared_queries": depth is not None,
        "greedy_worst_readings": depth,
        "greedy_nodes": nodes,
        "blind_robust_decisions": list(audit.common(audit.full)),
        "certificate_0_1_2_or_at_least_3_histogram": {
            str(v): lowers.count(v) for v in sorted(set(lowers))
        },
        "unresolved_classes_without_common_decision": blocked,
        "decision_masks": list(winning),
        "cost_scope": "Readings and control words treated as atomic; no live action, tool, token or cognitive-depth claim.",
    }


def w4():
    started = perf_counter()
    old = PROGRAMS[5866]
    history = (0, 1)
    current = execute(old, INITIAL, history)
    require(current == execute(old, INITIAL, history, oracle=True), "old state oracle mismatch")
    worlds = one_link_changes(old)
    full_reachability = []
    for state in reachable(old, INITIAL):
        sets = [set(reachable(program, state)) for program in worlds]
        exact_targets = set.intersection(*sets) - {state}
        display_targets = set.intersection(*({display(s) for s in states} for states in sets)) - {
            display(state)
        }
        full_reachability.append(
            {
                "current_state": state,
                "nontrivial_exact_targets": sorted(exact_targets),
                "nontrivial_display_targets": sorted(display_targets),
            }
        )
    outcomes = tuple(tuple(execute(p, current, word) for word in CONTROLS) for p in worlds)
    # Independent scalar transition path for every candidate continuation, not a
    # shared table lookup. Observation predictions are included in these paths.
    for p, row in zip(worlds, outcomes):
        for word, state in zip(CONTROLS, row):
            require(state == execute(p, current, word, oracle=True), "W4 scalar mismatch")
    observations = tuple(
        bytes(display(outcomes[i][CONTROLS.index(word)]) for i in range(len(worlds)))
        for word in WORDS
    )
    common_reachable = set(outcomes[0])
    for row in outcomes[1:]:
        common_reachable.intersection_update(row)
    targets = sorted(common_reachable - {current})

    def analyze(target, visible=False):
        wins = tuple(
            sum(
                1 << i
                for i, row in enumerate(outcomes)
                if (display(row[j]) == target if visible else row[j] == target)
            )
            for j in range(len(CONTROLS))
        )
        covered = 0
        for mask in wins:
            covered |= mask
        missing = [i for i in range(len(worlds)) if not covered >> i & 1]
        if missing:
            return {
                "target": target,
                "individually_solvable": False,
                "unsolvable_world_indices": missing,
            }
        result = policy_summary(observations, wins, len(worlds))
        shortest = [
            next(len(CONTROLS[j]) for j, mask in enumerate(wins) if mask >> i & 1)
            for i in range(len(worlds))
        ]
        result.update(
            target=target,
            individually_solvable=True,
            known_new_law_control_lengths=shortest,
            blind_robust_words=[CONTROLS[j] for j in result["blind_robust_decisions"]],
            unchanged_law_plan_success_worlds=sum(
                bool(wins[j] >> i & 1)
                for i in range(len(worlds))
                for j in [
                    next(
                        k
                        for k, word in enumerate(CONTROLS)
                        if (
                            display(execute(old, current, word)) == target
                            if visible
                            else execute(old, current, word) == target
                        )
                    )
                ]
            ),
        )
        return result

    exact = [analyze(target) for target in targets]
    # One focused redesign: retain the law, state, histories and prior; expose a
    # display-valued control target instead of demanding an exact hidden state.
    visible = [analyze(value, True) for value in range(3) if value != display(current)]
    return {
        "version": "w4-bounded-poc-v1",
        "old_program": old,
        "old_history": history,
        "reconstructed_current_state": current,
        "law_change_contract": "Zero or one of four directed links changes once, after the disclosed old history; stationary thereafter.",
        "worlds": worlds,
        "control_vocabulary": {
            "binary_words_through_length": 7,
            "includes_empty": True,
            "count": len(CONTROLS),
        },
        "observation_contract": "Readonly clone of the current carrier; execute a binary word of length 1..6 and report the final display. Every experiment starts at that same current state; committing a control word uses the real carrier.",
        "exact_state_targets_reachable_in_every_world": targets,
        "exact_state_candidates": exact,
        "all_history_reachability_across_every_old_reachable_state": full_reachability,
        "focused_redesign": "A directly observable display goal, with unchanged physics and prior.",
        "display_goal_candidates": visible,
        "controls": {
            "supplied_state": "Same posterior/control problem; removes deterministic reconstruction from old law/history.",
            "supplied_new_law": "Singleton law; control length enumerated per world; reconstruct current state from old law/history.",
            "supplied_both": "Singleton law and explicit state; identical mechanical reachability; no inference observations required.",
        },
        "novelty_gate": "A winning public policy alone is insufficient. Reject promotion when no exact-state candidate qualifies, or a blind/short identify-then-execute policy trivializes the intended contrast. Display redesign is reported separately.",
        "production_family_admitted": False,
        "empirical_difficulty_calibrated": False,
        "seconds": perf_counter() - started,
    }


def cascade_step(
    programs: tuple[Program, Program], states: tuple[State, State], mode: int, *, oracle=False
):
    step = scalar_step if oracle else advance
    left = step(programs[0], states[0], mode)
    right = step(programs[1], states[1], (0, 1, 0)[left[0] % 3])
    return left, right


@cache
def cascade_machine(programs: tuple[Program, Program]) -> FiniteMachine:
    initial = (INITIAL, INITIAL)
    states = [initial]
    indices = {initial: 0}
    rows: list[list[int]] = [[], []]
    for state in states:
        for mode in (0, 1):
            target = cascade_step(programs, state, mode)
            require(
                target == cascade_step(programs, state, mode, oracle=True),
                "cascade scalar mismatch",
            )
            if target not in indices:
                require(len(states) < 3136, "cascade reachable state cap")
                indices[target] = len(states)
                states.append(target)
            rows[mode].append(indices[target])
    return FiniteMachine(tuple(display(s[1]) for s in states), tuple(tuple(row) for row in rows))


def machine_read(machine: FiniteMachine, word: tuple[int, ...]):
    state = machine.initial
    for mode in word:
        state = machine.transitions[mode][state]
    return machine.outputs[state]


def nw2():
    started = perf_counter()
    old = (PROGRAMS[5866], PROGRAMS[6464])
    worlds = tuple(
        sorted(
            {(p, old[1]) for p in one_link_changes(old[0])}
            | {(old[0], p) for p in one_link_changes(old[1])}
        )
    )
    baseline = cascade_machine(old)
    baseline_signature = baseline.signature()
    machines = tuple(cascade_machine(p) for p in worlds)
    # Bounded vocabulary: no repair, restore upstream, restore downstream.
    repaired = tuple(
        tuple(cascade_machine(pair) for pair in (p, (old[0], p[1]), (p[0], old[1]))) for p in worlds
    )
    winning = tuple(
        sum(1 << i for i, row in enumerate(repaired) if row[j].signature() == baseline_signature)
        for j in range(3)
    )
    for i, row in enumerate(repaired):
        for j, machine in enumerate(row):
            require(
                (machine.counterexample(baseline) is None) == bool(winning[j] >> i & 1),
                "cascade full-history equivalence disagreement",
            )
    end_rows = tuple(bytes(machine_read(m, word) for m in machines) for word in WORDS)
    tap_rows = tuple(bytes(display(execute(p[0], INITIAL, word)) for p in worlds) for word in WORDS)
    clamp_rows = tuple(
        bytes(display(execute(p[1], INITIAL, word)) for p in worlds) for word in WORDS
    )
    end = policy_summary(end_rows, winning, len(worlds))
    isolated = policy_summary(tap_rows + clamp_rows, winning, len(worlds))
    assisted = policy_summary(end_rows + tap_rows + clamp_rows, winning, len(worlds))
    all_history_groups = {}
    for i, machine in enumerate(machines):
        all_history_groups.setdefault(machine.signature(), []).append(i)
    unresolvable = []
    for group in all_history_groups.values():
        mask = sum(1 << i for i in group)
        if not any(mask & ~win == 0 for win in winning):
            unresolvable.append(
                {
                    "world_indices": group,
                    "accepted_decisions_by_world": {
                        str(i): [j for j, win in enumerate(winning) if win >> i & 1] for i in group
                    },
                }
            )
    # End-to-end observations preserve correlations; compare actual world pairs
    # with the Cartesian product of their projections to expose unsound factoring.
    correlation = None
    for q, row in enumerate(end_rows):
        for value in set(row):
            pairs = [worlds[i] for i, output in enumerate(row) if output == value]
            product_size = len({p[0] for p in pairs}) * len({p[1] for p in pairs})
            if product_size > len(pairs):
                correlation = {
                    "query": WORDS[q],
                    "output": value,
                    "actual_joint_worlds": len(pairs),
                    "independent_product_worlds": product_size,
                }
                break
        if correlation:
            break
    return {
        "version": "nw2-bounded-poc-v1",
        "known_reference_programs": old,
        "world_count": len(worlds),
        "worlds": worlds,
        "contract": {
            "faults": "At most one module has at most one changed link; zero faults allowed.",
            "decoder": [0, 1, 0],
            "timing": "Advance upstream on external input, decode its NEW display, then advance downstream once.",
            "initialization": "Both modules start at (2,1,1,1). Every query resets both modules to this initialization.",
            "end_to_end_observation": "Only final downstream display for a word of length 1..6.",
            "tap_control": "Final upstream display for the same reset word.",
            "clamp_control": "Reset downstream; replace incoming signal with the chosen binary word; expose final downstream display.",
            "repairs": ["none", "restore known upstream", "restore known downstream"],
            "acceptance": "Full-history downstream display equivalence to the healthy cascade from the specified initialization, not physical wiring identity.",
        },
        "end_to_end": end,
        "independent_modules_control": isolated,
        "tap_and_clamp_assistance": assisted,
        "all_history_end_to_end_equivalence_classes": len(all_history_groups),
        "all_history_indistinguishable_groups_without_common_repair": unresolvable,
        "correlation_counterexample": correlation,
        "qualification_size": {
            "world_cap": 16384,
            "decision_masks": 3,
            "decision_mask_cap": 256,
            "query_rows_with_controls": len(end_rows + tap_rows + clamp_rows),
            "table_cells": len(worlds) * len(end_rows + tap_rows + clamp_rows),
            "table_cell_cap": 16_000_000,
            "largest_reachable_joint_machine": max(len(m.outputs) for m in machines),
        },
        "minimum_local_repair_identity_required": False,
        "production_family_admitted": False,
        "empirical_difficulty_calibrated": False,
        "seconds": perf_counter() - started,
    }


def run(output):
    source = source_digest()
    report = {"status": "running", "source_sha256": source}
    atomic_json(output, report)
    try:
        report["W4"] = w4()
        atomic_json(output, report)
        report["NW2"] = nw2()
        require(source == source_digest(), "source changed during prototype qualification")
        report["status"] = "completed"
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(output, report)
        raise
    atomic_json(output, report)
    return report
