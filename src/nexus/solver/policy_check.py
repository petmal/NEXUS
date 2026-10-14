"""Small independent checker for finite-game policy proof payloads.

The checker re-executes words directly from transition data. It does not trust
the solver's closure, claimed coverage, chosen policy or search-completion flag.
The finite transition table is its explicit trusted model boundary.
"""

from collections import deque

from nexus.solver.finite_game import (
    Belief,
    FiniteGame,
    PolicyProof,
    Possibility,
    Program,
    SearchBudget,
)


class InvalidProof(ValueError):
    pass


def _run(
    game: FiniteGame, start: Belief, commands: tuple[int, ...], limits: SearchBudget | None = None
):
    outcomes: dict[tuple[str, ...], dict[tuple[int, int], int]] = {}
    won = 0
    for entry in start:
        if limits:
            limits.poll()
        state, left = entry.state, entry.remaining
        signature: list[str] = []
        stopped = False
        for command in commands:
            if limits:
                limits.poll()
            if game.terminal[state] != "active":
                break
            edge = game.transitions[state][command]
            if left < edge.cost:
                stopped = True
                break
            left -= edge.cost
            state = edge.state
            signature.append(edge.observation)
            if left == 0 and edge.cost > 0 and game.terminal[state] == "active":
                stopped = True
                break
        if stopped or game.terminal[state] == "failed":
            continue
        if game.terminal[state] == "won":
            won += entry.mass
        else:
            group = outcomes.setdefault(tuple(signature), {})
            key = state, left
            group[key] = group.get(key, 0) + entry.mass
    groups = tuple(
        (signature, tuple(Possibility(s, b, w) for (s, b), w in sorted(states.items())))
        for signature, states in sorted(outcomes.items())
    )
    return won, groups


def replay_program(
    game: FiniteGame,
    start: Belief,
    program: Program,
    rounds: int,
    *,
    limits: SearchBudget | None = None,
) -> int:
    pending = [(start, program, rounds)]
    success = 0
    while pending:
        current, policy, left = pending.pop()
        if limits:
            limits.poll()
        if any(type(c) is not int or not 0 <= c < len(game.actions) for c in policy.commands):
            raise InvalidProof("policy contains an uncovered request class")
        won, groups = _run(game, current, policy.commands, limits)
        success += won
        if not policy.branches:
            continue
        if left <= 0 or not policy.commands:
            raise InvalidProof(
                "policy exceeds its feedback-round bound or branches without a batch"
            )
        children = dict(policy.branches)
        if len(children) != len(policy.branches) or set(children) != {s for s, _ in groups}:
            raise InvalidProof("policy response branches do not exactly cover public continuations")
        pending.extend((group, children[s], left - 1) for s, group in groups)
    return success


def check_proof(
    game: FiniteGame, proof: PolicyProof, *, limits: SearchBudget | None = None
) -> None:
    """Verify a matching upper bound and executable lower bound, or raise.

    SearchLimit is deliberately distinct from InvalidProof. Exhausting checker
    resources never yields a successful qualification result.
    """
    limits = limits or SearchBudget()
    limits.start()
    if proof.scope != "compiled-finite-model" or proof.game_digest != game.digest:
        raise InvalidProof("proof identity or trusted-model scope mismatch")
    if (
        type(proof.budget) is not int
        or proof.budget < 0
        or type(proof.rounds) is not int
        or proof.rounds < 0
    ):
        raise InvalidProof("invalid proof budget or round count")
    combined: dict[int, int] = {}
    for state, mass in game.initial:
        combined[state] = combined.get(state, 0) + mass
    root = tuple(Possibility(s, proof.budget, w) for s, w in sorted(combined.items()))
    total = sum(combined.values())
    if type(proof.total_mass) is not int or proof.total_mass != total:
        raise InvalidProof("proof discarded or changed prior probability mass")
    values = {}
    for bound in proof.bounds:
        limits.poll()
        if type(bound.rounds) is not int or not 0 <= bound.rounds <= proof.rounds:
            raise InvalidProof("invalid bound round count")
        if not bound.belief or tuple(sorted(bound.belief)) != bound.belief:
            raise InvalidProof("bound belief is not canonical")
        if len({(p.state, p.remaining) for p in bound.belief}) != len(bound.belief):
            raise InvalidProof("bound duplicates an equivalent continuation state")
        for p in bound.belief:
            if (
                type(p.state) is not int
                or not 0 <= p.state < len(game.terminal)
                or type(p.remaining) is not int
                or not 0 <= p.remaining <= proof.budget
                or type(p.mass) is not int
                or p.mass <= 0
            ):
                raise InvalidProof("invalid bound possibility")
        mass = sum(p.mass for p in bound.belief)
        if type(bound.success_mass) is not int or not 0 <= bound.success_mass <= mass:
            raise InvalidProof("invalid success upper bound")
        key = bound.belief, bound.rounds
        if key in values:
            raise InvalidProof("duplicate bound payload")
        values[key] = bound.success_mass
    if (
        type(proof.success_mass) is not int
        or values.get((root, proof.rounds)) != proof.success_mass
    ):
        raise InvalidProof("root claim is absent or inconsistent")
    if replay_program(game, root, proof.witness, proof.rounds, limits=limits) != proof.success_mass:
        raise InvalidProof("witness does not attain the claimed success")

    for (start, rounds), upper in values.items():
        limits.poll()
        if upper == sum(p.mass for p in start):
            continue  # Universal probability <= 1; root attainment is checked separately.
        first = _run(game, start, (), limits)
        queue: deque[tuple[tuple[int, ...], tuple]] = deque([((), first)])
        seen = {(first[0], tuple(sorted(group for _, group in first[1])))}
        limits.tick()
        while queue:
            commands, (won, groups) = queue.popleft()
            attainable_upper = won
            if commands and rounds:
                for _, group in groups:
                    child = group, rounds - 1
                    if child not in values:
                        raise InvalidProof(
                            "missing continuation bound: action coverage is incomplete"
                        )
                    attainable_upper += values[child]
            if attainable_upper > upper:
                raise InvalidProof("success bound fails an admitted request-word inequality")
            if groups:
                for action in range(len(game.actions)):
                    limits.poll()
                    word = (*commands, action)
                    after = _run(game, start, word, limits)
                    key = after[0], tuple(sorted(group for _, group in after[1]))
                    if key not in seen:
                        limits.tick()
                        seen.add(key)
                        queue.append((word, after))
    limits.poll()
