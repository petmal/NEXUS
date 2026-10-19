"""Offline exhaustive proof with an independent literal-table arithmetic oracle.

The oracle uses only primitive lookup tables and tuple arithmetic; production
functions are imported solely for comparison. Neither generator nor runtime loads
this module. A failed or capped proof is not an admission certificate.
"""

from collections import Counter, deque
from itertools import combinations, product

from nexus.evaluation.goal_information import (
    feedback_success_ceiling,
    minimum_supporting_certificate,
)
from nexus.ontology.assembly.inference import Belief
from nexus.ontology.assembly.laws import (
    BUILDS,
    POINTS,
    QUERIES,
    WORLDS,
    accepted,
    physical,
    prepare,
    prior_mask,
    signature,
    tables,
    target,
)
from nexus.ontology.assembly.schema import Investigation, Specimen
from nexus.ontology.inference import Measurement
from nexus.solver.decision_audit import DecisionAudit

PRIMITIVES = (
    ((0, 1, 2), (1, 2, 0), (2, 0, 1)),
    ((0, 2, 1), (1, 0, 2), (2, 1, 0)),
    ((0, 0, 0), (0, 1, 2), (0, 2, 1)),
    ((0, 1, 2), (1, 2, 0), (1, 2, 0)),
)


def oracle_physical(build, x, y):
    s, a, t, b, h = build
    return PRIMITIVES[h][(s * x + a) % 3][(t * y + b) % 3]


def oracle_signature(build):
    return (
        build[0],
        build[2],
        *(oracle_physical(build, x, y) for x, y in product(range(3), repeat=2)),
    )


def oracle_read(raw, query, coupled=True):
    s, a, t, b, h, r = raw
    channel, x, y = query
    if not coupled:
        r = 0
    if channel == 0:
        return (s * x + a + r) % 3
    if channel == 1:
        return (t * y + b - r) % 3
    return (oracle_physical((s, a, t, b, h), x, y) + r) % 3


def closure(prior, outcomes, queries):
    mask = prior
    for q in queries:
        mask &= outcomes[q]
    return mask


def supporting_certificate(spec, index):
    table = tables(spec.coupled_reader)
    prior = prior_mask(spec)
    outcomes = tuple(
        parts[table.rows[index][q]] & prior for q, parts in enumerate(table.partitions)
    )
    winning = tuple(win & prior for win in set(table.accepting) if win >> index & 1)
    return minimum_supporting_certificate(prior, outcomes, winning)


def world_audit(spec, index):
    table = tables(spec.coupled_reader)
    prior = prior_mask(spec)
    if not prior >> index & 1:
        raise ValueError("selected world outside public prior")
    outcomes = tuple(
        parts[table.rows[index][q]] & prior for q, parts in enumerate(table.partitions)
    )
    panels = {
        "local_only": tuple(range(6)),
        "joint_only": tuple(range(6, 15)),
        "b_and_joint": (0, 1, 2, *range(6, 15)),
        "c_and_joint": (3, 4, 5, *range(6, 15)),
    }
    closures = {}
    for name, qs in panels.items():
        mask = closure(prior, outcomes, qs)
        closures[name] = {
            "remaining_worlds": mask.bit_count(),
            "remaining_mission_signatures": len(
                {table.signatures[i] for i in range(len(WORLDS)) if mask >> i & 1}
            ),
            "supported": any(not mask & ~win for win in table.accepting),
        }
    posterior = Belief(spec)
    policy = []
    while (q := posterior.choose_query()) is not None:
        ch, x, y = QUERIES[q]
        posterior.observe(
            Measurement("reader", {"channel": ch, "x": x, "y": y, "value": table.rows[index][q]})
        )
        policy.append(q)
    certificate = supporting_certificate(spec, index)
    return {
        "minimum_supporting_readings": len(certificate),
        "supporting_queries": certificate,
        "closures": closures,
        "public_policy_queries": policy,
        "public_policy_readings": len(policy),
        "remaining_worlds_after_policy": posterior.counts()[0],
        "common_builds_after_policy": len(posterior.common_decisions()),
    }


def oracle_certificate(rows, signatures, index, prior):
    """Independent exhaustive subset enumeration; no production search/bitset DP."""
    rivals = sum(
        1 << i for i in range(len(rows)) if prior >> i & 1 and signatures[i] != signatures[index]
    )
    actual = [
        sum(1 << i for i, row in enumerate(rows) if row[q] == rows[index][q]) for q in range(15)
    ]
    for size in range(8):
        for chosen in combinations(range(15), size):
            remaining = rivals
            for q in chosen:
                remaining &= actual[q]
            if not remaining:
                return size
    raise ValueError("independent certificate search exhausted bounded domain")


def physical_costs():
    """Independent BFS over the complete public preparation state/control graph.

    Excludes unavoidable take/finish and P1 movement. Reader, wait, copies, drop
    and previews cannot improve physical construction. Configure and all repeated
    forge/assembly operations are included, with no two-preparation restriction.
    """
    initial = (None, None, None, (0, 1, 0), 0)
    queue = deque([(initial, 0)])
    seen = {initial}
    costs = {}
    forge_controls = tuple(product(range(2), (1, 2), range(3)))
    while queue and len(costs) < len(BUILDS):
        (b, c, h, forge, assembler), cost = queue.popleft()
        if h is not None:
            costs.setdefault((*b, *c, h), cost)
        children = [(b, c, h, f, assembler) for f in forge_controls if f != forge]
        children.extend((b, c, h, forge, a) for a in range(4) if a != assembler)
        slot, gain, phase = forge
        if slot == 0:
            next_b = (gain, phase)
            next_c = None if c is None else (c[0], (c[1] + phase) % 3)
        else:
            next_c = (gain, phase)
            next_b = None if b is None else (b[0], (b[1] + phase) % 3)
        children.append((next_b, next_c, h, forge, assembler))
        if b is not None and c is not None:
            children.append((b, c, assembler, forge, assembler))
        for child in children:
            if child not in seen:
                seen.add(child)
                queue.append((child, cost + 1))
    if len(costs) != len(BUILDS):
        raise ValueError("public construction graph does not reach all builds")
    return costs


