"""Offline independent mechanics and explicit bounds, never player-visible hints."""

from collections import Counter, deque
from functools import cache
from itertools import combinations, permutations, product

from nexus.ontology.coupled_memory import laws
from nexus.ontology.coupled_memory.inference import Belief, choose
from nexus.ontology.inference import Measurement


def oracle(program, old, pulse):
    """Scalar packet transfer, intentionally not the production vector update."""
    order = tuple(permutations((0, 1, 2)))[program[0]]
    origin, destination = order[pulse], order[(pulse + 1) % 3]
    amount = 1
    parity = old[4] + old[destination] + program[1] * old[destination]
    if program[2]:
        parity += old[3]
    if parity % 2:
        amount += 1
    amount = min(amount, old[origin])
    result = list(old)
    for _ in range(amount):
        result[origin] -= 1
        result[destination] += 1
    result[3] = (old[3] + amount + (old[destination] if program[3] else 0)) % 3
    result[4] = (old[4] + old[3] + (amount if program[2] else 0)) % 3
    return tuple(result)


def oracle_signal(p, s):
    terms = [s[0]] * p[4] + [s[1]] + [s[3]] * p[5] + [s[4]]
    if p[6]:
        terms.extend([s[4]] * s[0])
    return sum(terms)


def ceiling_log(count, base):
    depth, capacity = 0, 1
    while capacity < count:
        capacity *= base
        depth += 1
    return depth


def certificate(index, mask):
    """Exact if <=3; fail closed rather than inventing an unproved optimum."""
    table, rows, parts = laws.tables()
    win = table.accepting[index]
    if not mask & ~win:
        return ()
    outcomes = {}
    for q, value in enumerate(rows[index]):
        outcomes.setdefault(mask & parts[q][value], q)
    for n in (1, 2, 3):
        for selection in combinations(outcomes, n):
            remaining = mask
            for outcome in selection:
                remaining &= outcome
            if not remaining & ~win:
                return tuple(laws.QUERIES[outcomes[m]] for m in selection)
    raise ValueError("certificate exceeds the audited three-reading bound")


def policy_tree(mask):
    q = choose(mask)
    if q is None:
        table = laws.tables()[0]
        build = next(b for b, m in zip(table.builds, table.accepting) if not mask & ~m)
        return {"build": build}, 0
    parts = laws.tables()[2][laws.QUERY_INDEX[q]]
    children, depths = {}, []
    for v, part in enumerate(parts):
        if branch := mask & part:
            child, depth = policy_tree(branch)
            children[str(v)] = child
            depths.append(depth)
    return {"query": q, "answers": children}, 1 + max(depths)


def predictive_witness(program):
    paths = {laws.INITIAL: ()}
    todo = deque(paths)
    while todo:
        state = todo.popleft()
        for x in range(3):
            nxt = oracle(program, state, x)
            if nxt not in paths:
                paths[nxt] = (*paths[state], x)
                todo.append(nxt)
    for a, b in combinations(paths, 2):
        if oracle_signal(program, a) % 3 != oracle_signal(program, b) % 3:
            continue
        pending, seen = deque([(a, b, ())]), {(a, b)}
        while pending:
            left, right, suffix = pending.popleft()
            values = [oracle_signal(program, s) % 3 for s in (left, right)]
            if values[0] != values[1]:
                return {
                    "histories": [paths[a], paths[b]],
                    "same_display": oracle_signal(program, a) % 3,
                    "suffix": suffix,
                    "future_displays": values,
                }
            for x in range(3):
                pair = oracle(program, left, x), oracle(program, right, x)
                if pair not in seen:
                    seen.add(pair)
                    pending.append((*pair, (*suffix, x)))
    return None


def matrix_policy(rows, alphabet):
    """Independent tree for bandwidth controls; wins are complete row classes."""
    groups = {}
    for i, row in enumerate(rows):
        groups[row] = groups.get(row, 0) | (1 << i)
    wins = tuple(groups.values())
    parts = tuple(
        tuple(sum(1 << i for i, row in enumerate(rows) if row[q] == v) for v in range(alphabet))
        for q in range(len(laws.QUERIES))
    )

    @cache
    def depth(mask):
        if any(not mask & ~win for win in wins):
            return 0
        q = min(
            range(len(parts)),
            key=lambda j: (
                max((mask & p).bit_count() for p in parts[j]),
                sum((mask & p).bit_count() ** 2 for p in parts[j]),
                len(laws.QUERIES[j]),
                laws.QUERIES[j],
            ),
        )
        return 1 + max(depth(mask & p) for p in parts[q] if mask & p)

    upper = depth((1 << len(rows)) - 1)
    lower = ceiling_log(len(wins), alphabet)
    return {
        "behavior_classes": len(wins),
        "reading_lower": lower,
        "reading_upper": upper,
        "optimality_proven": lower == upper,
        "scope": "Counterfactual sensor alphabet, not the live family.",
    }


