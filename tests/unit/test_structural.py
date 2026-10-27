"""Small exact graph oracles independent of the production search algorithms."""

from __future__ import annotations

from collections import deque
from heapq import heappop, heappush
from itertools import permutations, product
from random import Random

import pytest

from nexus.ontology.structural import (
    bank_contiguous_cost,
    distances,
    machine_block_distances,
    minimum_machine_blocks,
    minimum_mask_breaks,
    minimum_optimal_machine_blocks,
    reachable_without_modes,
    reverse_distances,
    trace_diagnostics,
)

type Rows = tuple[tuple[int, ...], ...]


def _macro_blocks(rows: Rows, goal: int, initial: int = 0) -> int | None:
    """A unit edge is the complete positive-power orbit of any one operator."""
    seen = {initial}
    queue = deque([(initial, 0)])
    while queue:
        state, cost = queue.popleft()
        if state == goal:
            return cost
        for row in rows:
            orbit: set[int] = set()
            after = row[state]
            while after not in orbit:
                orbit.add(after)
                if after not in seen:
                    seen.add(after)
                    queue.append((after, cost + 1))
                after = row[after]
    return None


def _enumerated_optimum(rows: Rows, goal: int, initial: int = 0) -> tuple[int | None, int | None]:
    """Enumerate words; a shortest physical path is simple and shorter than N."""
    for length in range(len(rows[0])):
        blocks: list[int] = []
        for word in product(range(len(rows)), repeat=length):
            state = initial
            for mode in word:
                state = rows[mode][state]
            if state == goal:
                blocks.append(sum(i == 0 or mode != word[i - 1] for i, mode in enumerate(word)))
        if blocks:
            return length, min(blocks)
    return None, None


def _heap_breaks(rows: Rows, goal: int, masks: tuple[int, ...], initial: int = 0) -> int | None:
    costs = {initial: 0}
    heap = [(0, initial)]
    while heap:
        cost, state = heappop(heap)
        if costs[state] != cost:
            continue
        if state == goal:
            return cost
        for row in rows:
            after = row[state]
            # Compare individual satisfied bits rather than the production bit operation.
            width = max(masks).bit_length()
            broken = any(
                masks[state] >> bit & 1 and not masks[after] >> bit & 1 for bit in range(width)
            )
            candidate = cost + int(broken)
            if after not in costs or candidate < costs[after]:
                costs[after] = candidate
                heappush(heap, (candidate, after))
    return None


def _ordered_bank_cost(
    rows: Rows, goal: int, banks: tuple[int, ...], initial: int = 0
) -> int | None:
    """Enumerate bank orders, with free forward stage switches and unit actions."""
    best: int | None = None
    for order in permutations(sorted(set(banks))):
        costs = {(initial, 0): 0}
        heap = [(0, initial, 0)]
        while heap:
            cost, state, stage = heappop(heap)
            if cost != costs[state, stage]:
                continue
            if state == goal:
                best = cost if best is None else min(best, cost)
                break
            edges = [
                (row[state], stage, 1)
                for row, bank in zip(rows, banks, strict=True)
                if bank == order[stage]
            ]
            if stage + 1 < len(order):
                edges.append((state, stage + 1, 0))
            for after, next_stage, weight in edges:
                key = after, next_stage
                candidate = cost + weight
                if key not in costs or candidate < costs[key]:
                    costs[key] = candidate
                    heappush(heap, (candidate, after, next_stage))
    return best


def _reverse_reachable(rows: Rows, goal: int, omitted: set[int], initial: int = 0) -> bool:
    reaches = {goal}
    while True:
        expanded = reaches | {
            state
            for state in range(len(rows[0]))
            if any(row[state] in reaches for mode, row in enumerate(rows) if mode not in omitted)
        }
        if expanded == reaches:
            return initial in reaches
        reaches = expanded


def _chain_rows(word: tuple[int, ...], mode_count: int) -> Rows:
    return tuple(
        tuple(
            state + 1 if state < len(word) and word[state] == mode else state
            for state in range(len(word) + 1)
        )
        for mode in range(mode_count)
    )


