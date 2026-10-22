"""Constructive public policy with a finite all-outcome guarantee.

The investigator chooses safe short experiments, uses their complete observable
transcript, and recomputes a continuation from the resulting *physical* belief.
There is no return to a fresh reference. Small residual beliefs may share a
supported installation word without identifying every law. This is an upper
bound witness, never an optimal-action or minimum-reasoning certificate.
"""

from collections import defaultdict
from functools import lru_cache
from itertools import product

from nexus.ontology.stateful.laws import MODES, SIZE, readout
from nexus.ontology.stateful.search import FINISH, SearchLimit, planner

WORDS = tuple(w for n in range(5) for w in product(range(4), repeat=n))


class Investigator:
    def __init__(self, target, resolved=None):
        self.game = planner(target, resolved)
        self.decisions = {}
        self.calls = 0
        self.construct = lru_cache(maxsize=20_000)(self._construct)
        self.install = lru_cache(maxsize=50_000)(self._install)

    def _install(self, belief, remaining):
        if self.game.ready(belief):
            return ()
        if self.game.lower(belief) > remaining + 1:
            return None
        for a in range(4):
            child = tuple((w, self.game.table[w][a][s]) for w, s in belief)
            if child == belief:
                continue
            suffix = self.install(child, remaining - 1)
            if suffix is not None:
                return (a, *suffix)
        return None

    def experiment(self, belief, word):
        groups = defaultdict(list)
        for w, state in belief:
            outputs = []
            for a in word:
                state = self.game.table[w][a][state]
                if self.game.distance[w][state] == SIZE:
                    return None
                outputs.append(readout(state))
            outputs.append(readout(self.game.table[w][0][state]))
            groups[tuple(outputs)].append((w, state))
        return tuple((o, tuple(c)) for o, c in sorted(groups.items()))

    def _construct(self, belief):
        self.calls += 1
        if self.calls > 20_000:
            raise SearchLimit("constructive policy cap; no guarantee established")
        if len(belief) == 1:
            w, state = belief[0]
            distances = self.game.distance[w]
            if distances[state] == SIZE:
                return None
            word = []
            while distances[state]:
                a = next(
                    a
                    for a in range(4)
                    if distances[self.game.table[w][a][state]] == distances[state] - 1
                )
                word.append(a)
                state = self.game.table[w][a][state]
            self.decisions[belief] = ("install", tuple(word))
            return len(word) + 1
        if len(belief) <= 8:
            # Search increasing horizons so the reference never pads a known
            # installation with harmless cycles just to fill an upper bound.
            for horizon in range(self.game.lower(belief) - 1, 9):
                word = self.install(belief, horizon)
                if word is not None:
                    self.decisions[belief] = ("install", word)
                    return len(word) + 1
        choices = []
        for word in WORDS:
            groups = self.experiment(belief, word)
            if groups is None:
                continue
            worst = max(len(c) for _, c in groups)
            if worst < len(belief):
                choices.append((worst, len(word), word, groups))
        for _, _, word, groups in sorted(choices):
            costs = []
            for _, child in groups:
                cost = self.construct(child)
                if cost is None:
                    break
                costs.append(cost)
            else:
                self.decisions[belief] = ("experiment", word)
                return len(word) + 1 + max(costs)
        return None

    def bound(self):
        bound = self.construct(self.game.initial)
        if bound is None:
            raise ValueError("no public policy established for complete prior")
        return bound


@lru_cache(maxsize=4)
def investigator(target, resolved=None):
    result = Investigator(target, resolved)
    result.bound()
    return result


def public_policy(player, evidence):
    import json

    from nexus.models.actions import (
        FinishAction,
        MoveAction,
        OperateAction,
        ProbeAction,
        TakeAction,
    )
    from nexus.ontology.stateful.schema import Investigation

    spec = Investigation.model_validate(json.loads(evidence["theory.json"])["specification"])

    def act(action):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"stateful public investigator failed: {result.message}")
        return result

    act(TakeAction(artifact="seal"))
    if player.observe().room != spec.mission_room:
        act(MoveAction(target=spec.mission_room))
    if spec.procedure is not None:
        for a in spec.procedure:
            act(OperateAction(machine=MODES[a], artifact="seal"))
        return act(FinishAction())
    policy = investigator(spec.target, spec.resolved)
    belief = policy.game.initial
    while True:
        kind, word = policy.decisions[belief]
        for a in (*word, FINISH if kind == "install" else 4):
            if a == FINISH:
                if not policy.game.ready(belief):
                    raise ValueError("public policy attempted an unsupported finish")
                return act(FinishAction())
            action_type = OperateAction if a < 4 else ProbeAction
            result = act(action_type(machine=MODES[a % 4], artifact="seal"))
            payload = next(
                e["details"]["result"]["payload"] for e in result.events if "result" in e["details"]
            )
            belief = dict(policy.game.branches(belief, a))[payload["reading"]]
        # Full transcript filtering is exactly the partition used in construct().
