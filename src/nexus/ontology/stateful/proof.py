"""Exact, bounded qualification. Unknown searches never count as negative results."""

from functools import lru_cache
from itertools import product

from nexus.ontology.stateful.laws import DEAD, STATES, WORLDS, readout, tables
from nexus.ontology.stateful.policy import Investigator, investigator
from nexus.ontology.stateful.search import FINISH, planner

HANDOFF_HORIZON = 20
PREFIX_DEPTH = 2


def scalar_step(world, state, mode):
    """Independent tuple interpreter: no compiled transitions or encode helper."""
    if state is None:
        return None
    result = list(state)
    raised = 1
    for _ in range(world.powers[mode]):
        raised *= state[(mode + 1) % 4]
    increment = sum(1 + raised for _ in range(world.gains[mode]))
    result[mode] = (state[mode] + increment) % 5
    return None if result == [4, 4, 4, 4] else tuple(result)


@lru_cache(maxsize=1)
def prove_kernel():
    checks = 0
    for w, world in enumerate(WORLDS):
        for a in range(4):
            for s, state in enumerate((*STATES, None)):
                expected = scalar_step(world, state, a)
                actual = tables()[w][a][s]
                if expected != (None if actual == DEAD else STATES[actual]):
                    raise ValueError("compiled and independent state transition differ")
                if actual != DEAD and any(
                    STATES[actual][j] != state[j] for j in range(4) if j != a
                ):
                    raise ValueError("local actuator changed an unrelated register")
                checks += 1
    # Every proper coordinate subset has an incoming functional dependency.
    # This is a physical factorization statement, not universal cognitive depth.
    for mask in range(1, 15):
        if not any(mask & (1 << i) and not mask & (1 << ((i + 1) % 4)) for i in range(4)):
            raise ValueError("coordinate partition unexpectedly closed")
    return {
        "independent_transition_checks": checks,
        "proper_closed_coordinate_partitions": 0,
        "scope": "No autonomous physical coordinate blocks under the legal actuator interface; does not exclude arbitrary mental subproblems.",
    }


@lru_cache(maxsize=3)
def prove_public_policy(target):
    policy = investigator(target)
    p = policy.game
    costs = []
    for w in range(len(WORLDS)):
        belief, state, count = p.initial, (0, 0, 0, 0), 0
        while True:
            kind, word = policy.decisions[belief]
            for a in (*word, FINISH if kind == "install" else 4):
                count += 1
                if a == FINISH:
                    if state != target or not p.ready(belief):
                        raise ValueError("policy does not finish with a supported physical goal")
                    break
                after = scalar_step(WORLDS[w], state, a % 4)
                observation = 5 if after is None else after[0]
                if a < 4:
                    state = after
                    if state is None:
                        raise ValueError("public policy destroys a possible specimen")
                belief = dict(p.branches(belief, a))[observation]
            if kind == "install":
                break
            if count > policy.bound():
                raise ValueError("public policy exceeded certified upper bound")
        costs.append(count)
    if max(costs) != policy.bound():
        raise ValueError("all-world replay bound differs from constructive certificate")
    return {
        "worlds": len(WORLDS),
        "minimum_realized_actions": min(costs),
        "maximum_realized_actions": max(costs),
        "all_finishes_supported": True,
    }


def panel_groups(p, prefix):
    """Free current readout AND every legal probe, after every committed prefix step."""
    groups = {}
    for w, initial in p.initial:
        state = initial
        transcript = []
        for a in (None, *prefix):
            if a is not None:
                state = p.table[w][a][state]
            transcript.append((readout(state), *(readout(p.table[w][m][state]) for m in range(4))))
        groups.setdefault(tuple(transcript), []).append((w, state))
    return tuple(tuple(g) for g in groups.values())


@lru_cache(maxsize=512)
def blind_possible(target, belief, horizon):
    return planner(target).blind_possible(belief, horizon)


