"""Independent, standard-library feasibility oracle; no NEXUS imports.

This file deliberately keeps its scalar equations independent of runtime tables.
Run with python scripts/history_oracle.py. The printed evidence is operator-only.
"""

import json
from collections import Counter, deque
from itertools import product
from time import perf_counter

LAWS = tuple(product(range(4), repeat=4))
ORIENTATIONS = tuple(product((1, 2), repeat=2))


def pulse(law, state, mode):
    h, k, x, _y = state
    inputs = (k, h, h + k, k + x)
    setting = law[mode]
    coefficient, shift = 1 + setting // 2, setting % 2
    values = list(state)
    values[mode] = (values[mode] + coefficient * (1 + (inputs[mode] + shift) ** 2)) % 3
    if mode == 2:
        values[1] = (values[1] + values[2]) % 3
    elif mode == 3:
        values[0] = (values[0] + values[3]) % 3
    return tuple(values)


def explore(law):
    paths = {(0, 0, 0, 0): ()}
    todo = deque(paths)
    while todo:
        state = todo.popleft()
        for mode in range(4):
            nxt = pulse(law, state, mode)
            if nxt not in paths:
                paths[nxt] = paths[state] + (mode,)
                todo.append(nxt)
    return paths


def observed(law, a, b, history, channel):
    state = (0, 0, 0, 0)
    for mode in history:
        state = pulse(law, state, mode)
    if channel:
        h, k, x, y = state
        state = (a if channel == 1 else h, b if channel == 2 else k, x, y)
        state = pulse(law, pulse(law, state, 2), 3)
    return state[2:]


def cover_orientations(law):
    """Find an ordinary physical path visiting every orientation's exact goal."""
    start = ((0, 0, 0, 0), 0)
    paths = {start: ()}
    todo = deque([start])
    while todo:
        state, visited = todo.popleft()
        if visited == 15:
            return paths[state, visited]
        for mode in range(4):
            nxt = pulse(law, state, mode)
            h, k, x, y = nxt
            flag = 1 << ((h - 1) * 2 + k - 1) if h and k and x == 1 and y == 2 else 0
            key = (nxt, visited | flag)
            if key not in paths:
                paths[key] = (*paths[state, visited], mode)
                todo.append(key)
    raise AssertionError("no orientation-cover path")


def limited_paths(law, modes):
    paths = {(0, 0, 0, 0): ()}
    todo = deque(paths)
    while todo:
        state = todo.popleft()
        if len(paths[state]) == 8:
            continue
        for mode in modes:
            nxt = pulse(law, state, mode)
            if nxt not in paths:
                paths[nxt] = (*paths[state], mode)
                todo.append(nxt)
    return paths


FIXED_PANEL = (
    ((1, 3, 2, 1), 1),
    ((0, 2, 1, 3), 2),
    ((2, 0, 2, 1), 1),
    ((0, 0, 2, 0), 2),
    ((1, 0, 0, 2), 1),
    ((1, 1, 0, 2), 1),
    ((0, 1, 3, 1), 1),
    ((0, 0, 1, 2), 0),
    ((0, 1), 1),
)
JOINT_QUERIES = (((0, 1, 0, 3), 2), ((0, 2, 2, 2), 0), ((0, 2, 1), 1))


def prove():
    start = perf_counter()
    results = [explore(law) for law in LAWS]
    distances = Counter()
    omitted = Counter()
    cd_only = 0
    signatures = []
    covers = Counter()
    worlds = tuple((law, a, b) for law in LAWS for a, b in ORIENTATIONS)
    for law, paths in zip(LAWS, results):
        assert len(paths) == 81
        covers[len(cover_orientations(law))] += 1
        alternatives = {
            mode: limited_paths(law, tuple(i for i in range(4) if i != mode)) for mode in range(4)
        }
        cd = limited_paths(law, (2, 3))
        for a, b in ORIENTATIONS:
            goal = (a, 2 * b % 3, 1, 2)
            distances[len(paths[goal])] += 1
            for mode, options in alternatives.items():
                omitted[mode] += goal in options
            cd_only += goal in cd
            signatures.append(tuple(observed(law, a, b, h, c) for h, c in FIXED_PANEL))
    assert len(set(signatures)) == 1024
    truth = worlds[260]
    posterior = list(range(1024))
    observations = []
    for history, channel in JOINT_QUERIES:
        for h, c in [*((history[:n], 0) for n in range(1, len(history) + 1)), (history, channel)]:
            value = observed(*truth, h, c)
            observations.append({"history": h, "channel": c, "reading": value})
            posterior = [i for i in posterior if observed(*worlds[i], h, c) == value]
    vectors = [(*worlds[i][0], *worlds[i][1:]) for i in posterior]
    modal = []
    for column in zip(*vectors):
        counts = Counter(column).most_common()
        assert len(counts) == 1 or counts[0][1] > counts[1][1]
        modal.append(counts[0][0])
    assert tuple(modal) not in vectors
    return {
        "version": "history-independent-proof-v1",
        "worlds": 1024,
        "all_normalized_states_reachable": all(len(p) == 81 for p in results),
        "goal_distances": dict(sorted(distances.items())),
        "omitted_pulse_solvable_worlds": dict(omitted),
        "tor_sen_only_solvable_worlds": cd_only,
        "finish_feedback_cover_lengths": dict(sorted(covers.items())),
        "finish_feedback_scope": "law known; orientation unknown; at most four finishes; zero intervention readers",
        "fixed_panel": FIXED_PANEL,
        "fixed_panel_behavior_classes": len(set(signatures)),
        "joint_inconsistency": {
            "queries": JOINT_QUERIES,
            "observations": observations,
            "worlds": posterior,
            "unique_marginal_modes": modal,
            "mode_vector_compatible": False,
        },
        "history_alias": {
            "law": LAWS[0],
            "histories": [[], [0]],
            "visible": [[0, 0], [0, 0]],
            "next_tor_visible": [
                observed(LAWS[0], 1, 1, (2,), 0),
                observed(LAWS[0], 1, 1, (0, 2), 0),
            ],
        },
        "deep_tier_admitted": False,
        "limitations": [
            "No mandatory adaptive-round theorem",
            "Repeatable finish bypasses intervention necessity",
            "Vek and nol are each omittable in every world",
            "Known-law physical depth is not inference depth",
        ],
        "seconds": perf_counter() - start,
    }


def main():
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = prove()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix(".tmp")
        temporary.write_text(json.dumps(result, indent=2) + "\n")
        temporary.replace(args.output)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k not in ("joint_inconsistency", "fixed_panel")},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