def prove_all():
    from nexus.ontology.assembly.policy import omniscient_construction

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    signatures = tuple(oracle_signature(target(w)) for w in WORLDS)
    raw = tuple((*target(w), w.offset) for w in WORLDS)
    costs = physical_costs()
    physical_histogram = Counter()
    for w in WORLDS:
        best = min(
            cost
            for build, cost in costs.items()
            if oracle_signature(build) == oracle_signature(target(w))
        )
        require(len(omniscient_construction(w)) == best, "private physical solver is not optimal")
        physical_histogram[best + 2] += 1
    for d in BUILDS:
        require(signature(d) == oracle_signature(d), "mission signature disagrees with oracle")
        require(
            all(physical(d, x, y) == oracle_physical(d, x, y) for x, y in POINTS),
            "physical arithmetic disagrees with oracle",
        )
        for w in WORLDS:
            require(
                accepted(w, d) == (oracle_signature(d) == oracle_signature(target(w))),
                "acceptance disagrees with oracle",
            )
    # Two preparations reach every target from all 49 prior component combinations,
    # including already assembled devices; no shortcut or dependency is a stage lock.
    components = (None, *product((1, 2), range(3)))
    construction_cases = 0
    for b, c in product(components, repeat=2):
        sample = Specimen(b=b, c=c, kernel=2 if b is not None and c is not None else None)
        for s, a, t, phase, h in BUILDS:
            final = prepare(prepare(sample, 0, s, (a - phase) % 3), 1, t, phase)
            require(
                final.b == (s, a) and final.c == (t, phase), "construction/recovery is not complete"
            )
            construction_cases += 1
    profiles = []
    for coupled in (False, True):
        table = tables(coupled)
        independent = tuple(tuple(oracle_read(w, q, coupled) for q in QUERIES) for w in raw)
        require(
            tuple(tuple(r) for r in table.rows) == independent, "observations disagree with oracle"
        )
        for theory, known in ((3, None), *((2, h) for h in range(4))):
            spec = Investigation(theory=theory, discovery=4 if coupled else 3, known_kernel=known)
            prior = prior_mask(spec)
            certs, counts = Counter(), Counter()
            supported = Counter()
            for i in range(len(WORLDS)):
                if not prior >> i & 1:
                    continue
                detail = world_audit(spec, i)
                exact = oracle_certificate(independent, signatures, i, prior)
                require(
                    exact == detail["minimum_supporting_readings"],
                    "certificate search disagrees with exhaustive oracle",
                )
                certs[exact] += 1
                counts[detail["public_policy_readings"]] += 1
                for name, value in detail["closures"].items():
                    supported[name] += int(value["supported"])
            require(max(counts) <= 7, "reference reading upper bound violated")
            profiles.append(
                {
                    "theory": theory,
                    "discovery": spec.discovery,
                    "known_kernel": known,
                    "worlds": prior.bit_count(),
                    "certificate_histogram": dict(sorted(certs.items())),
                    "policy_reading_histogram": dict(sorted(counts.items())),
                    "channel_closure_supported_worlds": dict(supported),
                }
            )
    table = tables(True)
    audit = DecisionAudit(
        len(WORLDS),
        tuple(bytes(row[q] for row in table.rows) for q in range(15)),
        tuple(sorted(set(table.accepting))),
    )
    exact = [
        {"readings": r, "guesses": g, "accepted_world_mass": audit.success_mass(r, g)}
        for r, g in ((0, 1), (1, 1), (2, 1), (0, 2), (1, 2))
    ]
    require(
        [v["accepted_world_mass"] for v in exact] == [9, 9, 27, 18, 18], "query/guess audit changed"
    )
    return {
        "version": "joint-assembly-proof-v1",
        "status": "passed",
        "worlds": 432,
        "complete_builds": len(BUILDS),
        "mission_signatures": len(set(signatures)),
        "construction_cases": construction_cases,
        "physical_optimal_actions_p0": dict(sorted(physical_histogram.items())),
        "profiles": profiles,
        "exact_query_guess_success_mass": exact,
        "feedback_success_upper_mass": [
            feedback_success_ceiling(432, 3, 9, k) for k in range(1, 8)
        ],
        "scope": "Exact complete-build evidence certificates exclude finish feedback and setup; exact small-horizon query/guess success and upper bounds include finishes with free preparation and setup. Uniform prior mass out of432, not model or curated-seed probabilities. Public policy is constructive, not optimal. No cognitive-depth claim.",
        "conformance": "All legal reader settings reduce to15 ternary query classes. Forge/assembler/stock/error/observation responses depend only on public state. Every complete eligible finish is membership in one of144 build masks. A relaxation grants every build and experiment for free setup; physical order, previews, stock copies and retries cannot give more hidden information than this audit.",
        "deep_tier_admitted": False,
    }
