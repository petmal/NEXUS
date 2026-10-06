"""Opt-in research switches; ordinary generation retains the baseline solver."""

from contextlib import contextmanager
from contextvars import ContextVar

SEARCH_MODE = ContextVar("nexus_solver_experiment", default="baseline")
MODES = ("baseline", "intern", "bounds", "combined")


@contextmanager
def solver_experiment(mode: str):
    if mode not in MODES:
        raise ValueError(f"unknown solver experiment: {mode}")
    token = SEARCH_MODE.set(mode)
    try:
        yield
    finally:
        SEARCH_MODE.reset(token)


class BudgetMemo:
    """Exact at-most-budget facts, optionally closed under budget monotonicity."""

    def __init__(self, monotone: bool):
        self.monotone = monotone
        self.entries = {}
        self.hits = 0

    def get(self, key):
        if not self.monotone:
            answer = self.entries.get(key)
        else:
            state, belief, budget = key
            failed, won = self.entries.get((state, belief), (-1, float("inf")))
            answer = False if budget <= failed else True if budget >= won else None
        self.hits += answer is not None
        return answer

    def __setitem__(self, key, value):
        if not self.monotone:
            self.entries[key] = value
            return
        state, belief, budget = key
        pair = (state, belief)
        failed, won = self.entries.get(pair, (-1, float("inf")))
        if value:
            won = min(won, budget)
        else:
            failed = max(failed, budget)
        if failed >= won:
            raise AssertionError("contradictory exact budget facts")
        self.entries[pair] = (failed, won)

    def __len__(self):
        return len(self.entries)
