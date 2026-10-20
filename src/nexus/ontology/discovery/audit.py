"""Offline, scoped shortcut certificates; never used to shape player observations."""

from collections import deque
from itertools import combinations

from nexus.evaluation.goal_information import minimum_supporting_certificate
from nexus.ontology.discovery.domains import module
from nexus.ontology.discovery.proof import representation_proof
from nexus.ontology.inference import Measurement


def predictive_witness(program):
    """Reachable histories with the same current view and a different future."""
    from nexus.ontology.representation.laws import advance, display

    paths = {(0, 0, 0): ()}
    pending = deque(paths)
    while pending:
        state = pending.popleft()
        for pulse in range(3):
            nxt = advance(program, state, pulse)
            if nxt not in paths:
                paths[nxt] = (*paths[state], pulse)
                pending.append(nxt)
    for a, b in combinations(paths, 2):
        if display(program, a) != display(program, b):
            continue
        queue = deque([(a, b, ())])
        seen = {(a, b)}
        while queue:
            left, right, word = queue.popleft()
            if display(program, left) != display(program, right):
                return {
                    "histories": [paths[a], paths[b]],
                    "same_display": display(program, a),
                    "distinguishing_suffix": word,
                    "future_displays": [display(program, left), display(program, right)],
                }
            for pulse in range(3):
                pair = advance(program, left, pulse), advance(program, right, pulse)
                if pair not in seen:
                    seen.add(pair)
                    queue.append((*pair, (*word, pulse)))
    return None


def world_audit(family, spec, world):
    laws = module(family, "laws")
    factory = module(family, "inference").Belief
    prior = factory(spec)
    posterior = factory(spec)
    transcript = []
    while (query := posterior.choose_query()) is not None:
        values = (
            laws.read(world.program, query)
            if family == "representation-discovery-v1"
            else laws.read(world, query)
        )
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
        if len(transcript) > 6:
            raise ValueError("public policy exceeded the proved bound")
    result = {
        "prior_mechanisms": prior.counts()[0],
        "prior_mission_classes": prior.counts()[1],
        "public_policy_readings": len(transcript),
        "public_policy_transcript": transcript,
        "supported_build": posterior.common_decisions()[0],
        "deep_tier_admitted": False,
        "certificate_scope": "Actual-outcome evidence only, with oracle query choice; excludes finish feedback and setup. Not a cognitive or policy-depth bound.",
    }
    if family == "representation-discovery-v1":
        index = laws.PROGRAM_INDEX[world.program]
        proof = representation_proof()
        table, rows, parts = laws.tables()
        win = table.accepting[index] & prior.mask
        query_for = {}
        for q, v in enumerate(rows[index]):
            query_for.setdefault(prior.mask & parts[q][v], laws.QUERIES[q])
        outcomes = tuple(query_for)
        certificate = None
        triples_checked = 0
        if prior.supports(world.program):
            lower = upper = 0
            certificate = ()
        elif (single := next((m for m in outcomes if m & ~win == 0), None)) is not None:
            lower = upper = 1
            certificate = (query_for[single],)
        elif (
            pair := next(((a, b) for a, b in combinations(outcomes, 2) if a & b & ~win == 0), None)
        ) is not None:
            lower = upper = 2
            certificate = tuple(query_for[m] for m in pair)
        else:
            lower, upper = 3, len(transcript)
            minimal = sorted(
                (m for m in outcomes if not any(n != m and n & m == n for n in outcomes)),
                key=int.bit_count,
            )
            for triple in combinations(minimal, 3):
                triples_checked += 1
                if triple[0] & triple[1] & triple[2] & ~win == 0:
                    upper = 3
                    certificate = tuple(query_for[m] for m in triple)
                    break
                if triples_checked == 100000:
                    break
        result.update(
            predictive_states=proof["predictive_states_by_program"][index],
            behavior_class=proof["classes_by_program"][index],
            skeleton=laws.skeleton(world.program),
            predictive_witness=predictive_witness(world.program),
            certificate_reading_lower=lower,
            certificate_reading_upper=upper,
            certificate_optimality_proven=lower == upper,
            supporting_certificate=certificate,
            triple_witness_candidates_checked=triples_checked,
            triple_witness_search_cap=100000,
            universal_fixed_panel_readings=len(proof["fixed_panel"]),
            blind_trial_guarantee_builds=len(
                {m & prior.mask for m in table.accepting if m & prior.mask}
            ),
        )
    else:
        outcomes = []
        for query in laws.QUERIES:
            belief = factory(spec)
            belief.observe(
                Measurement("reader", {"query": query, "values": laws.read(world, query)})
            )
            outcomes.append(belief.mask)
        winning = tuple(
            mask & prior.mask
            for b, mask in zip(prior.table.builds, prior.table.accepting)
            if laws.accepted(world, b)
        )
        certificate = minimum_supporting_certificate(prior.mask, tuple(outcomes), winning)
        moments = factory(spec)
        for mode in (1, 2):
            moments.observe(
                Measurement("reader", {"query": (mode, 0), "values": laws.read(world, (mode, 0))})
            )
        valid = tuple(b for b in laws.BUILDS if laws.accepted(world, b))
        uncovered, blind = prior.mask, []
        while uncovered:
            b = max(
                range(len(laws.BUILDS)),
                key=lambda j: (uncovered & prior.table.accepting[j]).bit_count(),
            )
            uncovered &= ~prior.table.accepting[b]
            blind.append(laws.BUILDS[b])
        result.update(
            certificate_reading_lower=len(certificate),
            certificate_reading_upper=len(certificate),
            certificate_optimality_proven=True,
            supporting_certificate=[laws.QUERIES[q] for q in certificate],
            moments_only_supported=bool(moments.common_decisions()),
            loading_matters_to_every_valid_build=all(b[0] & 10 for b in valid),
            valid_builds=valid,
            fixture_assignments=prior.compatible_schedules,
            universal_fixed_panel_readings=5,
            blind_trial_guarantee_builds=len(blind),
            blind_trial_panel=blind,
            blind_trial_optimality_proven=False,
        )
    result["blind_trial_action_upper"] = 1 + 3 * result["blind_trial_guarantee_builds"]
    return result