def handoff_audit(target, world, horizon=HANDOFF_HORIZON, *, stop_on_shortcut=False):
    p = planner(target)
    rows = []
    for length in range(PREFIX_DEPTH, -1, -1) if stop_on_shortcut else range(PREFIX_DEPTH + 1):
        for prefix in product(range(4), repeat=length):
            group = next(g for g in panel_groups(p, prefix) if any(w == world for w, _ in g))
            possible = blind_possible(target, group, horizon - length)
            rows.append(
                {"prefix": prefix, "remaining_laws": len(group), "blind_suffix_possible": possible}
            )
            if possible and stop_on_shortcut:
                return {
                    "horizon": horizon,
                    "prefix_depth": PREFIX_DEPTH,
                    "prefixes": rows,
                    "passes": False,
                    "exhaustive_prefix_coverage": False,
                    "scope": "Positive shortcut found; further exclusions are unnecessary for rejection.",
                }
    return {
        "horizon": horizon,
        "prefix_depth": PREFIX_DEPTH,
        "prefixes": rows,
        "passes": not any(r["blind_suffix_possible"] for r in rows),
        "exhaustive_prefix_coverage": True,
        "scope": "All fixed committed prefixes of length<=2, full free probe panels at every visited state, then transcript-selected observation-blind actions with success-aware repeated finish. Total physical/action suffix cost<=20; panel cost forgiven. Not an unbounded impossibility theorem.",
    }


def adaptive_witness(target, world):
    """Existence witness tailored offline to a realized branch, not a player hint.

    The resulting policy uses only observations. Every off-branch outcome has a
    public constructive continuation. The chosen truth helps FIND this strategy,
    but is never consulted to execute it. Do not call this a uniform-optimal policy.
    """
    p = planner(target)
    length, leading = p.supported_trace(world, safe=True)
    fallback = Investigator(target)
    belief, upper = p.initial, length
    branches = []
    spine = []
    for elapsed, a in enumerate(leading, 1):
        intended = p.actual_child(belief, a, world)
        spine.append((a, intended))
        for observation, other in p.branches(belief, a):
            if other == intended:
                continue
            cost = fallback.construct(other)
            if cost is None:
                raise ValueError("adaptive witness has an uncertified off-branch continuation")
            upper = max(upper, elapsed + cost)
            branches.append((elapsed, observation, cost, len(other)))
        belief = intended
    # Independently execute the contingent tree for EVERY possible law, including
    # any early successful mixed finish. No guessed success is counted twice.
    realized = []
    for w in range(len(WORLDS)):
        current, state, count, done = p.initial, (0, 0, 0, 0), 0, False

        def apply(a, law=WORLDS[w]):
            nonlocal current, state, count, done
            count += 1
            if a == FINISH:
                if state == target:
                    done = True
                else:
                    current = dict(p.branches(current, a))[False]
                return
            after = scalar_step(law, state, a % 4)
            observation = 5 if after is None else after[0]
            if a < 4:
                state = after
                if state is None:
                    raise ValueError("adaptive witness destroys an off-branch specimen")
            current = dict(p.branches(current, a))[observation]

        for a, intended in spine:
            apply(a)
            if done or current != intended:
                break
        while not done:
            kind, word = fallback.decisions[current]
            for a in (*word, FINISH if kind == "install" else 4):
                apply(a)
            if count > upper:
                raise ValueError("adaptive fallback exceeds its claimed bound")
        realized.append(count)
    if realized[world] != length or max(realized) != upper:
        raise ValueError("adaptive branch/all-outcome replay differs from certificate")
    return {
        "selected_branch_actions": length,
        "all_outcome_upper": upper,
        "leading_actions": leading,
        "fallbacks": branches,
        "independent_replayed_worlds": len(realized),
        "scope": "Existence of an observation-only contingent policy with this short realized branch and a checked safe continuation for every other observation; not a claimed universal optimum.",
    }


@lru_cache(maxsize=16)
def world_audit(target, world):
    p = planner(target)
    minimum = p.supported_minimum(world)
    progress, _ = p.supported_trace(world, free_initial_panel=True, operations_only=True)
    initial_group = next(g for g in panel_groups(p, ()) if any(w == world for w, _ in g))
    return {
        "supported_action_minimum": minimum,
        "physical_action_minimum": p.distance[world][0] + 1,
        "minimum_committed_operations_with_free_evidence": progress,
        "adaptive_witness": adaptive_witness(target, world),
        "handoff": handoff_audit(target, world),
        "initial_blind_through_22": initial_blind(target, initial_group),
        "cost_scope": "Seal already carried in array; finish included in action costs; operation lower bound makes all probes and failed finishes free. Success must be supported BEFORE final finish, except blind audit explicitly allows safe success-aware guessing.",
    }


@lru_cache(maxsize=8)
def initial_blind(target, belief):
    return planner(target).blind_possible(belief, 22, max_nodes=1_000_000)
