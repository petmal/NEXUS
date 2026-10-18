"""Exact correlated posteriors, including physical operations and failed finishes."""

from __future__ import annotations

from functools import lru_cache

from nexus.ontology.history.laws import (
    WORLD_INDEX,
    WORLDS,
    decisions,
    transitions,
    word_index,
    words,
)


def indices(mask: int):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


@lru_cache(maxsize=2048)
def normalized_states(history: tuple[int, ...]) -> bytes:
    if not history:
        return bytes(256)
    parent = normalized_states(history[:-1])
    mode = history[-1]
    return bytes(table[mode][parent[i]] for i, table in enumerate(transitions()))


@lru_cache(maxsize=2048)
def partitions(history: tuple[int, ...], channel: int) -> tuple[int, ...]:
    masks = [0] * 9
    for law, state in enumerate(normalized_states(history)):
        if channel == 0:
            masks[state % 9] |= 15 << (law * 4)
            continue
        table = transitions()[law]
        for orientation in (1, 2):
            clamped = (
                orientation * 27 + state % 27
                if channel == 1
                else state // 27 * 27 + orientation * 9 + state % 9
            )
            value = table[3][table[2][clamped]] % 9
            mask = (3 << (2 * (orientation - 1))) if channel == 1 else (5 << (orientation - 1))
            masks[value] |= mask << (law * 4)
    return tuple(masks)


@lru_cache(maxsize=1024)
def common(mask: int) -> int:
    if not mask:
        return 0
    winners = decisions().winning
    selected = iter(indices(mask))
    result = winners[next(selected)]
    for index in selected:
        result &= winners[index]
        if not result:
            break
    return result


class Belief:
    def __init__(self, spec):
        self.mask = (
            (1 << len(WORLDS)) - 1 if spec.resolved is None else 1 << WORLD_INDEX[spec.resolved]
        )

    def counts(self):
        return self.mask.bit_count(), len({decisions().winning[i] for i in indices(self.mask)})

    def observe(self, measurement):
        sample = measurement.sample
        channel = sample.get("channel")
        from nexus.ontology.history.laws import READERS

        index = 0 if channel is None else READERS.index(channel)
        x, y = sample["visible"] if channel is None else sample["reading"]
        self.mask &= partitions(tuple(sample["history"]), index)[x * 3 + y]
        if not self.mask:
            raise ValueError("history observation contradicts the public prior")

    def common_decisions(self):
        return tuple(words()[i] for i in indices(common(self.mask)))

    def accepting_count(self, history):
        if history is None:
            return 0
        return (self.mask & decisions().accepting[word_index(history)]).bit_count()

    def supports(self, history):
        return (
            bool(self.mask)
            and history is not None
            and self.accepting_count(history) == self.mask.bit_count()
        )

    def exclude_target(self, history):
        if history is not None:
            self.mask &= ~decisions().accepting[word_index(history)]
