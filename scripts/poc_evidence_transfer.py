"""Independent finite oracle; intentionally imports no NEXUS runtime code.

Run before integration, or with --output to refresh the inspectable proof.
This establishes finite information conditions, not human/LLM cognitive depth.
"""

import argparse
import json
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from time import perf_counter


def programs():
    return tuple(
        (topology, f, g, h, changed, replacement, shift)
        for topology, f, g, h, changed, replacement, shift in product(
            range(3), range(4), range(4), range(4), range(3), range(4), range(3)
        )
        if (f, g, h)[changed] != replacement
    )


def conditions():
    return tuple(product(range(2), *([range(3)] * 5)))


def components(program, setting):
    graph, f, g, h, changed, replacement, shift = program
    context, x, y, z, a, b = setting
    operations = [f, g, h]
    if context:
        operations[changed] = replacement

    def apply(selector, u, v):
        return (u + v, u - v, u * v, u * u + v)[selector] % 3

    first = (apply(operations[0], x, y) + a) % 3
    second = (apply(operations[1], y if graph == 1 else first, z) + b) % 3
    return (apply(operations[2], second if graph == 0 else first,
                  x if graph == 0 else second) + shift) % 3, second


def scalar(program, setting):
    return components(program, setting)[0]


def reader(program, offset, setting):
    return (offset + components(program, (1 - setting[0], *setting[1:]))[1]) % 3


def closure(signatures, selected):
    groups = defaultdict(set)
    for row in signatures:
        groups[bytes(row[i] for i in selected)].add(row)
    ambiguous = {key for key, targets in groups.items() if len(targets) > 1}
    return {
        "groups": len(groups),
        "ambiguous_groups": len(ambiguous),
        "affected_worlds": sum(bytes(row[i] for i in selected) in ambiguous for row in signatures),
    }


def prove():
    start = perf_counter()
    worlds, queries = programs(), conditions()
    signatures = tuple(bytes(scalar(w, q) for q in queries) for w in worlds)
    groups = Counter(signatures)
    base_worlds, base_signatures = worlds[::3], signatures[::3]
    reference_signatures = tuple(bytes(reader(w, 0, q) for q in queries) for w in base_worlds)
    survey_signatures = tuple(bytes((f + e) % 3 for f, e in zip(row, ref))
                              for row, ref in zip(base_signatures, reference_signatures))
    survey_groups, reference_groups = defaultdict(set), defaultdict(set)
    for physical, survey, reference in zip(base_signatures, survey_signatures, reference_signatures):
        survey_groups[survey].add(physical)
        reference_groups[reference].add(physical)
    affected = [i for i, row in enumerate(survey_signatures) if len(survey_groups[row]) > 1]
    # Algebraic all-query rival: shifting physical baseline by +1 and reader
    # offset by -1 preserves EVERY survey, but changes EVERY mission response.
    for world in worlds:
        rival = (*world[:6], (world[6] + 1) % 3)
        for q in queries:
            assert scalar(rival, q) == (scalar(world, q) + 1) % 3
            assert reader(rival, 0, q) == reader(world, 0, q)
            for offset in range(3):
                shown = (scalar(world, q) + reader(world, offset, q)) % 3
                rival_shown = (scalar(rival, q) + reader(rival, (offset - 1) % 3, q)) % 3
                assert shown == rival_shown
                assert (shown - reader(world, offset, q)) % 3 == scalar(world, q)
    return {
        "schema": "evidence-transfer-independent-proof-v1",
        "physical_programs": len(worlds),
        "behavior_classes": len(groups),
        "max_equivalent_programs": max(groups.values()),
        "conditions": len(queries),
        "reader_offsets": 3,
        "joint_worlds": len(worlds) * 3,
        "survey_only_incompatible_rival_for_every_world": True,
        "reference_only_incompatible_rival_for_every_world": True,
        "matched_subtraction_recovers_physical_response": True,
        "structural_survey_closure": {
            "groups": len(survey_groups),
            "ambiguous_groups": sum(len(v) > 1 for v in survey_groups.values()),
            "affected_base_worlds": len(affected),
            "nonlinear_affected_base_worlds": sum(any(g >= 2 for g in (*base_worlds[i][1:4], base_worlds[i][5])) for i in affected),
            "by_topology": dict(Counter(base_worlds[i][0] for i in affected)),
            "by_replacement_location": dict(Counter(base_worlds[i][4] for i in affected)),
        },
        "reference_remaining_base_targets_histogram": dict(Counter(len(v) for v in reference_groups.values())),
        "passive": closure(signatures, [i for i, q in enumerate(queries) if q[4:] == (0, 0)]),
        "context_0_only": closure(signatures, [i for i, q in enumerate(queries) if q[0] == 0]),
        "context_1_only": closure(signatures, [i for i, q in enumerate(queries) if q[0] == 1]),
        "unmixed_inputs": closure(signatures, [i for i, q in enumerate(queries) if sum(v != 0 for v in q[1:4]) <= 1]),
        "guess_bounds": {
            "scope": "Uniform syntax-world prior; any adaptive sequence with at most listed ternary readings and binary finishes. Successful target leaves <= guesses*3**readings, weighted by largest behavior classes. Preparation is granted free; targeted matrix rates are not bounded by this population statement.",
            "bounds": [{"readings": readings, "guesses": guesses,
                        "correct_world_mass_upper": sum(sorted(groups.values(), reverse=True)[:guesses * 3**readings]),
                        "population": len(worlds)} for readings, guesses in ((0, 1), (0, 3), (1, 1), (2, 2), (3, 3))],
        },
        "revision_poc": {
            "integrate_required_revision": False,
            "reason": "Both contexts are accessible from the start. Early transition plus joint stationary inference is legal; a provisional inherited program does not force belief revision. Context-restricted inference loses target information, but context order is arbitrary.",
            "scope": "Negative gate for this stationary construction; no claim that all revision designs are impossible.",
        },
        "claims_excluded": ["required adaptive rounds", "cognitive depth", "model failure rate", "reference-first order is necessary"],
        "seconds": round(perf_counter() - start, 6),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = prove()
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered)