def test_blocks_support_order_seven_and_zero_cost_cycles() -> None:
    rows = ((1, 2, 3, 4, 5, 6, 0, 7), tuple(range(8)))
    assert distances(rows) == (0, 1, 2, 3, 4, 5, 6, None)
    assert minimum_machine_blocks(rows, 6) == _macro_blocks(rows, 6) == 1
    assert minimum_optimal_machine_blocks(rows, 6) == 1
    assert minimum_machine_blocks(rows, 7) is None
    assert minimum_optimal_machine_blocks(rows, 7) is None
    assert minimum_mask_breaks(rows, 7, (0,) * 8) is None
    assert bank_contiguous_cost(rows, 7, (11, -5)) is None
    assert machine_block_distances(rows) == (0, 1, 1, 1, 1, 1, 1, None)


def test_reverse_distances_use_directed_predecessors_for_noninvertible_modes() -> None:
    rows = ((1, 2, 2, 3, 3), (0, 1, 2, 4, 4))
    assert reverse_distances(rows, goal=2) == (2, 1, 0, None, None)
    assert reverse_distances(rows, goal=0) == (0, None, None, None, None)
    assert reverse_distances(rows, goal=4) == (None, None, None, 1, 0)
    assert distances(rows, initial=2) == (None, None, 0, None, None)


def test_fewer_blocks_can_require_more_primitive_operations() -> None:
    rows = ((1, 2, 3, 4, 4), (0, 4, 2, 3, 4))
    assert distances(rows)[4] == 2
    assert minimum_machine_blocks(rows, 4) == _macro_blocks(rows, 4) == 1
    assert minimum_optimal_machine_blocks(rows, 4) == 2
    assert trace_diagnostics(rows, (0, 0, 0, 0)).machine_blocks == 1
    assert trace_diagnostics(rows, (0, 1)).machine_blocks == 2


def test_mask_cost_counts_operations_and_repeated_reopening() -> None:
    rows = _chain_rows((0,) * 6, 2)
    coordinate_masks = (3, 0, 3, 0, 3, 0, 3)
    bank_masks = (1, 0, 1, 0, 1, 0, 1)
    assert minimum_mask_breaks(rows, 6, coordinate_masks) == 3
    assert minimum_mask_breaks(rows, 6, bank_masks) == 3
    assert _heap_breaks(rows, 6, coordinate_masks) == 3
    report = trace_diagnostics(rows, (0,) * 6, state_masks=coordinate_masks)
    assert report.mask_break_operations == 3


def test_minimum_mask_breaks_can_use_a_longer_successful_word() -> None:
    rows = ((1, 2, 3, 5, 4, 5), (4, 1, 2, 3, 5, 5))
    masks = (1, 1, 1, 1, 0, 1)
    assert distances(rows)[5] == 2
    assert minimum_mask_breaks(rows, 5, masks) == _heap_breaks(rows, 5, masks) == 0
    assert trace_diagnostics(rows, (1, 1), state_masks=masks).mask_break_operations == 1
    assert trace_diagnostics(rows, (0, 0, 0, 0), state_masks=masks).mask_break_operations == 0


def test_bank_contiguous_cost_allows_later_operations_to_complete_earlier_bank() -> None:
    # Modes 0 and 2 share a bank despite being nonadjacent in the table.
    # Its predicate is only completed by mode 1, after leaving that bank.
    rows = _chain_rows((0, 2, 1), 4)
    banks = (400, -8, 400, 31)
    bank_masks = (0, 0, 0, 3)
    assert bank_contiguous_cost(rows, 3, banks) == _ordered_bank_cost(rows, 3, banks) == 3
    report = trace_diagnostics(rows, (0, 2, 1), mode_banks=banks, state_masks=bank_masks)
    assert report.machine_blocks == 3
    assert report.bank_blocks == 2
    assert report.bank_returns == 0
    assert report.mask_break_operations == 0


