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

if not __debug__:
    raise RuntimeError("evidence-transfer PoC requires Python assertions")


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
    return (
        apply(operations[2], second if graph == 0 else first, x if graph == 0 else second) + shift
    ) % 3, second


def scalar(program, setting):
    return components(program, setting)[0]


def reader(program, offset, setting):
    return (offset + components(program, (1 - setting[0], *setting[1:]))[1]) % 3


def closure(signatures, selected, target_signatures=None):
    groups = defaultdict(set)
    for j, row in enumerate(signatures):
        groups[bytes(row[i] for i in selected)].add(
            row if target_signatures is None else target_signatures[j]
        )
    ambiguous = {key for key, targets in groups.items() if len(targets) > 1}
    return {
        "groups": len(groups),
        "ambiguous_groups": len(ambiguous),
        "affected_worlds": sum(bytes(row[i] for i in selected) in ambiguous for row in signatures),
    }


def revision_gate(worlds, signatures):
    """Truthful inherited pre-change program, followed by one module replacement.

    Triggering the change immediately leaves the same nine-candidate stationary
    problem. Enumerate every inherited notebook, condition on its actual public
    information, and construct an after-trigger-only witness. This is a failed
    gate for THIS candidate, not a theorem about all revision environments.
    """
    notebooks = defaultdict(list)
    for i, world in enumerate(worlds):
        notebooks[(*world[:4], world[-1])].append(i)
    queries = conditions()
    old_queries = tuple(i for i, q in enumerate(queries) if q[0] == 0)
    new_queries = tuple(i for i, q in enumerate(queries) if q[0] == 1)

    def bound(candidates):
        if len({signatures[i] for i in candidates}) == 1:
            return 0
        query = min(
            new_queries,
            key=lambda q: (max(Counter(signatures[i][q] for i in candidates).values()), q),
        )
        branches = [[i for i in candidates if signatures[i][query] == v] for v in range(3)]
        assert not any(len(b) == len(candidates) for b in branches)
        return 1 + max(bound(b) for b in branches if b)

    bounds, target_counts = [], []
    for candidates in notebooks.values():
        assert len(candidates) == 9
        assert all(len({signatures[i][q] for i in candidates}) == 1 for q in old_queries)
        bounds.append(bound(candidates))
        target_counts.append(len({signatures[i] for i in candidates}))
    return {
        "integrate_required_revision": False,
        "candidate": "Truthful inherited pre-change topology, primitives and q; one different primitive replacement after a player-triggered transition.",
        "inherited_notebooks_checked": len(notebooks),
        "conditioned_worlds_per_notebook": 9,
        "remaining_target_range": [min(target_counts), max(target_counts)],
        "early_transition_then_stationary_reading_upper": max(bounds),
        "old_context_measurements_in_witness": 0,
        "reason": "Every conditioned notebook has an after-trigger-only winning witness. Trigger-first leaves exactly the stationary posterior; no mistaken initial commitment, prior investigation or actual belief revision is required.",
        "scope": "Negative gate for this candidate, no claim that all revision designs are impossible. A merely provisional unsupported note cannot be treated as truthful evidence.",
    }


def prove():
    start = perf_counter()
    worlds, queries = programs(), conditions()
    signatures = tuple(bytes(scalar(w, q) for q in queries) for w in worlds)
    groups = Counter(signatures)
    base_worlds, base_signatures = worlds[::3], signatures[::3]
    reference_signatures = tuple(bytes(reader(w, 0, q) for q in queries) for w in base_worlds)
    survey_signatures = tuple(
        bytes((f + e) % 3 for f, e in zip(row, ref))
        for row, ref in zip(base_signatures, reference_signatures)
    )
    survey_groups, reference_groups = defaultdict(set), defaultdict(set)
    for physical, survey, reference in zip(
        base_signatures, survey_signatures, reference_signatures
    ):
        survey_groups[survey].add(physical)
        reference_groups[reference].add(physical)
    affected = [i for i, row in enumerate(survey_signatures) if len(survey_groups[row]) > 1]
    # Paired displays are invertibly (F,E). The zero reference identifies r.
    paired = tuple(
        bytes(v for pair in zip(row, reference_signatures[i // 3]) for v in pair)
        for i, row in enumerate(signatures)
    )
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
            "nonlinear_affected_base_worlds": sum(
                any(g >= 2 for g in (*base_worlds[i][1:4], base_worlds[i][5])) for i in affected
            ),
            "by_topology": dict(Counter(base_worlds[i][0] for i in affected)),
            "by_replacement_location": dict(Counter(base_worlds[i][4] for i in affected)),
        },
        "reference_remaining_base_targets_histogram": dict(
            Counter(len(v) for v in reference_groups.values())
        ),
        "passive": closure(signatures, [i for i, q in enumerate(queries) if q[4:] == (0, 0)]),
        "coupled_paired_passive": closure(
            paired,
            [
                2 * i + channel
                for i, q in enumerate(queries)
                if q[4:] == (0, 0)
                for channel in range(2)
            ],
            signatures,
        ),
        "coupled_paired_context_0": closure(
            paired,
            [2 * i + channel for i, q in enumerate(queries) if q[0] == 0 for channel in range(2)],
            signatures,
        ),
        "coupled_paired_context_1": closure(
            paired,
            [2 * i + channel for i, q in enumerate(queries) if q[0] == 1 for channel in range(2)],
            signatures,
        ),
        "context_0_only": closure(signatures, [i for i, q in enumerate(queries) if q[0] == 0]),
        "context_1_only": closure(signatures, [i for i, q in enumerate(queries) if q[0] == 1]),
        "unmixed_inputs": closure(
            signatures, [i for i, q in enumerate(queries) if sum(v != 0 for v in q[1:4]) <= 1]
        ),
        "guess_bounds": {
            "scope": "Uniform syntax-world prior; any adaptive sequence with at most listed ternary readings and binary finishes. Successful target leaves <= guesses*3**readings, weighted by largest behavior classes. Preparation is granted free; targeted matrix rates are not bounded by this population statement.",
            "bounds": [
                {
                    "readings": readings,
                    "guesses": guesses,
                    "correct_world_mass_upper": sum(
                        sorted(groups.values(), reverse=True)[: guesses * 3**readings]
                    ),
                    "population": len(worlds),
                }
                for readings, guesses in ((0, 1), (0, 3), (1, 1), (2, 2), (3, 3))
            ],
        },
        "revision_poc": revision_gate(worlds, signatures),
        "claims_excluded": [
            "required adaptive rounds",
            "cognitive depth",
            "model failure rate",
            "reference-first order is necessary",
        ],
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
