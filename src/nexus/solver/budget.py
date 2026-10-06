"""Compact exact at-most-budget facts for deterministic minimax search."""


class BudgetMemo:
    """Retain the largest failing and smallest winning budget for each state/belief.

    Positive action costs and finishing early make feasibility monotone. Budgets
    strictly between the bounds remain unknown and must be searched.
    """

    def __init__(self):
        self.entries: dict[tuple[int, frozenset[int]], tuple[int, int | float]] = {}
        self.hits = 0

    def get(self, key: tuple[int, frozenset[int], int]) -> bool | None:
        state, belief, budget = key
        failed, won = self.entries.get((state, belief), (-1, float("inf")))
        answer = False if budget <= failed else True if budget >= won else None
        self.hits += answer is not None
        return answer

    def __setitem__(self, key: tuple[int, frozenset[int], int], value: bool) -> None:
        state, belief, budget = key
        failed, won = self.entries.get((state, belief), (-1, float("inf")))
        failed, won = (failed, min(won, budget)) if value else (max(failed, budget), won)
        if failed >= won:
            raise AssertionError("contradictory exact budget facts")
        self.entries[(state, belief)] = (failed, won)

    def __len__(self) -> int:
        return len(self.entries)