def test_multiple_bank_returns_make_bank_contiguous_goal_unreachable() -> None:
    word = (0, 1, 0, 2, 1)
    rows = _chain_rows(word, 3)
    banks = (81, -9, 22)
    assert distances(rows)[5] == 5
    assert bank_contiguous_cost(rows, 5, banks) is None
    assert _ordered_bank_cost(rows, 5, banks) is None
    report = trace_diagnostics(rows, word, mode_banks=banks)
    assert report.bank_blocks == 5
    assert report.bank_returns == 2
    for mode in range(3):
        assert not reachable_without_modes(rows, 5, {mode})
    assert reachable_without_modes(rows, 5, set())


def test_bank_contiguous_solution_may_cost_more_than_free_optimum() -> None:
    rows = ((1, 1, 3, 3, 4, 5, 6), (4, 2, 2, 3, 5, 6, 3))
    assert distances(rows)[3] == 3  # A, B, A.
    assert bank_contiguous_cost(rows, 3, (7, -2)) == 4  # B, B, B, B.
    assert _ordered_bank_cost(rows, 3, (7, -2)) == 4


def test_omission_is_joint_and_unused_modes_are_not_required() -> None:
    rows = ((1, 2, 2), (0, 1, 2), (2, 1, 2))
    assert reachable_without_modes(rows, 2, {0})
    assert reachable_without_modes(rows, 2, {2})
    assert reachable_without_modes(rows, 2, {1})
    assert not reachable_without_modes(rows, 2, {0, 2})
    assert not reachable_without_modes(rows, 2, {0, 1, 2})


def test_nonzero_initial_and_empty_successful_word() -> None:
    rows = ((0, 2, 0), (0, 1, 2))
    assert distances(rows, initial=1) == (2, 0, 1)
    assert minimum_machine_blocks(rows, 0, initial=1) == 1
    assert minimum_optimal_machine_blocks(rows, 0, initial=1) == 1
    assert minimum_mask_breaks(rows, 0, (0, 1, 0), initial=1) == 1
    assert bank_contiguous_cost(rows, 0, (-1, 300), initial=1) == 2
    assert reachable_without_modes(rows, 0, {1}, initial=1)
    assert minimum_machine_blocks(rows, 1, initial=1) == 0
    assert minimum_optimal_machine_blocks(rows, 1, initial=1) == 0
    assert minimum_mask_breaks(rows, 1, (0, 1, 0), initial=1) == 0
    assert bank_contiguous_cost(rows, 1, (-1, 300), initial=1) == 0
    assert reachable_without_modes(rows, 1, {0, 1}, initial=1)
    report = trace_diagnostics(rows, (), initial=1, mode_banks=(-1, 300), state_masks=(0, 1, 0))
    assert report.terminal_state == 1
    assert report.operations == report.machine_blocks == report.bank_blocks == 0
    assert report.bank_returns == report.mask_break_operations == 0


def test_trace_noops_count_as_operations_and_diagnostics_are_not_minima() -> None:
    rows = ((0, 1), (0, 1))
    report = trace_diagnostics(rows, (0, 1, 1, 0), mode_banks=(-1, 2), state_masks=(1, 0))
    assert report.terminal_state == 0
    assert report.operations == 4
    assert report.machine_blocks == report.bank_blocks == 3
    assert report.bank_returns == 1
    assert report.mask_break_operations == 0
    unavailable = trace_diagnostics(rows, ())
    assert unavailable.bank_blocks is None
    assert unavailable.bank_returns is None
    assert unavailable.mask_break_operations is None


def test_all_two_mode_three_state_graphs_match_independent_block_oracles() -> None:
    for entries in product(range(3), repeat=6):
        rows = (entries[:3], entries[3:])
        actual_distances = distances(rows)
        actual_blocks = machine_block_distances(rows)
        for goal in range(3):
            distance, optimal_blocks = _enumerated_optimum(rows, goal)
            assert actual_distances[goal] == distance
            assert minimum_optimal_machine_blocks(rows, goal) == optimal_blocks
            assert minimum_machine_blocks(rows, goal) == _macro_blocks(rows, goal)
            assert actual_blocks[goal] == _macro_blocks(rows, goal)
            assert reverse_distances(rows, goal=goal) == tuple(
                _enumerated_optimum(rows, goal, initial)[0] for initial in range(3)
            )


