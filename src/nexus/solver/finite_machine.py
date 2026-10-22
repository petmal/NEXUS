"""Exact observable behavior of finite, deterministic machines.

This is a semantic compiler, not a difficulty qualifier. Canonical minimization
includes every reachable state and every symbol, without a history-length cutoff.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class FiniteMachine:
    outputs: tuple[int, ...]
    transitions: tuple[tuple[int, ...], ...]
    initial: int = 0

    def __post_init__(self):
        size = len(self.outputs)
        if (
            not size
            or type(self.initial) is not int
            or not 0 <= self.initial < size
            or not self.transitions
        ):
            raise ValueError("finite machine requires states, an initial state and inputs")
        if (
            not isinstance(self.outputs, tuple)
            or any(type(v) is not int for v in self.outputs)
            or not isinstance(self.transitions, tuple)
            or any(not isinstance(row, tuple) for row in self.transitions)
        ):
            raise ValueError("finite machine requires immutable integer output/transition tuples")
        if any(
            len(row) != size or any(type(s) is not int or not 0 <= s < size for s in row)
            for row in self.transitions
        ):
            raise ValueError("finite-machine transition leaves its declared state space")

    def signature(self) -> tuple[tuple[int, ...], ...]:
        """Canonical minimal Moore machine, ordered by input-labelled traversal."""
        reachable = [self.initial]
        indices = {self.initial: 0}
        for state in reachable:
            for row in self.transitions:
                successor = row[state]
                if successor not in indices:
                    indices[successor] = len(reachable)
                    reachable.append(successor)
        labels = [self.outputs[state] for state in reachable]
        while True:
            classes = {}
            refined = []
            for index, state in enumerate(reachable):
                key = (labels[index], *(labels[indices[row[state]]] for row in self.transitions))
                refined.append(classes.setdefault(key, len(classes)))
            if refined == labels:
                break
            labels = refined
        representatives = {}
        for index, state in enumerate(reachable):
            representatives.setdefault(labels[index], state)
        pending = [labels[0]]
        canonical = {pending[0]: 0}
        result = []
        for label in pending:
            state = representatives[label]
            successors = []
            for row in self.transitions:
                target = labels[indices[row[state]]]
                if target not in canonical:
                    canonical[target] = len(pending)
                    pending.append(target)
                successors.append(canonical[target])
            result.append((self.outputs[state], *successors))
        return tuple(result)

    def counterexample(self, other: FiniteMachine) -> tuple[int, ...] | None:
        """Shortest distinguishing input history; None means all-history equivalence."""
        if len(self.transitions) != len(other.transitions):
            raise ValueError("finite machines must share an input alphabet")
        initial = (self.initial, other.initial)
        pending = deque([(initial, ())])
        seen = {initial}
        while pending:
            (left, right), word = pending.popleft()
            if self.outputs[left] != other.outputs[right]:
                return word
            for symbol, (a, b) in enumerate(zip(self.transitions, other.transitions)):
                successor = (a[left], b[right])
                if successor not in seen:
                    seen.add(successor)
                    pending.append((successor, (*word, symbol)))
        return None
