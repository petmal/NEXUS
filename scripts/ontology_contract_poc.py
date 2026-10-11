"""Independent exhaustive proof for the categorical ontology extension contract."""

from __future__ import annotations

import json
from itertools import permutations, product


def prove(depth: int) -> dict[str, int | bool]:
    laws = tuple(permutations(range(3)))
    worlds = tuple(product(laws, repeat=depth))

    def prefix(world, stop, symbol):
        for law in world[:stop]:
            symbol = law[symbol]
        return symbol

    def observe(world, stage, symbol, tuning):
        if stage and tuning != prefix(world, stage, symbol):
            return None
        return world[stage][symbol]

    targets = {tuple(prefix(w, depth, x) for x in range(3)) for w in worlds}
    assert len(targets) == 6
    for world in worlds:
        learned = []
        evidence = []
        for stage in range(depth):
            readings = []
            for symbol in (0, 1):
                tuning = prefix(learned, stage, symbol)
                value = observe(world, stage, symbol, tuning)
                assert value is not None
                readings.append(value)
                evidence.append((stage, symbol, tuning, value))
            candidates = [p for p in laws if p[:2] == tuple(readings)]
            assert len(candidates) == 1
            learned.append(candidates[0])
        compatible = [w for w in worlds if all(observe(w, s, x, z) == v for s, x, z, v in evidence)]
        assert len(compatible) == 1
        assert tuple(prefix(learned, depth, x) for x in range(3)) == tuple(prefix(world, depth, x) for x in range(3))
        # Every undiscovered relation can change the mission, even with all others fixed.
        for stage in range(depth):
            alternatives = {tuple(prefix(world[:stage] + (p,) + world[stage+1:], depth, x) for x in range(3)) for p in laws}
            assert len(alternatives) == 6
        # Later tuning depends on upstream composition and misses still exclude worlds.
        for stage in range(1, depth):
            z = (prefix(world, stage, 0) + 1) % 3
            assert observe(world, stage, 0, z) is None
            assert 0 < sum(observe(w, stage, 0, z) is None for w in worlds) < len(worlds)
    return {"depth": depth, "worlds": len(worlds), "target_classes": len(targets),
            "reference_measurement_bound": 2*depth, "all_worlds_identified": True,
            "every_factor_affects_target": True, "no_signal_is_informative": True,
            "claims_exact_global_minimum": False}


if __name__ == "__main__":
    print(json.dumps({"proof": [prove(2), prove(3)]}, indent=2))
