"""Local modular shears in a feedback loop; only register zero is observable."""

from collections import deque
from functools import lru_cache
from itertools import product

from nexus.ontology.stateful.schema import Truth

MODES = ("vek", "sul", "pax", "nir")
STATES = tuple(product(range(5), repeat=4))
DEAD = 625
SIZE = 626
WORLDS = tuple(Truth(gains=p[:4], powers=p[4:]) for p in product((1, 2), repeat=8))
WORLD_INDEX = {w: i for i, w in enumerate(WORLDS)}


def encode(v):
    return ((v[0] * 5 + v[1]) * 5 + v[2]) * 5 + v[3]


def step(world, state, mode):
    if state == DEAD:
        return DEAD
    v = list(STATES[state])
    i, j = mode, (mode + 1) % 4
    v[i] = (v[i] + world.gains[i] * (1 + v[j] ** world.powers[i])) % 5
    return DEAD if v == [4, 4, 4, 4] else encode(v)


def readout(state):
    if state == DEAD:
        return 5
    return STATES[state][0]


@lru_cache(maxsize=1)
def tables():
    # Tuples are immutable and share small ints. No cache mutation is exposed.
    return tuple(tuple(tuple(step(w, s, a) for s in range(SIZE)) for a in range(4)) for w in WORLDS)


@lru_cache(maxsize=1)
def joint_tables():
    """Intern packed law/state IDs for the large blind-word audit cache."""
    ids = tuple(range(len(WORLDS) * SIZE))
    compiled = tables()
    return tuple(
        tuple(ids[w * SIZE + compiled[w][a][s]] for w in range(len(WORLDS)) for s in range(SIZE))
        for a in range(4)
    )


@lru_cache(maxsize=2048)
def history_states(history):
    # Iterative, so R0 is not accidentally constrained by Python recursion depth.
    values = [0] * len(WORLDS)
    compiled = tables()
    for a in history:
        values = [compiled[w][a][s] for w, s in enumerate(values)]
    return tuple(values)


@lru_cache(maxsize=8)
def distances(target):
    goal = encode(target)
    result = []
    for world in tables():
        incoming = [[] for _ in range(SIZE)]
        for mode in world:
            for before, after in enumerate(mode):
                incoming[after].append(before)
        d = [SIZE] * SIZE
        d[goal] = 0
        queue = deque([goal])
        while queue:
            after = queue.popleft()
            for before in incoming[after]:
                if d[before] > d[after] + 1:
                    d[before] = d[after] + 1
                    queue.append(before)
        result.append(tuple(d))
    return tuple(result)


def shortest(world, target, state=0):
    w = WORLD_INDEX[world]
    d = distances(target)[w]
    if d[state] == SIZE:
        raise ValueError("target is unreachable from current state")
    word = []
    while d[state]:
        a = next(a for a in range(4) if d[tables()[w][a][state]] == d[state] - 1)
        word.append(a)
        state = tables()[w][a][state]
    return tuple(word)