def feedback_witness(program, direction):
    """Exhibit an observable consequence of removing a named causal connection."""
    paths = {(): laws.INITIAL}
    for word in laws.QUERIES:
        old = paths[word[:-1]]
        if direction == "memory_to_transfer":
            # Compute the flow with memory disconnected, but update the memory
            # from real prior values and the resulting physical transfer.
            order = laws.WIRINGS[program[0]]
            source, destination = order[word[-1]], order[(word[-1] + 1) % 3]
            next_q = oracle(program, (*old[:3], 0, 0), word[-1])[:3]
            flow = old[source] - next_q[source]
            state = (
                *next_q,
                (old[3] + flow + program[3] * old[destination]) % 3,
                (old[4] + old[3] + program[2] * flow) % 3,
            )
        elif direction == "material_to_memory":
            next_q = oracle(program, old, word[-1])[:3]
            state = (*next_q, old[3], (old[4] + old[3]) % 3)
        else:
            raise ValueError("unknown feedback ablation")
        paths[word] = state
        actual = laws.read(program, word)[0]
        ablated = oracle_signal(program, state) % 3
        if actual != ablated:
            return {"query": word, "actual": actual, "ablated": ablated}
    return None


@cache
def prove():
    states = tuple(
        (a, b, 4 - a - b, h, k)
        for a in range(5)
        for b in range(5 - a)
        for h in range(3)
        for k in range(3)
    )
    indices = {s: i for i, s in enumerate(states)}
    transitions, labels = [], []
    for p in laws.PROGRAMS:
        for s in states:
            row = []
            for x in range(3):
                nxt = oracle(p, s, x)
                if nxt != laws.advance(p, s, x) or nxt not in indices:
                    raise ValueError("independent transition/conservation conformance failed")
                row.append(indices[nxt])
            transitions.append(tuple(row))
            value = oracle_signal(p, s)
            if value != laws.signal(p, s) or value % 3 != laws.display(p, s):
                raise ValueError("independent observation conformance failed")
            labels.append(value % 3)
    width = len(states)
    blocks = labels[:]
    for _ in range(len(labels)):
        ids, new = {}, []
        for i, ts in enumerate(transitions):
            offset = i // width * width
            signature = (labels[i], *(blocks[offset + t] for t in ts))
            new.append(ids.setdefault(signature, len(ids)))
        if new == blocks:
            break
        blocks = new
    else:
        raise ValueError("partition refinement did not converge")
    classes = tuple(blocks[i * width + indices[laws.INITIAL]] for i in range(len(laws.PROGRAMS)))
    by_class = {}
    for i, c in enumerate(classes):
        by_class[c] = by_class.get(c, 0) | (1 << i)
    table, rows, _parts = laws.tables()
    if table.accepting != tuple(by_class[c] for c in classes):
        raise ValueError("reader signatures do not equal complete all-history behavior")
    reachable, predictive, controls = [], [], {2: [], 5: []}
    for i, p in enumerate(laws.PROGRAMS):
        seen, todo = {indices[laws.INITIAL]}, [indices[laws.INITIAL]]
        while todo:
            for nxt in transitions[i * width + todo.pop()]:
                if nxt not in seen:
                    seen.add(nxt)
                    todo.append(nxt)
        reachable.append(len(seen))
        predictive.append(len({blocks[i * width + s] for s in seen}))
        paths, control = {(): laws.INITIAL}, {2: [], 5: []}
        for q, word in enumerate(laws.QUERIES):
            state = oracle(p, paths[word[:-1]], word[-1])
            paths[word] = state
            signal = oracle_signal(p, state)
            if rows[i][q] != signal % 3:
                raise ValueError("cached reader row mismatch")
            control[2].append(int(signal % 5 >= 2))
            control[5].append(signal % 5)
        for alphabet in controls:
            controls[alphabet].append(bytes(control[alphabet]))
    # Every counterfactual row is unique: hence each corresponding full behavior
    # is distinct too. No full-machine equivalence shortcut is assumed there.
    if any(len(set(v)) != len(laws.PROGRAMS) for v in controls.values()):
        raise ValueError("bandwidth control lost full-prior identifiability")
    full = (1 << len(laws.PROGRAMS)) - 1
    tree, upper = policy_tree(full)
    lower = ceiling_log(len(by_class), 3)
    certificates = [certificate(i, full) for i in range(len(laws.PROGRAMS))]
    oracle_bounds = {}
    for label, selection in (
        ("known_dynamics", lambda p: p[:4]),
        ("known_encoder", lambda p: p[4:]),
    ):
        groups = {}
        for i, p in enumerate(laws.PROGRAMS):
            key = selection(p)
            groups[key] = groups.get(key, 0) | (1 << i)
        bounds = []
        for mask in groups.values():
            _, hi = policy_tree(mask)
            lo = ceiling_log(len({c for i, c in enumerate(classes) if mask >> i & 1}), 3)
            bounds.append((lo, hi))
        oracle_bounds[label] = {"bounds": sorted(set(bounds)), "priors": len(groups)}
    # Fixed panel greedy partition refinement is an upper bound, not optimum.
    cells, panel = [full], []
    while any(not any(not cell & ~m for m in by_class.values()) for cell in cells):
        q = min(
            range(len(laws.QUERIES)),
            key=lambda j: (
                sum((cell & p).bit_count() ** 2 for cell in cells for p in _parts[j]),
                len(laws.QUERIES[j]),
                laws.QUERIES[j],
            ),
        )
        new = [cell & p for cell in cells for p in _parts[q] if cell & p]
        if len(new) <= len(cells):
            raise ValueError("fixed panel stalled")
        panel.append(laws.QUERIES[q])
        cells = new
    encoders = tuple(product((1, 2), (1, 2), range(2)))
    support_only, frequency_signal = [], []
    for q in range(len(laws.QUERIES)):
        counts = [
            Counter(rows[i][q] for i, p in enumerate(laws.PROGRAMS) if p[4:] == e) for e in encoders
        ]
        if all(set(c) == {0, 1, 2} for c in counts):
            support_only.append(q)
        if len({tuple(c[v] for v in range(3)) for c in counts}) > 1:
            frequency_signal.append(q)
    cross_encoder = sum(
        len({laws.PROGRAMS[i][4:] for i in range(len(classes)) if mask >> i & 1}) > 1
        for mask in by_class.values()
    )
    if (len(by_class), lower, upper, set(map(len, certificates))) != (336, 6, 6, {3}):
        raise ValueError("versioned qualification expectations changed")
    return {
        "version": "coupled-memory-proof-v1",
        "programs": len(classes),
        "behavior_classes": len(by_class),
        "classes": classes,
        "reachable_states": reachable,
        "predictive_states": predictive,
        "all_history_partition_matches_reader": True,
        "all_legal_states_checked": len(labels),
        "adaptive_reading_lower": lower,
        "adaptive_reading_upper": upper,
        "adaptive_optimality_proven": lower == upper,
        "decision_tree": tree,
        "certificates": certificates,
        "certificate_scope": "Actual truth selects queries; these are not a public three-read policy.",
        "fixed_panel": panel,
        "fixed_panel_lower": lower,
        "fixed_panel_upper": len(panel),
        "fixed_panel_optimality_proven": lower == len(panel),
        "oracle_ablations": oracle_bounds,
        "bandwidth_controls": {str(a): matrix_policy(tuple(v), a) for a, v in controls.items()},
        "single_queries_eliminating_no_encoder": len(support_only),
        "single_queries_with_encoder_frequency_signal": len(frequency_signal),
        "behavior_classes_spanning_encoders": cross_encoder,
        "feedback_ablations": {
            direction: [feedback_witness(p, direction) for p in laws.PROGRAMS]
            for direction in ("memory_to_transfer", "material_to_memory")
        },
        "calibration_first_global_parameter_identifiability": False,
        "calibration_first_scope": "Cross-encoder mission-equivalent programs cannot be distinguished by ANY query panel. This is parameter nonidentifiability, not difficulty. Bounded calibration-first policy optimality is not claimed.",
        "mixed_probe_finish_evidence_event_lower": lower,
        "mixed_probe_finish_evidence_event_upper": upper + 1,
        "mixed_scope": "Reader has at most three outcomes, eligible finish at most two. Lower bound counts BOTH; upper includes successful finish. No exact total-action bound or mandatory reader count.",
        "reference_action_upper": 2 * upper + 4,
        "deep_tier_admitted": False,
        "empirical_difficulty_calibrated": False,
    }


