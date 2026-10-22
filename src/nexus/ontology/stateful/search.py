"""Finite joint-law/state planning. All counted actions cost one, including finish.

Actions 0..3 commit; 4..7 are ordinary counterfactual probes; 8 is finish.
A belief has exactly one current state per surviving law. Failed finish filters
the goal subset; success branches terminate. No selected truth enters strong().
Search exhaustion raises: it never becomes a negative certificate.
"""

from collections import defaultdict
from functools import lru_cache
from heapq import heappop, heappush

from nexus.ontology.stateful.laws import (
    SIZE,
    WORLD_INDEX,
    distances,
    encode,
    joint_tables,
    readout,
    tables,
)

FINISH = 8
CAP = 250_000


class SearchLimit(RuntimeError):
    pass


class Planner:
    def __init__(self, target, resolved=None):
        self.target = encode(target)
        self.table = tables()
        self.distance = distances(target)
        self.initial = tuple(
            (w, 0) for w in range(len(self.table)) if resolved is None or w == WORLD_INDEX[resolved]
        )
        self.policy = {}
        self.nodes = 0
        # Per-instance bounded caches: callers retain at most a handful of planners.
        self.branches = lru_cache(maxsize=100_000)(self._branches)
        self.strong = lru_cache(maxsize=CAP)(self._strong)

    def ready(self, belief):
        return bool(belief) and all(s == self.target for _, s in belief)

    def lower(self, belief):
        return max((self.distance[w][s] + 1 for w, s in belief), default=0)

    def _branches(self, belief, action):
        if action == FINISH:
            failed = tuple((w, s) for w, s in belief if s != self.target)
            return ((False, failed),) if failed else ()
        groups = defaultdict(list)
        for w, s in belief:
            after = self.table[w][action % 4][s]
            groups[readout(after)].append((w, after if action < 4 else s))
        return tuple((o, tuple(c)) for o, c in sorted(groups.items()))

    def _strong(self, belief, horizon):
        self.nodes += 1
        if self.nodes > CAP:
            raise SearchLimit("strong policy search cap; result unknown")
        if not belief:
            return True
        if self.lower(belief) > horizon:
            return False
        if self.ready(belief):
            self.policy[belief, horizon] = FINISH
            return True
        choices = []
        for a in range(9):
            children = tuple(c for _, c in self.branches(belief, a))
            if belief in children or any(self.lower(c) > horizon - 1 for c in children):
                continue
            choices.append((max(map(len, children), default=0), a, children))
        for _, a, children in sorted(choices):
            if all(self.strong(c, horizon - 1) for c in sorted(children, key=len, reverse=True)):
                self.policy[belief, horizon] = a
                return True
        return False

    def optimum(self, cap=20):
        for h in range(self.lower(self.initial), cap + 1):
            if self.strong(self.initial, h):
                return h
        raise SearchLimit(f"no strong policy established within {cap} actions")

    def actual_child(self, belief, action, world):
        return next(
            (c for _, c in self.branches(belief, action) if any(w == world for w, _ in c)), ()
        )

    def supported_minimum(self, world, *, free_initial_panel=False):
        return self.supported_trace(world, free_initial_panel=free_initial_panel)[0]

    def supported_trace(
        self, world, *, free_initial_panel=False, safe=False, operations_only=False
    ):
        """Optimistic exact minimum: even unsafe off-trajectory branches are allowed.

        Finish must be entailed BEFORE success. Lucky mixed-belief success is not
        evidence support. A* uses the actual-law physical distance only as a lower
        bound; the search may not choose a law-specific unobserved state directly.
        """
        start = self.initial
        if free_initial_panel:
            for a in range(4, 8):
                start = self.actual_child(start, a, world)
        queue = [(0, 0, start)]
        best = {start: 0}
        parent = {}
        while queue:
            _, cost, belief = heappop(queue)
            if best[belief] != cost:
                continue
            if self.ready(belief):
                path = [FINISH]
                while belief in parent:
                    belief, action = parent[belief]
                    path.append(action)
                return cost + (not operations_only), tuple(reversed(path))
            if len(best) > CAP:
                raise SearchLimit("supported trajectory search cap; result unknown")
            current = next(s for w, s in belief if w == world)
            for a in range(9):
                if a == FINISH and current == self.target:
                    continue
                if (
                    safe
                    and a < 4
                    and any(self.lower(c) > SIZE for _, c in self.branches(belief, a))
                ):
                    continue
                child = self.actual_child(belief, a, world)
                if not child:
                    continue
                actual = next(s for w, s in child if w == world)
                lower = self.distance[world][actual]
                increment = int(not operations_only or a < 4)
                if lower == SIZE or cost + increment >= best.get(child, CAP):
                    continue
                best[child] = cost + increment
                parent[child] = (belief, a)
                heappush(
                    queue,
                    (cost + increment + lower + (not operations_only), cost + increment, child),
                )
        raise ValueError("no evidence-supported trajectory exists")

    def initial_panel(self):
        beliefs = (self.initial,)
        for a in range(4, 8):
            beliefs = tuple(c for b in beliefs for _, c in self.branches(b, a))
        return beliefs

    def blind_possible(self, belief, horizon, *, max_nodes=CAP):
        """Exact bounded observation-blind policy, with success-aware failed finishes.

        Free initial panel may be supplied by caller. Subsequent readouts are
        ignored, but successful finish removes completed worlds. This strictly
        dominates one final blind guess and includes synchronized/reset words.
        """
        nodes = 0
        kernel = joint_tables()
        dists = tuple(d for world in self.distance for d in world)
        goal = self.target

        @lru_cache(maxsize=max_nodes)
        def search(b, h):
            nonlocal nodes
            nodes += 1
            if nodes > max_nodes:
                raise SearchLimit("blind suffix search cap; result unknown")
            if not b:
                return True
            if max(dists[v] for v in b) >= h:
                return False
            if all(v % SIZE == goal for v in b):
                return True
            choices = []
            for a in (*range(4), FINISH):
                child = (
                    tuple(v for v in b if v % SIZE != goal)
                    if a == FINISH
                    else tuple(kernel[a][v] for v in b)
                )
                if child == b:
                    continue
                ds = [dists[v] for v in child]
                if max(ds, default=-1) >= h - 1:
                    continue
                choices.append((len(child), max(ds, default=-1), sum(ds), a, child))
            for _, _, _, a, child in sorted(choices):
                if search(child, h - 1):
                    return True
            return False

        try:
            return search(tuple(w * SIZE + s for w, s in belief), horizon)
        finally:
            search.cache_clear()


@lru_cache(maxsize=4)
def planner(target, resolved=None):
    return Planner(target, resolved)
