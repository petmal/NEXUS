"""Exact operator-only metrics for bounded deterministic finite transition tables.

``rows[mode][state]`` is a total transition table over integer states. Costs
count primitive operations, not navigation, take/finish actions, or cognitive
decisions. The empty word succeeds when ``initial == goal``. An unreachable
goal has cost ``None``; an exhausted search bound raises ``ValueError`` instead
of being reported as unreachable. Inputs are not mutated or cached.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Collection, Sequence
from dataclasses import dataclass

__all__ = [
    "TraceDiagnostics",
    "bank_contiguous_cost",
    "distances",
    "machine_block_distances",
    "minimum_machine_blocks",
    "minimum_mask_breaks",
    "minimum_optimal_machine_blocks",
    "reachable_without_modes",
    "reverse_distances",
    "trace_diagnostics",
]

type TransitionRows = Sequence[Sequence[int]]

_DEFAULT_SEARCH_BOUND = 1_000_000


def _validate_rows(rows: TransitionRows, initial: int, max_search_states: int) -> int:
    if type(max_search_states) is not int or max_search_states < 1:
        raise ValueError("max_search_states must be a positive integer")
    if not rows or not rows[0]:
        raise ValueError("transition rows must contain at least one mode and state")
    size = len(rows[0])
    _check_bound(size, max_search_states)
    _validate_state(initial, size, "initial")
    for row in rows:
        if len(row) != size:
            raise ValueError("transition rows must have the same number of states")
        if any(type(after) is not int or not 0 <= after < size for after in row):
            raise ValueError("transition destinations must be integer state indices")
    return size


def _validate_state(state: int, size: int, name: str) -> None:
    if type(state) is not int or not 0 <= state < size:
        raise ValueError(f"{name} must be an integer state index")


def _validate_masks(state_masks: Sequence[int], size: int) -> None:
    if len(state_masks) != size or any(type(mask) is not int or mask < 0 for mask in state_masks):
        raise ValueError("state_masks must contain one nonnegative integer mask per state")


def _validate_banks(mode_banks: Sequence[int], mode_count: int) -> None:
    if len(mode_banks) != mode_count or any(type(bank) is not int for bank in mode_banks):
        raise ValueError("mode_banks must contain one integer bank ID per mode")


def _check_bound(count: int, max_search_states: int) -> None:
    if count > max_search_states:
        raise ValueError(f"structural search exceeds max_search_states={max_search_states}")


def distances(
    rows: TransitionRows,
    *,
    initial: int = 0,
    max_search_states: int = _DEFAULT_SEARCH_BOUND,
) -> tuple[int | None, ...]:
    """Minimum primitive-operation cost to every state, or None if unreachable.

    The bound covers the table's physical state count. Each state is visited
    once; self-loops and noninvertible operators need no special handling.
    """
    size = _validate_rows(rows, initial, max_search_states)
    result: list[int | None] = [None] * size
    result[initial] = 0
    queue = deque([(initial, 0)])
    while queue:
        state, cost = queue.popleft()
        for row in rows:
            after = row[state]
            if result[after] is None:
                result[after] = cost + 1
                queue.append((after, cost + 1))
    return tuple(result)


def minimum_machine_blocks(
    rows: TransitionRows,
    goal: int,
    *,
    initial: int = 0,
    max_search_states: int = _DEFAULT_SEARCH_BOUND,
) -> int | None:
    """Fewest maximal same-mode runs across all successful operation words.

    A 0/1 search retains the last mode: continuing it costs zero; the first
    operation or changing mode costs one. This is exact for arbitrary operator
    orders, including nonpermutations and zero-cost cycles. The bound covers
    both physical states and discovered (state, last-mode) search states.
    """
    size = _validate_rows(rows, initial, max_search_states)
    _validate_state(goal, size, "goal")
    return _machine_block_costs(rows, initial, max_search_states, stop_at=goal)[goal]


def machine_block_distances(
    rows: TransitionRows,
    *,
    initial: int = 0,
    max_search_states: int = _DEFAULT_SEARCH_BOUND,
) -> tuple[int | None, ...]:
    """Fewest same-mode runs to every state, or None when unreachable.

    This all-target counterpart of ``minimum_machine_blocks`` shares one
    augmented 0/1 search, useful when qualifying several targets of a kernel.
    """
    _validate_rows(rows, initial, max_search_states)
    return _machine_block_costs(rows, initial, max_search_states)


def _machine_block_costs(
    rows: TransitionRows,
    initial: int,
    max_search_states: int,
    *,
    stop_at: int | None = None,
) -> tuple[int | None, ...]:
    result: list[int | None] = [None] * len(rows[0])
    costs = {(initial, -1): 0}
    queue = deque([(0, initial, -1)])
    while queue:
        cost, state, previous = queue.popleft()
        if cost != costs[state, previous]:
            continue
        if result[state] is None:
            result[state] = cost
        if state == stop_at:
            break
        for mode, row in enumerate(rows):
            after = row[state]
            weight = int(mode != previous)
            candidate = cost + weight
            key = after, mode
            known = costs.get(key)
            if known is None or candidate < known:
                if known is None:
                    _check_bound(len(costs) + 1, max_search_states)
                costs[key] = candidate
                item = candidate, after, mode
                if weight:
                    queue.append(item)
                else:
                    queue.appendleft(item)
    return tuple(result)


def reverse_distances(
    rows: TransitionRows,
    *,
    goal: int,
    max_search_states: int = _DEFAULT_SEARCH_BOUND,
) -> tuple[int | None, ...]:
    """Minimum primitive-operation cost from each state to the given goal.

    Predecessors are constructed from the supplied directed table; operators
    need not be invertible. These distances support exact remaining cost and
    per-operation excess calculations without modifying player-facing state.
    """
    size = _validate_rows(rows, 0, max_search_states)
    _validate_state(goal, size, "goal")
    predecessors: list[list[int]] = [[] for _ in range(size)]
    for row in rows:
        for before, after in enumerate(row):
            predecessors[after].append(before)
    result: list[int | None] = [None] * size
    result[goal] = 0
    queue = deque([(goal, 0)])
    while queue:
        state, cost = queue.popleft()
        for before in predecessors[state]:
            if result[before] is None:
                result[before] = cost + 1
                queue.append((before, cost + 1))
    return tuple(result)


def minimum_optimal_machine_blocks(
    rows: TransitionRows,
    goal: int,
    *,
    initial: int = 0,
    max_search_states: int = _DEFAULT_SEARCH_BOUND,
) -> int | None:
    """Fewest same-mode runs among primitive-operation-optimal solutions.

    This is a different metric from ``minimum_machine_blocks``: a longer word
    can have fewer runs. Dynamic programming uses only edges advancing one
    level in the shortest-distance DAG. Its search states retain the last
    mode, and are subject to the same bound as the unrestricted block search.
    """
    depth = distances(rows, initial=initial, max_search_states=max_search_states)
    _validate_state(goal, len(depth), "goal")
    goal_depth = depth[goal]
    if goal_depth is None:
        return None
    costs = {(initial, -1): 0}
    queue = deque([(initial, -1, 0)])
    result: int | None = None
    while queue:
        state, previous, level = queue.popleft()
        cost = costs[state, previous]
        if state == goal:
            result = cost if result is None else min(result, cost)
        if level >= goal_depth:
            continue
        for mode, row in enumerate(rows):
            after = row[state]
            if depth[after] != level + 1:
                continue
            key = after, mode
            candidate = cost + int(mode != previous)
            known = costs.get(key)
            if known is None:
                _check_bound(len(costs) + 1, max_search_states)
                costs[key] = candidate
                queue.append((after, mode, level + 1))
            elif candidate < known:
                # FIFO layers finish every predecessor before this key is popped.
                costs[key] = candidate
    return result


def minimum_mask_breaks(
    rows: TransitionRows,
    goal: int,
    state_masks: Sequence[int],
    *,
    initial: int = 0,
    max_search_states: int = _DEFAULT_SEARCH_BOUND,
) -> int | None:
    """Fewest operations unsetting at least one currently satisfied mask bit.

    ``state_masks[s]`` supplies satisfied subgoals at state s. Coordinate masks
    and whole-bank masks use the same algorithm. One operation costs at most
    one, even when it unsets several bits. Repeatedly reopening the same bit
    on different operations counts each time. The minimum ranges over all
    successful words, including words longer than a shortest solution.
    """
    size = _validate_rows(rows, initial, max_search_states)
    _validate_state(goal, size, "goal")
    _validate_masks(state_masks, size)
    costs: list[int | None] = [None] * size
    costs[initial] = 0
    queue = deque([(0, initial)])
    while queue:
        cost, state = queue.popleft()
        if cost != costs[state]:
            continue
        if state == goal:
            return cost
        for row in rows:
            after = row[state]
            weight = int(bool(state_masks[state] & ~state_masks[after]))
            candidate = cost + weight
            known = costs[after]
            if known is None or candidate < known:
                costs[after] = candidate
                if weight:
                    queue.append((candidate, after))
                else:
                    queue.appendleft((candidate, after))
    return None


def bank_contiguous_cost(
    rows: TransitionRows,
    goal: int,
    mode_banks: Sequence[int],
    *,
    initial: int = 0,
    max_search_states: int = _DEFAULT_SEARCH_BOUND,
) -> int | None:
    """Shortest word using each bank in at most one contiguous operation block.

    Bank IDs may be arbitrary integers and modes need not be grouped by bank.
    Banks can be omitted or visited in any order. Leaving a bank does not
    require completing it: later banks may write its coordinates. Search
    retains (state, last bank, used-bank mask), with a bound on discovered
    search states as well as on physical states.
    """
    size = _validate_rows(rows, initial, max_search_states)
    _validate_state(goal, size, "goal")
    _validate_banks(mode_banks, len(rows))
    bank_indices: dict[int, int] = {}
    banks = tuple(bank_indices.setdefault(bank, len(bank_indices)) for bank in mode_banks)
    start = initial, -1, 0
    seen = {start}
    queue = deque([(start, 0)])
    while queue:
        (state, previous, used), cost = queue.popleft()
        if state == goal:
            return cost
        for row, bank in zip(rows, banks, strict=True):
            bit = 1 << bank
            if bank != previous and used & bit:
                continue
            key = row[state], bank, used | bit
            if key not in seen:
                _check_bound(len(seen) + 1, max_search_states)
                seen.add(key)
                queue.append((key, cost + 1))
    return None


def reachable_without_modes(
    rows: TransitionRows,
    goal: int,
    omitted_modes: Collection[int],
    *,
    initial: int = 0,
    max_search_states: int = _DEFAULT_SEARCH_BOUND,
) -> bool:
    """Whether any successful word omits all of the supplied mode indices.

    To prove a mode required, first establish full-table reachability and then
    show that omitting it makes the goal unreachable. Omitting every mode
    still admits the empty word when the initial state is already the goal.
    """
    size = _validate_rows(rows, initial, max_search_states)
    _validate_state(goal, size, "goal")
    if any(type(mode) is not int or not 0 <= mode < len(rows) for mode in omitted_modes):
        raise ValueError("omitted_modes must contain valid integer mode indices")
    omitted = set(omitted_modes)
    allowed = tuple(row for mode, row in enumerate(rows) if mode not in omitted)
    seen = {initial}
    queue = deque([initial])
    while queue:
        state = queue.popleft()
        if state == goal:
            return True
        for row in allowed:
            after = row[state]
            if after not in seen:
                seen.add(after)
                queue.append(after)
    return False


@dataclass(frozen=True, slots=True, kw_only=True)
class TraceDiagnostics:
    """Observed trace counts, never claims about minima over successful words."""

    operations: int
    terminal_state: int
    machine_blocks: int
    bank_blocks: int | None
    bank_returns: int | None
    mask_break_operations: int | None


def trace_diagnostics(
    rows: TransitionRows,
    modes: Sequence[int],
    *,
    initial: int = 0,
    mode_banks: Sequence[int] | None = None,
    state_masks: Sequence[int] | None = None,
    max_search_states: int = _DEFAULT_SEARCH_BOUND,
) -> TraceDiagnostics:
    """Replay a finite mode word and count its runs and mask-breaking operations.

    ``bank_returns`` counts entries into a previously used bank after leaving
    it; this differs from reopening a satisfied bank predicate. Supply whole-
    bank masks to count that through ``mask_break_operations`` instead. No-op
    operations still appear in run counts. Optional unavailable metrics are
    None, while available metrics for the empty trace are zero.
    """
    size = _validate_rows(rows, initial, max_search_states)
    if mode_banks is not None:
        _validate_banks(mode_banks, len(rows))
    if state_masks is not None:
        _validate_masks(state_masks, size)
    if any(type(mode) is not int or not 0 <= mode < len(rows) for mode in modes):
        raise ValueError("modes must contain valid integer mode indices")
    state = initial
    previous = -1
    previous_bank: int | None = None
    used_banks: set[int] = set()
    blocks = bank_blocks = bank_returns = breaks = 0
    for mode in modes:
        blocks += int(mode != previous)
        after = rows[mode][state]
        if state_masks is not None:
            breaks += int(bool(state_masks[state] & ~state_masks[after]))
        if mode_banks is not None:
            bank = mode_banks[mode]
            if bank != previous_bank:
                bank_blocks += 1
                bank_returns += int(bank in used_banks)
                used_banks.add(bank)
            previous_bank = bank
        state, previous = after, mode
    return TraceDiagnostics(
        operations=len(modes),
        terminal_state=state,
        machine_blocks=blocks,
        bank_blocks=bank_blocks if mode_banks is not None else None,
        bank_returns=bank_returns if mode_banks is not None else None,
        mask_break_operations=breaks if state_masks is not None else None,
    )
