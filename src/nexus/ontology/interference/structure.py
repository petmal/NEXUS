"""Operator-only structural costs and post-attempt trajectory diagnostics.

A machine block is a maximal consecutive sequence of the same machine in an
operation word, regardless of its repetition count. It is not a cognitive unit.
A bank reopening is one operation that unsets at least one fully matched bank.
"""

from functools import lru_cache

from nexus.ontology import structural
from nexus.ontology.interference.laws import decode, encode, tables
from nexus.ontology.interference.schema import SIZE


@lru_cache(maxsize=32)
def masks(target):
    coordinates, banks = [], []
    for state in range(SIZE):
        vector = decode(state)
        coordinates.append(sum((v == t) << i for i, (v, t) in enumerate(zip(vector, target))))
        banks.append(sum((vector[b : b + 3] == target[b : b + 3]) << (b // 3) for b in (0, 3)))
    return tuple(coordinates), tuple(banks)


@lru_cache(maxsize=32)
def metrics(spec):
    rows = tables(spec.resolved, spec.options.coupling)
    goal = encode(spec.target)
    coordinate_masks, bank_masks = masks(spec.target)
    return {
        "minimum_machine_blocks": structural.minimum_machine_blocks(rows, goal),
        "minimum_machine_blocks_on_optimal_paths": structural.minimum_optimal_machine_blocks(
            rows, goal
        ),
        "minimum_coordinate_goal_breaks": structural.minimum_mask_breaks(
            rows, goal, coordinate_masks
        ),
        "minimum_whole_bank_reopening_operations": structural.minimum_mask_breaks(
            rows, goal, bank_masks
        ),
    }


@lru_cache(maxsize=32)
def remaining_operations(spec):
    return structural.reverse_distances(
        tables(spec.resolved, spec.options.coupling), goal=encode(spec.target)
    )


def trajectory(spec, trace):
    """Costs ignore the remaining budget, so incomplete attempts remain interpretable.

    `avoidable_actions_so_far` equals accepted actions plus the physical minimum
    still needed, minus the original minimum. A failed/no-op action can increase
    it. `success_excess_actions` is only defined for a successful finish. Counts
    of blocks refer to the operation subsequence; reads/probes don't add a block.
    """
    distance = remaining_operations(spec)
    coordinate_masks, bank_masks = masks(spec.target)
    initial = distance[0]
    if initial is None:
        raise ValueError("structural diagnostics require a reachable target")
    registers = (0,) * len(spec.target)
    state = 0
    carried = False
    previous = None
    blocks = coordinate_breaks = bank_breaks = unchanged = 0
    first_loss = None
    avoidable = 0
    remaining = initial + 2
    success = False
    for record in trace:
        action = record.action
        success = False
        if action.type == "take" and action.artifact == "seal":
            carried = True
        elif action.type == "drop" and action.artifact == "seal":
            carried = False
        elif action.type == "operate":
            payload = next(
                event.details["result"]["payload"]
                for event in record.events
                if "result" in event.details
            )
            registers = tuple(payload["registers"])
            after = encode(registers)
            coordinate_breaks += bool(coordinate_masks[state] & ~coordinate_masks[after])
            bank_breaks += bool(bank_masks[state] & ~bank_masks[after])
            unchanged += after == state
            blocks += action.machine != previous
            previous, state = action.machine, after
        elif action.type == "finish":
            success = carried and registers == spec.target
        cost = distance[state]
        if cost is None:
            raise ValueError("trace left the reversible reachable component")
        remaining = 0 if success else cost + 1 + int(not carried)
        updated = record.turn + remaining - (initial + 2)
        if updated < avoidable:
            raise ValueError("trace contradicts exact remaining-action distances")
        if first_loss is None and updated > 0:
            first_loss = record.turn
        avoidable = updated
    return {
        "machine_blocks": blocks,
        "coordinate_goal_breaking_operations": coordinate_breaks,
        "whole_bank_reopening_operations": bank_breaks,
        "unchanged_operations": unchanged,
        "remaining_minimum_actions": remaining,
        "avoidable_actions_so_far": avoidable,
        "first_loss_of_optimality_turn": first_loss,
        "success_excess_actions": avoidable if success else None,
    }
