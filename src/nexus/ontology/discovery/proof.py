"""Offline independent scalar oracles, complete acceptance and shortcut audits.

Runtime/generation never imports this module. Proof searches are bounded and
raise on an incomplete claim. Timings belong to preflight, not stable proof data.
"""

from collections import Counter
from functools import cache
from itertools import combinations, product
from math import factorial

from nexus.ontology.inference import Measurement


def representation_oracle(program, old, pulse):
    values = [pulse, *old]
    wiring = [0, program[0], program[1]]
    new = []
    for i in range(3):
        value = values[wiring[i]]
        if program[i + 5] == 2:
            value += value
        if program[i + 2] == 1:
            value += old[i]
        new.append(value % 3)
    return tuple(new)


def representation_view(program, state):
    if program[-1] == 0:
        return state[-1]
    return (state[0] + sum(state[1] for _ in range(state[2]))) % 3


@cache
def representation_proof():
    from nexus.ontology.representation import laws as law
    from nexus.ontology.representation.inference import Belief

    states = tuple(product(range(3), repeat=3))
    indices = {s: i for i, s in enumerate(states)}
    programs = tuple(
        product(range(2), range(3), range(2), range(2), range(2), (1, 2), (1, 2), (1, 2), range(2))
    )
    if programs != law.PROGRAMS:
        raise ValueError("representation prior changed without proof review")
    transitions = []
    views = []
    for p in programs:
        transition = []
        for s in states:
            row = []
            for x in range(3):
                nxt = representation_oracle(p, s, x)
                if nxt != law.advance(p, s, x) or representation_view(p, s) != law.display(p, s):
                    raise ValueError("representation scalar conformance failed")
                row.append(indices[nxt])
            transition.append(tuple(row))
        transitions.append(tuple(transition))
        views.append(tuple(representation_view(p, s) for s in states))
    blocks = [v for row in views for v in row]
    for iteration in range(768 * 27):
        ids = {}
        new = []
        for i in range(768):
            for s in range(27):
                signature = (views[i][s], *(blocks[27 * i + t] for t in transitions[i][s]))
                new.append(ids.setdefault(signature, len(ids)))
        if new == blocks:
            break
        blocks = new
    else:
        raise ValueError("finite automaton partition did not converge")
    classes = tuple(blocks[::27])
    predictive = []
    reachable = []
    for i in range(768):
        seen = {0}
        pending = [0]
        while pending:
            for t in transitions[i][pending.pop()]:
                if t not in seen:
                    seen.add(t)
                    pending.append(t)
        reachable.append(len(seen))
        predictive.append(len({blocks[27 * i + s] for s in seen}))
    table, rows, parts = law.tables()
    # Equality of complete behavior is an independently proven relation, not
    # inferred merely from matching a bounded set of reader queries.
    expected_accepting = tuple(
        sum(1 << j for j, c in enumerate(classes) if c == classes[i]) for i in range(768)
    )
    if table.accepting != expected_accepting:
        raise ValueError("finite reader signatures do not equal complete behavior")
    representatives = {}
    for i, c in enumerate(classes):
        representatives.setdefault(c, i)
    for i in representatives.values():
        for j in representatives.values():
            if law.equivalent(programs[i], programs[j]) != (classes[i] == classes[j]):
                raise ValueError("product automaton acceptance failed")
    lengths = {}
    for n in range(1, 7):
        qs = tuple(q for q, word in enumerate(law.QUERIES) if len(word) <= n)
        lengths[str(n)] = len({bytes(row[q] for q in qs) for row in rows})
    counts = {2: Counter(), 3: Counter()}
    for theory in (2, 3):
        for p in programs:
            posterior = Belief(law.specification(law.Truth(program=p), theory, 4))
            count = 0
            while (q := posterior.choose_query()) is not None:
                posterior.observe(Measurement("reader", {"query": q, "values": law.read(p, q)}))
                count += 1
                if count > 6:
                    raise ValueError("reference policy exceeded six-reading bound")
            if not posterior.supports(p):
                raise ValueError("reference posterior lost the true behavior")
            counts[theory][count] += 1
    cells = [(1 << 768) - 1]
    panel = []
    while any(not any(cell & ~win == 0 for win in set(table.accepting)) for cell in cells):
        scores = [
            sum((cell & part).bit_count() ** 2 for cell in cells for part in pp) for pp in parts
        ]
        q = min(range(len(scores)), key=lambda q: (scores[q], len(law.QUERIES[q]), law.QUERIES[q]))
        if scores[q] >= sum(cell.bit_count() ** 2 for cell in cells):
            raise ValueError("fixed panel search stalled")
        panel.append(law.QUERIES[q])
        cells = [cell & part for cell in cells for part in parts[q] if cell & part]
    return {
        "programs": 768,
        "behavior_classes": len(set(classes)),
        "predictive_state_counts": dict(sorted(Counter(predictive).items())),
        "predictive_states_by_program": predictive,
        "reachable_states_by_program": reachable,
        "classes_by_program": classes,
        "query_length_closure_classes": lengths,
        "public_policy_readings": dict(sorted(counts[3].items())),
        "t2_public_policy_readings": dict(sorted(counts[2].items())),
        "fixed_panel": panel,
        "fixed_panel_optimality_proven": False,
        "best_uninformed_build_mass": max(m.bit_count() for m in table.accepting),
        "prior_mass": 768,
        "all_science_can_precede_construction": True,
        "deep_tier_admitted": False,
    }


