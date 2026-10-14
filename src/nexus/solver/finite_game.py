"""Exact bounded policies for small, explicitly compiled deterministic games.

The model is a finite quotient, not an assertion that a live API has been covered.
States retain hidden-world identity whenever it affects future behavior. A batch
is a fixed word of requests; its replies may be used only at the next boundary.
All terminal states halt automatically. The final word ignores its replies.
A positive-cost request exhausting the deadline fails unless it wins immediately;
this is not a cost ceiling that allows free continuations after exhaustion.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import asdict, dataclass
from hashlib import sha256
from time import monotonic
from typing import Literal


@dataclass(frozen=True, slots=True)
class Transition:
    state: int
    observation: str
    cost: int = 1


@dataclass(frozen=True, slots=True)
class FiniteGame:
    model_id: str
    public_signature: str
    actions: tuple[str, ...]
    terminal: tuple[Literal["active", "won", "failed"], ...]
    transitions: tuple[tuple[Transition, ...], ...]
    initial: tuple[tuple[int, int], ...]  # (state, integer prior mass)

    def __post_init__(self) -> None:
        n = len(self.terminal)
        if not self.model_id or not self.public_signature or not n or not self.initial:
            raise ValueError("a finite game requires identity, public scope and initial support")
        if len(set(self.actions)) != len(self.actions) or not self.actions:
            raise ValueError("request classes must be nonempty and uniquely named")
        if len(self.transitions) != n or any(
            len(row) != len(self.actions) for row in self.transitions
        ):
            raise ValueError("transition table must cover every state/request pair")
        if any(status not in ("active", "won", "failed") for status in self.terminal):
            raise ValueError("unknown terminal value")
        for state, mass in self.initial:
            if type(state) is not int or not 0 <= state < n or type(mass) is not int or mass <= 0:
                raise ValueError("invalid initial state or prior mass")
        for row in self.transitions:
            for edge in row:
                if (
                    type(edge.state) is not int
                    or not 0 <= edge.state < n
                    or type(edge.cost) is not int
                    or edge.cost < 0
                    or not isinstance(edge.observation, str)
                ):
                    raise ValueError("invalid finite transition")

    @property
    def digest(self) -> str:
        encoded = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return sha256(encoded.encode()).hexdigest()


@dataclass(frozen=True, order=True, slots=True)
class Possibility:
    state: int
    remaining: int
    mass: int


type Belief = tuple[Possibility, ...]


def belief(entries: tuple[Possibility, ...]) -> Belief:
    """Merge only identical full continuation states, retaining probability mass."""
    groups: dict[tuple[int, int], int] = {}
    for entry in entries:
        key = entry.state, entry.remaining
        groups[key] = groups.get(key, 0) + entry.mass
    return tuple(
        Possibility(state, remaining, mass) for (state, remaining), mass in sorted(groups.items())
    )


def initial_belief(game: FiniteGame, budget: int) -> Belief:
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be a nonnegative integer")
    return belief(tuple(Possibility(state, budget, mass) for state, mass in game.initial))


@dataclass(frozen=True, slots=True)
class Program:
    """Fixed request word, optionally followed by one public-feedback branch."""

    commands: tuple[int, ...] = ()
    branches: tuple[tuple[tuple[str, ...], Program], ...] = ()


@dataclass(frozen=True, slots=True)
class Bound:
    belief: Belief
    rounds: int
    success_mass: int


@dataclass(frozen=True, slots=True)
class PolicyProof:
    game_digest: str
    budget: int
    rounds: int
    success_mass: int
    total_mass: int
    bounds: tuple[Bound, ...]
    witness: Program
    scope: Literal["compiled-finite-model"] = "compiled-finite-model"


@dataclass(frozen=True, slots=True)
class Analysis:
    status: Literal["exact", "unknown"]
    proof: PolicyProof | None
    states_visited: int
    seconds: float
    reason: str = ""


@dataclass(slots=True)
class SearchBudget:
    max_states: int = 100_000
    max_seconds: float = 30.0
    visited: int = 0
    started: float = 0.0

    def start(self) -> None:
        if self.max_states < 1 or self.max_seconds <= 0:
            raise ValueError("analysis limits must be positive")
        self.visited = 0
        self.started = monotonic()

    def poll(self) -> None:
        """Check elapsed work even when every successor was already seen."""
        if monotonic() - self.started > self.max_seconds:
            raise SearchLimit("finite policy search exceeded its declared time limit")

    def tick(self) -> None:
        self.visited += 1
        self.poll()
        if self.visited > self.max_states:
            raise SearchLimit("finite policy search exceeded its declared state/time limit")


class SearchLimit(RuntimeError):
    """An incomplete proof is unknown, never an impossibility certificate."""


@dataclass(frozen=True, slots=True)
class WordState:
    groups: tuple[Belief, ...]
    won_mass: int


def word_start(game: FiniteGame, possibilities: Belief) -> WordState:
    active = tuple(p for p in possibilities if game.terminal[p.state] == "active")
    won = sum(p.mass for p in possibilities if game.terminal[p.state] == "won")
    return WordState((active,) if active else (), won)


def advance(game: FiniteGame, current: WordState, command: int) -> WordState:
    """Apply one common request without choosing it from intermediate replies."""
    groups: list[Belief] = []
    won = current.won_mass
    for previous in current.groups:
        replies: dict[str, list[Possibility]] = {}
        for p in previous:
            edge = game.transitions[p.state][command]
            if edge.cost > p.remaining:
                continue
            remaining = p.remaining - edge.cost
            status = game.terminal[edge.state]
            if status == "won":
                won += p.mass
            elif status == "active" and (remaining > 0 or edge.cost == 0):
                replies.setdefault(edge.observation, []).append(
                    Possibility(edge.state, remaining, p.mass)
                )
        groups.extend(belief(tuple(entries)) for entries in replies.values())
    return WordState(tuple(sorted(groups)), won)


def reachable_words(game: FiniteGame, start: Belief, limits: SearchBudget):
    """Finite closure includes informative zero-cost responses and their cycles.

    The key includes full continuation states, remaining budgets and the entire
    observation partition. Repeating it adds no information or physical ability.
    Paths with different literal replies but identical partitions are isomorphic
    only within this already compiled model; live normalization needs its own proof.
    """
    first = word_start(game, start)
    limits.tick()
    queue: deque[tuple[WordState, tuple[int, ...]]] = deque([(first, ())])
    seen = {first}
    while queue:
        current, word = queue.popleft()
        yield current, word
        if not current.groups:
            continue
        for command in range(len(game.actions)):
            limits.poll()
            after = advance(game, current, command)
            if after not in seen:
                limits.tick()
                seen.add(after)
                queue.append((after, (*word, command)))


def observations_after(game: FiniteGame, start: Belief, word: tuple[int, ...]):
    groups: dict[tuple[str, ...], list[Possibility]] = {}
    won = 0
    for p in start:
        state, remaining = p.state, p.remaining
        replies: list[str] = []
        for command in word:
            if game.terminal[state] != "active":
                break
            edge = game.transitions[state][command]
            if edge.cost > remaining:
                remaining = -1
                break
            remaining -= edge.cost
            state = edge.state
            replies.append(edge.observation)
            if remaining == 0 and edge.cost > 0 and game.terminal[state] == "active":
                remaining = -1
                break
        if remaining >= 0 and game.terminal[state] == "won":
            won += p.mass
        elif remaining >= 0 and game.terminal[state] == "active":
            groups.setdefault(tuple(replies), []).append(Possibility(state, remaining, p.mass))
    return won, tuple(
        (signature, belief(tuple(entries))) for signature, entries in sorted(groups.items())
    )


def analyze(
    game: FiniteGame, *, budget: int, rounds: int, limits: SearchBudget | None = None
) -> Analysis:
    if type(rounds) is not int or rounds < 0:
        raise ValueError("feedback rounds must be a nonnegative integer")
    root = initial_belief(game, budget)
    limits = limits or SearchBudget()
    limits.start()
    values: dict[tuple[Belief, int], tuple[int, Program]] = {}

    def solve(start: Belief, remaining_rounds: int) -> tuple[int, Program]:
        key = start, remaining_rounds
        if key in values:
            return values[key]
        total = sum(p.mass for p in start)
        best = 0
        witness = Program()
        for current, word in reachable_words(game, start, limits):
            score = current.won_mass
            if word and remaining_rounds and current.groups:
                score += sum(solve(group, remaining_rounds - 1)[0] for group in current.groups)
            if score > best:
                best = score
                branches = ()
                if word and remaining_rounds and current.groups:
                    _, groups = observations_after(game, start, word)
                    branches = tuple(
                        (signature, solve(group, remaining_rounds - 1)[1])
                        for signature, group in groups
                    )
                witness = Program(word, branches)
            if best == total:
                break  # A concrete perfect policy meets the universal mass upper bound.
        values[key] = best, witness
        return values[key]

    try:
        mass, policy = solve(root, rounds)
        limits.poll()
    except (SearchLimit, RecursionError) as exc:
        return Analysis("unknown", None, limits.visited, monotonic() - limits.started, str(exc))
    proof = PolicyProof(
        game.digest,
        budget,
        rounds,
        mass,
        sum(p.mass for p in root),
        tuple(Bound(b, r, v) for (b, r), (v, _) in values.items()),
        policy,
    )
    try:
        limits.poll()
    except SearchLimit as exc:
        return Analysis("unknown", None, limits.visited, monotonic() - limits.started, str(exc))
    return Analysis("exact", proof, limits.visited, monotonic() - limits.started)