def world_audit(spec, world):
    proof = prove()
    posterior = Belief(spec)
    prior = posterior.mask
    transcript = []
    while (query := posterior.choose_query()) is not None:
        values = laws.read_world(world, query)
        posterior.observe(Measurement("reader", {"query": query, "values": values}))
        transcript.append(
            {
                "query": query,
                "values": values,
                "remaining_mechanisms": posterior.counts()[0],
                "remaining_mission_classes": posterior.counts()[1],
                "common_builds": len(posterior.common_decisions()),
            }
        )
    index = laws.PROGRAM_INDEX[world.program]
    cert = certificate(index, prior)
    masks = {m & prior for m in posterior.table.accepting if m & prior}
    return {
        "prior_mechanisms": prior.bit_count(),
        "prior_mission_classes": len(masks),
        "public_policy_readings": len(transcript),
        "public_policy_transcript": transcript,
        "supported_build": posterior.common_decisions()[0],
        "supporting_certificate": cert,
        "certificate_reading_lower": len(cert),
        "certificate_reading_upper": len(cert),
        "certificate_optimality_proven": True,
        "certificate_scope": proof["certificate_scope"],
        "reachable_states": proof["reachable_states"][index],
        "predictive_states": proof["predictive_states"][index],
        "behavior_class": proof["classes"][index],
        "dynamics": world.program[:4],
        "predictive_witness": predictive_witness(world.program),
        "feedback_witnesses": {k: v[index] for k, v in proof["feedback_ablations"].items()},
        "blind_trial_guarantee_builds": len(masks),
        "blind_trial_action_upper": 1 + 3 * len(masks),
        "best_uninformed_build_program_mass": max(m.bit_count() for m in masks),
        "deep_tier_admitted": False,
    }