def uncertainty_oracle(model, build):
    a, b = model.checks
    c, d = model.syndrome
    mask, offset, pattern = build
    relation = mask | 16
    relations = {a: c, b: d, a ^ b: c ^ d}
    selected_odd = bool(mask & 10)
    return relations.get(relation) == offset and (pattern == model.pattern or not selected_odd)


@cache
def uncertainty_proof():
    from nexus.ontology.uncertainty import laws as law
    from nexus.ontology.uncertainty.inference import Belief

    table, exposures = law.tables()
    all_models = (1 << len(law.MODELS)) - 1
    if any(mask == all_models for mask in table.accepting):
        raise ValueError("universal compensator bypasses uncertainty")
    for i, model in enumerate(law.MODELS):
        points = law.support(model)
        if len(points) != 8:
            raise ValueError("support size is not eight")
        for j in range(5):
            if sum(1 if z >> j & 1 else -1 for z in points):
                raise ValueError("physical marginal is unbalanced")
        for j, k in combinations(range(5), 2):
            if any(
                sum(((z >> j & 1), (z >> k & 1)) == pair for z in points) != 2
                for pair in product(range(2), repeat=2)
            ):
                raise ValueError("pairwise independence failed")
        for build in law.BUILDS:
            if uncertainty_oracle(model, build) != law.accepted(model, build):
                raise ValueError("robust construction disagrees with independent dual-space oracle")
        if any(
            not tuple(values) in exposures[i] for values in (law.exposure(model, z) for z in points)
        ):
            raise ValueError("observation table misses a possible support point")
    total = Counter()
    unsupported = Counter()
    for model in law.MODELS:
        for k in range(1, 6):
            for subset in combinations(law.support(model), k):
                posterior = Belief(law.specification(model, 3, 4))
                for j, z in enumerate(subset):
                    posterior.observe(
                        Measurement("reader", {"query": (0, j), "values": law.exposure(model, z)})
                    )
                total[k] += 1
                unsupported[k] += not bool(posterior.common_decisions())
                if posterior.compatible_schedules != posterior.mask.bit_count() * factorial(8 - k):
                    raise ValueError("factored schedule multiplicity failed")
    if unsupported[1] != total[1] or not unsupported[4] or unsupported[5]:
        raise ValueError("one/four/five-sample qualification changed")
    # Any exact marginal/mean/covariance strategy leaves the full support prior.
    for model in law.MODELS:
        posterior = Belief(law.specification(model, 3, 4))
        for mode in (1, 2):
            world = law.Truth(**model.model_dump(), order=tuple(range(8)))
            posterior.observe(
                Measurement("reader", {"query": (mode, 0), "values": law.read(world, (mode, 0))})
            )
        if posterior.common_decisions():
            raise ValueError("reference/moments alone yield a supported compensator")
    # Independence replaces support with the complete cube, where z4 cannot be
    # predicted from four inputs. This checks its operational failure, not prose.
    independent_robust_builds = sum(
        all(
            ((-1) ** offset) * ((-1) ** ((z & mask).bit_count() % 2)) == (-1) ** (z >> 4 & 1)
            for z in range(32)
        )
        for mask, offset, pattern in law.BUILDS
    )
    if independent_robust_builds:
        raise ValueError("independent-channel baseline unexpectedly passes")
    return {
        "mechanism_models": 120,
        "physical_supports": 60,
        "fixture_assignments_per_model": factorial(8),
        "complete_worlds": 120 * factorial(8),
        "builds": len(law.BUILDS),
        "accepted_build_counts": dict(
            sorted(Counter(s.bit_count() for s in table.mission_signatures).items())
        ),
        "subset_totals": dict(total),
        "subsets_without_common_build": dict(unsupported),
        "universal_fixed_exposures_upper": 5,
        "four_exposures_not_guaranteed": True,
        "mean_covariance_only_supported": False,
        "independent_cube_valid_builds": independent_robust_builds,
        "best_uninformed_build_mass": max(m.bit_count() for m in table.accepting),
        "prior_mechanism_mass": 120,
        "repeated_fixture_information_gain": 0,
        "implicit_calibration_by_five_exposures": True,
        "all_science_can_precede_construction": True,
        "deep_tier_admitted": False,
    }


def prove_all():
    return {
        "version": "discovery-proof-v1",
        "representation": representation_proof(),
        "uncertainty": uncertainty_proof(),
        "scope": "Finite behavioral/robust acceptance and explicitly scoped shortcut witnesses. Query counts are not cognition or total-action lower bounds; fixture subset fractions use the full uniform mechanism/assignment prior, not selected-seed model-failure probabilities.",
        "deep_tier_admitted": False,
    }
