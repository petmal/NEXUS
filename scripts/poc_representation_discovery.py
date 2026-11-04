"""Offline representation candidate audit, NOT a registered or admitted NEXUS family.

A query starts at (0,0,0), applies a word of trits, and returns only its final
view. Exact partition refinement covers all future words; the finite panel is
an achieved shortcut upper bound, not an optimality or cognitive-depth proof.
No runtime imports, source-bound releases, player evidence, or matrix changes.
"""

from itertools import product
from collections import Counter
import argparse
import json
from time import perf_counter

W = tuple(product(range(3), repeat=5))
W = tuple((*w, u, v) for w in W for u, v in product(range(2), repeat=2))
S = tuple(product(range(3), repeat=3))
SI = {s: i for i, s in enumerate(S)}


def step(w, s, x):
    a, b, c, d, e, u, v = w
    p, q, r = s
    return q, r, (p + a * q + b * r + c * q * r + d * q * q + e * r * r + x) % 3


def view(w, s):
    *_, u, v = w
    p, q, r = s
    return (p + u * q * r + v * r * r) % 3


start = perf_counter()
trans = [tuple(tuple(SI[step(w, s, x)] for x in range(3)) for s in S) for w in W]
obs = [tuple(view(w, s) for s in S) for w in W]
blocks = [o for row in obs for o in row]
for it in range(40):
    ids = {}
    nxt = []
    for i in range(len(W)):
        for s in range(27):
            sig = (obs[i][s], *(blocks[i * 27 + t] for t in trans[i][s]))
            nxt.append(ids.setdefault(sig, len(ids)))
    if nxt == blocks:
        break
    blocks = nxt
else:
    raise RuntimeError("behavioral partition did not converge")
reachability = []
for transitions in trans:
    reached = {0}
    pending = [0]
    while pending:
        for successor in transitions[pending.pop()]:
            if successor not in reached:
                reached.add(successor)
                pending.append(successor)
    reachability.append(len(reached))
assert set(reachability) == {27}
assert len(set(blocks[::27])) == 972
assert all(len(set(blocks[i * 27 : (i + 1) * 27])) == 27 for i in range(len(W)))
print(
    "representation:",
    len(W),
    "worlds",
    len(set(blocks[::27])),
    "mission classes",
    Counter(len(set(blocks[i * 27 : (i + 1) * 27])) for i in range(len(W))),
    "state classes;",
    it,
    "refinements",
    perf_counter() - start,
    flush=True,
)
# Prefix traversal executes each prefix once for each world.
front = [((), tuple(0 for w in W))]
qs = []
rows = []
coverage = []
for length in range(1, 7):
    new = []
    for word, states in front:
        for a in range(3):
            nxt = tuple(trans[i][s][a] for i, s in enumerate(states))
            q = word + (a,)
            rows.append(bytes(obs[i][s] for i, s in enumerate(nxt)))
            qs.append(q)
            new.append((q, nxt))
    front = new
    sigs = {tuple(row[i] for row in rows) for i in range(len(W))}
    coverage.append({"max_word_length": length, "queries": len(qs), "behavior_classes": len(sigs)})
    print(
        "length",
        length,
        "queries",
        len(qs),
        "classes",
        len(sigs),
        "sec",
        round(perf_counter() - start, 2),
        flush=True,
    )
    if len(sigs) == len(set(blocks[::27])):
        break
parts = tuple(
    tuple(sum(1 << i for i, v in enumerate(row) if v == x) for x in range(3)) for row in rows
)
mission = blocks[::27]
# Find a universal fixed panel, not a lower bound.
cells = [(1 << len(W)) - 1]
panel = []
panel_steps = []
while any(len({mission[i] for i in range(len(W)) if b >> i & 1}) > 1 for b in cells):
    costs = [sum((b & p).bit_count() ** 2 for b in cells for p in pp) for pp in parts]
    if min(costs) >= sum(b.bit_count() ** 2 for b in cells):
        raise RuntimeError("query domain cannot resolve every behavior")
    q = min(range(len(costs)), key=lambda q: (costs[q], len(qs[q]), qs[q]))
    panel.append(qs[q])
    cells = [b & p for b in cells for p in parts[q] if b & p]
    panel_steps.append(
        {
            "queries": len(panel),
            "classes": len(cells),
            "largest_class": max(b.bit_count() for b in cells),
        }
    )
    print(
        "fixed panel",
        len(panel),
        "cells",
        len(cells),
        "max",
        max(b.bit_count() for b in cells),
        flush=True,
    )
print("panel words", panel, flush=True)
print("total seconds", perf_counter() - start, flush=True)

assert len(cells) == 972 and all(b.bit_count() == 1 for b in cells)
report = {
    "status": "candidate-audited-not-runtime-qualified",
    "world_count": len(W),
    "reachable_states_per_world": 27,
    "minimal_predictive_states_per_world": 27,
    "initial_behavior_classes": len(set(blocks[::27])),
    "arithmetic": "modulo 3; initial state (0,0,0)",
    "parameters": "a,b,c,d,e in {0,1,2}; u,v in {0,1}; all 972 combinations",
    "transition": "(p,q,r) -> (q,r,p+a*q+b*r+c*q*r+d*q*q+e*r*r+input)",
    "view": "p+u*q*r+v*r*r",
    "query_contract": "start a fresh zero-state fixture; apply the input word; return one final trit only",
    "coverage": coverage,
    "fixed_panel": panel,
    "fixed_panel_steps": panel_steps,
    "hard_tier_admitted": False,
    "runtime_integrated": False,
    "scope": "Exact finite-state future-behavior equivalence and reachability; achieved ten-query fixed panel. Does not prove minimum queries/actions, model failure, an unknown representation requirement, or resistance to all shortcut policies. No finish/error channels exist in this standalone model.",
    "remaining": "Audit known-feature coefficient fitting and sufficient-state shortcuts; settle player grammar/T2 contrast and action costs; implement and audit the uncertainty candidate before runtime integration.",
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output")
args = parser.parse_args()
if args.output:
    from pathlib import Path

    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