def test_seeded_small_graphs_match_independent_mask_bank_and_omission_oracles() -> None:
    random = Random(27067)
    for _ in range(60):
        rows = tuple(tuple(random.randrange(5) for _ in range(5)) for _ in range(3))
        masks = tuple(random.randrange(8) for _ in range(5))
        banks = (42, -7, random.choice((42, -7, 108)))
        initial = random.randrange(5)
        for goal in range(5):
            assert minimum_mask_breaks(rows, goal, masks, initial=initial) == _heap_breaks(
                rows, goal, masks, initial
            )
            assert bank_contiguous_cost(rows, goal, banks, initial=initial) == _ordered_bank_cost(
                rows, goal, banks, initial
            )
            for omitted in ({0}, {1}, {2}, {0, 2}):
                assert reachable_without_modes(rows, goal, omitted, initial=initial) == (
                    _reverse_reachable(rows, goal, omitted, initial)
                )


@pytest.mark.parametrize("rows", [(), ((),), ((0,), (0, 1)), ((2, 1),), ((True,),)])
def test_invalid_transition_tables_fail_clearly(rows: Rows) -> None:
    with pytest.raises(ValueError):
        distances(rows)


@pytest.mark.parametrize("initial", [-1, 2, True])
def test_invalid_initial_states_fail_clearly(initial: int) -> None:
    with pytest.raises(ValueError, match="initial"):
        distances(((0, 1),), initial=initial)


def test_invalid_goals_masks_banks_and_modes_fail_clearly() -> None:
    rows = ((1, 1),)
    with pytest.raises(ValueError, match="goal"):
        minimum_machine_blocks(rows, 2)
    with pytest.raises(ValueError, match="goal"):
        minimum_optimal_machine_blocks(rows, -1)
    with pytest.raises(ValueError, match="goal"):
        reverse_distances(rows, goal=2)
    for masks in ((1,), (-1, 1), (False, 1)):
        with pytest.raises(ValueError, match="state_masks"):
            minimum_mask_breaks(rows, 1, masks)
    for banks in ((), (1, 2), (False,)):
        with pytest.raises(ValueError, match="mode_banks"):
            bank_contiguous_cost(rows, 1, banks)
    with pytest.raises(ValueError, match="omitted_modes"):
        reachable_without_modes(rows, 1, {1})
    with pytest.raises(ValueError, match="omitted_modes"):
        reachable_without_modes(rows, 1, [0, False])
    with pytest.raises(ValueError, match="modes"):
        trace_diagnostics(rows, (-1,))


@pytest.mark.parametrize("limit", [0, -1, True])
def test_invalid_search_bounds_fail_clearly(limit: int) -> None:
    with pytest.raises(ValueError, match="max_search_states"):
        distances(((0,),), max_search_states=limit)


def test_search_bound_failure_is_distinct_from_unreachability() -> None:
    rows = ((0, 1), (0, 1))
    with pytest.raises(ValueError, match="max_search_states=1"):
        distances(rows, max_search_states=1)
    with pytest.raises(ValueError, match="max_search_states=2"):
        minimum_machine_blocks(rows, 1, max_search_states=2)
    with pytest.raises(ValueError, match="max_search_states=2"):
        machine_block_distances(rows, max_search_states=2)
    with pytest.raises(ValueError, match="max_search_states=2"):
        bank_contiguous_cost(rows, 1, (80, -4), max_search_states=2)
    # The physical state count fits; the optimal DAG needs more augmented keys.
    with pytest.raises(ValueError, match="max_search_states=2"):
        minimum_optimal_machine_blocks(((1, 1), (1, 1)), 1, max_search_states=2)
    assert minimum_machine_blocks(rows, 1, max_search_states=3) is None
    assert bank_contiguous_cost(rows, 1, (80, -4), max_search_states=5) is None
