from __future__ import annotations

import hashlib
import heapq
import json
from collections import OrderedDict, deque
from dataclasses import dataclass
from itertools import count, product

from pydantic import BaseModel, ConfigDict

from nexus.diagnostics import timed_stage
from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.engine.goals import evaluate_goal
from nexus.models.actions import (
    Action,
    DropAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
    WaitAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.models.rules import Effect
from nexus.models.world import INVENTORY, TerminalStatus, WorldState
from nexus.solver.experiments import BudgetMemo, SEARCH_MODE
from nexus.solver.search import (
    SearchStateKey,
    goal_field_artifact_ids,
    goal_location_rooms,
    neighbors,
    search_state_key,
)


class PolicyWitnessNode(BaseModel):
    """One ordinary environment action in a private minimax policy witness."""

    model_config = ConfigDict(extra="forbid")

    action: dict[str, object]
    remaining_budget: int
    branches: tuple["PolicyWitnessBranch", ...] = ()


class PolicyWitnessBranch(BaseModel):
    """One observable outcome branch from a policy-witness action."""

    model_config = ConfigDict(extra="forbid")

    outcome: str
    viable_hypotheses: int
    next: PolicyWitnessNode | None = None


PolicyWitnessNode.model_rebuild()
PolicyWitnessBranch.model_rebuild()


class PolicyActionValue(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    action: Action
    worst_case_total_actions: int | None = None
    outcome_count: int = 1
    discriminative: bool = False


class BeliefPolicyResult(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    solvable: bool
    viable_hypothesis_count: int
    optimal_worst_case_actions: int | None = None
    initial_action_values: tuple[PolicyActionValue, ...] = ()
    witness: PolicyWitnessNode | None = None
    visited_belief_nodes: int = 0
    exhausted_action_limit: bool = False


class CompressedPhysicalResult(BaseModel):
    """Exact single-world result on the movement-quotiented interaction graph."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    solvable: bool
    optimal_action_count: int | None = None
    plan: tuple[Action, ...] = ()
    visited_states: int = 0
    max_frontier_size: int = 0
    exhausted_state_limit: bool = False


@dataclass(frozen=True)
class _MacroChoice:
    route: tuple[MoveAction, ...]
    action: Action

    @property
    def cost(self) -> int:
        return len(self.route) + 1


class _MovementOracle:
    """Deterministic shortest room paths for one immutable episode topology."""

    def __init__(self, episode: PrivateEpisode) -> None:
        self._paths: dict[tuple[str, str], tuple[MoveAction, ...]] = {}
        for source in sorted(episode.public.rooms):
            parents: dict[str, str | None] = {source: None}
            frontier: deque[str] = deque([source])
            while frontier:
                room = frontier.popleft()
                for adjacent in neighbors(episode, room):
                    if adjacent in parents:
                        continue
                    parents[adjacent] = room
                    frontier.append(adjacent)

            for target in sorted(parents):
                rooms: list[str] = []
                current = target
                while current != source:
                    rooms.append(current)
                    parent = parents[current]
                    if parent is None:
                        raise RuntimeError("shortest-path parent chain terminated early")
                    current = parent
                rooms.reverse()
                self._paths[(source, target)] = tuple(
                    MoveAction(target=room) for room in rooms
                )

    def route(self, source: str, target: str) -> tuple[MoveAction, ...] | None:
        return self._paths.get((source, target))


@dataclass(frozen=True)
class _CachedPolicyResult:
    max_actions: int
    result: BeliefPolicyResult


_POLICY_RESULT_CACHE: OrderedDict[
    tuple[str, int, int, tuple[str, ...]], _CachedPolicyResult
] = OrderedDict()
_POLICY_RESULT_CACHE_LIMIT = 16


def _action_identity(action: Action) -> str:
    return json.dumps(
        action.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )


def _action_value_selection_key(
    include_action_values: bool,
    requested_action_values: tuple[Action, ...] | None,
) -> tuple[str, ...]:
    if not include_action_values:
        return ("none",)
    if requested_action_values is None:
        return ("all",)
    return (
        "requested",
        *tuple(sorted({_action_identity(action) for action in requested_action_values})),
    )


def _policy_semantic_key(
    episode: PrivateEpisode,
    candidate_rules_by_machine: dict[str, list[Effect]],
) -> str:
    state = episode.public.initial_state.model_dump(mode="json")
    state["turn"] = 0
    state["resources"]["actions_remaining"] = 0
    payload = {
        "rooms": {
            room_id: room.model_dump(mode="json")
            for room_id, room in sorted(episode.public.rooms.items())
        },
        "edges": sorted(tuple(edge) for edge in episode.public.edges),
        "phase_modulus": episode.public.phase_modulus,
        "initial_state": state,
        "goal": episode.public.goal.model_dump(mode="json"),
        "candidate_rules_by_machine": {
            machine_id: [
                rule.model_dump(mode="json")
                for rule in candidate_rules_by_machine[machine_id]
            ]
            for machine_id in sorted(candidate_rules_by_machine)
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _cache_result(
    key: tuple[str, int, int, tuple[str, ...]],
    max_actions: int,
    result: BeliefPolicyResult,
) -> BeliefPolicyResult:
    existing = _POLICY_RESULT_CACHE.get(key)
    if existing is None or max_actions >= existing.max_actions:
        _POLICY_RESULT_CACHE[key] = _CachedPolicyResult(
            max_actions=max_actions,
            result=result.model_copy(deep=True),
        )
    _POLICY_RESULT_CACHE.move_to_end(key)
    while len(_POLICY_RESULT_CACHE) > _POLICY_RESULT_CACHE_LIMIT:
        _POLICY_RESULT_CACHE.popitem(last=False)
    return result


def _adapt_cached_result(
    cached: _CachedPolicyResult,
    *,
    max_actions: int,
    expected_actions: int | None,
    include_action_values: bool,
) -> BeliefPolicyResult | None:
    """Reuse an exact pure policy result without overstating a cached proof bound."""
    result = cached.result.model_copy(deep=True)
    optimum = result.optimal_worst_case_actions

    if optimum is None:
        # An exhausted search proves only that no policy exists through its searched bound.
        if max_actions > cached.max_actions:
            return None
        result.initial_action_values = ()
        return result

    if expected_actions is not None:
        if expected_actions != optimum or expected_actions > max_actions:
            return BeliefPolicyResult(
                solvable=False,
                viable_hypothesis_count=result.viable_hypothesis_count,
                visited_belief_nodes=result.visited_belief_nodes,
                exhausted_action_limit=expected_actions < optimum,
            )
    elif optimum > max_actions:
        return BeliefPolicyResult(
            solvable=False,
            viable_hypothesis_count=result.viable_hypothesis_count,
            visited_belief_nodes=result.visited_belief_nodes,
            exhausted_action_limit=True,
        )

    if not include_action_values:
        result.initial_action_values = ()
        return result

    # Action values are bounded analyses. A larger requested bound may resolve an action that was
    # None in the cached result, so only reuse rich values when the cached search covered at least
    # the requested range.
    if max_actions > cached.max_actions:
        return None
    result.initial_action_values = tuple(
        value.model_copy(
            update={
                "worst_case_total_actions": (
                    value.worst_case_total_actions
                    if value.worst_case_total_actions is None
                    or value.worst_case_total_actions <= max_actions
                    else None
                )
            }
        )
        for value in result.initial_action_values
    )
    return result


def _normalize_state(state: WorldState, search_budget: int) -> WorldState:
    """Normalize a caller-owned state by copying it first."""
    normalized = state.model_copy(deep=True)
    normalized.turn = 0
    normalized.resources.actions_remaining = search_budget
    return normalized


def _normalize_fresh_state(state: WorldState, search_budget: int) -> WorldState:
    """Normalize a fresh solver-owned transition state in place."""
    state.turn = 0
    state.resources.actions_remaining = search_budget
    return state


def _macro_sort_key(choice: _MacroChoice) -> tuple[int, int, str]:
    rank = {
        "finish": 0,
        "operate": 1,
        "probe": 2,
        "take": 3,
        "drop": 4,
        "wait": 5,
    }.get(choice.action.type, 9)
    return (
        choice.cost,
        rank,
        json.dumps(choice.action.model_dump(mode="json"), sort_keys=True),
    )


def _macro_choices(
    episode: PrivateEpisode,
    state: WorldState,
    movement: _MovementOracle,
    *,
    belief_mode: bool,
) -> tuple[_MacroChoice, ...]:
    """Enumerate exact movement-compressed interactions from an observable state."""
    if state.terminal_status != TerminalStatus.ACTIVE:
        return ()

    choices: list[_MacroChoice] = []
    if evaluate_goal(episode.public.goal, state):
        choices.append(_MacroChoice(route=(), action=FinishAction()))

    goal_rooms = goal_location_rooms(episode.public.goal)
    for artifact in sorted(state.artifacts.values(), key=lambda item: item.id):
        if artifact.location != INVENTORY:
            route = movement.route(state.agent_room, artifact.location)
            if route is not None:
                choices.append(
                    _MacroChoice(route=route, action=TakeAction(artifact=artifact.id))
                )
        else:
            for room_id in sorted(goal_rooms.get(artifact.id, ())):
                route = movement.route(state.agent_room, room_id)
                if route is not None:
                    choices.append(
                        _MacroChoice(route=route, action=DropAction(artifact=artifact.id))
                    )

    carried = sorted(artifact.id for artifact in state.carried_artifacts())
    goal_artifacts = goal_field_artifact_ids(episode.public.goal)
    total_machine_uses = sum(machine.uses_remaining for machine in state.machines.values())
    for machine in sorted(state.machines.values(), key=lambda item: item.id):
        route = movement.route(state.agent_room, machine.room_id)
        if route is None:
            continue
        for artifact_id in carried:
            if belief_mode:
                choices.append(
                    _MacroChoice(
                        route=route,
                        action=ProbeAction(machine=machine.id, artifact=artifact_id),
                    )
                )
            if machine.uses_remaining <= 0:
                continue

            if artifact_id in goal_artifacts or (belief_mode and total_machine_uses > 1):
                choices.append(
                    _MacroChoice(
                        route=route,
                        action=OperateAction(machine=machine.id, artifact=artifact_id),
                    )
                )

    if episode.public.phase_modulus > 1:
        choices.append(_MacroChoice(route=(), action=WaitAction()))

    choices.sort(key=_macro_sort_key)
    return tuple(choices)


def _apply_route(
    state: WorldState,
    route: tuple[MoveAction, ...],
    episode: PrivateEpisode,
    search_budget: int,
) -> WorldState | None:
    current = state
    for move in route:
        result = step(current, move, episode)
        if not result.ok:
            return None
        current = result.state
    if not route:
        return _normalize_state(state, search_budget)
    return _normalize_fresh_state(current, search_budget)


def _execute_macro(
    state: WorldState,
    choice: _MacroChoice,
    episode: PrivateEpisode,
    search_budget: int,
):
    moved = _apply_route(state, choice.route, episode, search_budget)
    if moved is None:
        return None
    result = step(moved, choice.action, episode)
    if not result.ok:
        return None
    result.state = _normalize_fresh_state(result.state, search_budget)
    return result


def solve_compressed_physical(
    episode: PrivateEpisode,
    *,
    initial_state: WorldState | None = None,
    max_states: int = 100_000,
) -> CompressedPhysicalResult:
    """Exact Dijkstra solver after quotienting side-effect-free movement into shortest paths."""
    search_budget = max(512, episode.public.initial_state.resources.actions_remaining + 64)
    initial = _normalize_state(
        initial_state if initial_state is not None else episode.public.initial_state,
        search_budget,
    )
    movement = _MovementOracle(episode)
    serial = count()
    frontier: list[tuple[int, int, WorldState, tuple[Action, ...]]] = [
        (0, next(serial), initial, ())
    ]
    best_cost = {search_state_key(initial): 0}
    max_frontier = 1

    while frontier:
        cost, _, state, plan = heapq.heappop(frontier)
        key = search_state_key(state)
        if cost != best_cost.get(key):
            continue
        if len(best_cost) > max_states:
            return CompressedPhysicalResult(
                solvable=False,
                visited_states=len(best_cost),
                max_frontier_size=max_frontier,
                exhausted_state_limit=True,
            )

        for choice in _macro_choices(episode, state, movement, belief_mode=False):
            result = _execute_macro(state, choice, episode, search_budget)
            if result is None:
                continue
            next_cost = cost + choice.cost
            next_plan = plan + choice.route + (choice.action,)
            if result.state.terminal_status == TerminalStatus.WON:
                return CompressedPhysicalResult(
                    solvable=True,
                    optimal_action_count=next_cost,
                    plan=next_plan,
                    visited_states=len(best_cost),
                    max_frontier_size=max_frontier,
                )
            if result.state.terminal_status != TerminalStatus.ACTIVE:
                continue

            next_key = search_state_key(result.state)
            previous = best_cost.get(next_key)
            if previous is not None and previous <= next_cost:
                continue
            best_cost[next_key] = next_cost
            heapq.heappush(
                frontier,
                (next_cost, next(serial), result.state, next_plan),
            )
            max_frontier = max(max_frontier, len(frontier))

    return CompressedPhysicalResult(
        solvable=False,
        visited_states=len(best_cost),
        max_frontier_size=max_frontier,
    )


def _episode_for_hypothesis(
    episode: PrivateEpisode,
    rules_by_machine: dict[str, Effect],
    *,
    search_budget: int,
) -> PrivateEpisode:
    # Hypotheses change only rules and the solver-local initial budget. Keep large immutable
    # episode payloads (evidence, metadata, witness, topology) shared while isolating every object
    # that this helper mutates.
    candidate = episode.model_copy(deep=False)
    candidate.public = episode.public.model_copy(deep=False)
    candidate.public.initial_state = episode.public.initial_state.model_copy(deep=True)
    candidate.public.initial_state.resources.actions_remaining = search_budget
    candidate.rules = dict(episode.rules)
    for machine_id, effect in rules_by_machine.items():
        rule_id = candidate.machine_rules[machine_id]
        candidate.rules[rule_id] = effect
    return candidate


def _probe_observation_key(result) -> str:
    event = next((item for item in result.events if item.type == "probe"), None)
    if event is None:
        raise ValueError("probe action did not emit a probe event")
    return json.dumps(event.details["result"], sort_keys=True, separators=(",", ":"))


def solve_guaranteed_policy(
    episode: PrivateEpisode,
    *,
    candidate_rules_by_machine: dict[str, list[Effect]],
    max_actions: int,
    max_physical_states: int = 100_000,
    max_hypotheses: int = 256,
    expected_actions: int | None = None,
    include_action_values: bool = True,
    requested_action_values: tuple[Action, ...] | None = None,
    minimum_guaranteed_probes: int | None = None,
) -> BeliefPolicyResult:
    """Solve the exact minimum worst-case total-action policy.

    Movement is compressed into deterministic shortest-path macro costs. The proof that this
    quotient preserves exact minimax cost is documented in
    docs/exact-belief-policy-solver-design.md.

    minimum_guaranteed_probes is accepted for API compatibility and validation only; probe count
    is not used as a total-action optimality certificate.
    """
    if max_actions < 1:
        raise ValueError("max_actions must be at least 1")
    if expected_actions is not None:
        if expected_actions < 1:
            raise ValueError("expected_actions must be at least 1")
        if expected_actions > max_actions:
            raise ValueError("expected_actions cannot exceed max_actions")
    if minimum_guaranteed_probes is not None and minimum_guaranteed_probes < 0:
        raise ValueError("minimum_guaranteed_probes cannot be negative")
    if requested_action_values is not None and not include_action_values:
        raise ValueError("requested_action_values requires include_action_values=True")

    semantic_key = _policy_semantic_key(episode, candidate_rules_by_machine)
    selection_key = _action_value_selection_key(
        include_action_values, requested_action_values
    )
    mode = SEARCH_MODE.get()
    if mode != "baseline":
        semantic_key = f"{semantic_key}|experiment={mode}"
    cache_key = (
        semantic_key,
        max_physical_states,
        max_hypotheses,
        selection_key,
    )
    cache_candidates = [cache_key]
    if not include_action_values:
        # A richer exact result contains the same minimax proof plus action-value analysis. A
        # no-action-value query may therefore reuse it, subject to the existing proof-bound
        # checks in _adapt_cached_result. Never reuse a weaker entry for a richer query.
        cache_candidates.extend(
            key
            for key in reversed(tuple(_POLICY_RESULT_CACHE.keys()))
            if key[:3] == cache_key[:3] and key != cache_key
        )
    for candidate_key in cache_candidates:
        cached = _POLICY_RESULT_CACHE.get(candidate_key)
        if cached is None:
            continue
        adapted = _adapt_cached_result(
            cached,
            max_actions=max_actions,
            expected_actions=expected_actions,
            include_action_values=include_action_values,
        )
        if adapted is not None:
            _POLICY_RESULT_CACHE.move_to_end(candidate_key)
            return adapted

    machine_ids = tuple(sorted(candidate_rules_by_machine))
    if not machine_ids or any(not candidate_rules_by_machine[item] for item in machine_ids):
        return BeliefPolicyResult(solvable=False, viable_hypothesis_count=0)

    combinations = tuple(
        dict(zip(machine_ids, rules))
        for rules in product(*(candidate_rules_by_machine[item] for item in machine_ids))
    )
    if len(combinations) > max_hypotheses:
        raise ValueError(
            f"causal hypothesis count {len(combinations)} exceeds limit {max_hypotheses}"
        )

    search_budget = max(512, max_actions + 64)
    hypothesis_episodes: list[PrivateEpisode] = []
    hypothesis_physical_optima: list[int] = []
    with timed_stage("policy.hypothesis_physical") as timing:
        for rules_by_machine in combinations:
            candidate = _episode_for_hypothesis(
                episode,
                rules_by_machine,
                search_budget=search_budget,
            )
            physical = solve_compressed_physical(candidate, max_states=max_physical_states)
            if physical.solvable and physical.optimal_action_count is not None:
                hypothesis_episodes.append(candidate)
                hypothesis_physical_optima.append(physical.optimal_action_count)
        timing["hypotheses"] = len(hypothesis_episodes)

    if not hypothesis_episodes:
        return BeliefPolicyResult(solvable=False, viable_hypothesis_count=0)

    initial_belief = frozenset(range(len(hypothesis_episodes)))
    initial_state = _normalize_state(episode.public.initial_state, search_budget)
    movement = _MovementOracle(episode)

    BranchSignature = str | SearchStateKey
    Branch = tuple[BranchSignature, WorldState, frozenset[int]]
    branch_cache: dict[
        tuple[SearchStateKey, frozenset[int], tuple[str, ...], str],
        tuple[Branch, ...] | None,
    ] = {}
    memo = BudgetMemo(monotone=mode in ("bounds", "combined"))
    state_ids: dict[SearchStateKey, int] = {}
    states: list[WorldState] = []
    object_ids: dict[int, int] = {}
    intern_states = mode in ("intern", "combined")

    def intern(state: WorldState) -> WorldState:
        if not intern_states:
            return state
        key = search_state_key(state)
        index = state_ids.get(key)
        if index is None:
            index = len(states)
            state_ids[key] = index
            states.append(state)
            object_ids[id(state)] = index
        # Retained states are read-only: engine.step copies before mutation.
        return states[index]

    def state_key(state: WorldState) -> int | SearchStateKey:
        return object_ids[id(state)] if intern_states else search_state_key(state)

    initial_state = intern(initial_state)

    def choice_key(choice: _MacroChoice) -> tuple[tuple[str, ...], str]:
        return (
            tuple(move.target for move in choice.route),
            _action_identity(choice.action),
        )

    def branches_for(
        state: WorldState,
        belief: frozenset[int],
        choice: _MacroChoice,
    ) -> tuple[Branch, ...] | None:
        route_key, action_key = choice_key(choice)
        key = (state_key(state), belief, route_key, action_key)
        if key in branch_cache:
            return branch_cache[key]

        representative_episode = hypothesis_episodes[next(iter(belief))]
        moved = _apply_route(state, choice.route, representative_episode, search_budget)
        if moved is None:
            branch_cache[key] = None
            return None

        if not isinstance(choice.action, (ProbeAction, OperateAction)):
            result = step(moved, choice.action, representative_episode)
            if not result.ok:
                branch_cache[key] = None
                return None
            next_state = intern(_normalize_fresh_state(result.state, search_budget))
            branches = ((search_state_key(next_state), next_state, belief),)
            branch_cache[key] = branches
            return branches

        grouped: dict[BranchSignature, tuple[WorldState, set[int]]] = {}
        for hypothesis_index in belief:
            result = step(moved, choice.action, hypothesis_episodes[hypothesis_index])
            if not result.ok:
                branch_cache[key] = None
                return None

            next_state = intern(_normalize_fresh_state(result.state, search_budget))
            if isinstance(choice.action, ProbeAction):
                signature: BranchSignature = "probe|" + _probe_observation_key(result)
            else:
                signature = search_state_key(next_state)

            existing = grouped.get(signature)
            if existing is None:
                grouped[signature] = (next_state, {hypothesis_index})
            else:
                representative, members = existing
                members.add(hypothesis_index)
                grouped[signature] = (representative, members)

        branches = tuple(
            (signature, state_value, frozenset(members))
            for signature, (state_value, members) in sorted(
                grouped.items(), key=lambda item: repr(item[0])
            )
        )
        branch_cache[key] = branches
        return branches

    def useless_probe(
        belief: frozenset[int],
        choice: _MacroChoice,
        branches: tuple[Branch, ...],
    ) -> bool:
        return (
            isinstance(choice.action, ProbeAction)
            and len(branches) == 1
            and branches[0][2] == belief
        )

    def can_win(state: WorldState, belief: frozenset[int], budget: int) -> bool:
        if state.terminal_status == TerminalStatus.WON:
            return True
        if state.terminal_status != TerminalStatus.ACTIVE or budget <= 0:
            return False

        key = (state_key(state), belief, budget)
        cached_value = memo.get(key)
        if cached_value is not None:
            return cached_value

        for choice in _macro_choices(episode, state, movement, belief_mode=True):
            if choice.cost > budget:
                continue
            branches = branches_for(state, belief, choice)
            if not branches or useless_probe(belief, choice, branches):
                continue
            remaining = budget - choice.cost
            if all(
                can_win(next_state, members, remaining)
                for _, next_state, members in branches
            ):
                memo[key] = True
                return True

        memo[key] = False
        return False

    lower_bound = max(hypothesis_physical_optima)
    optimal: int | None = None
    with timed_stage("policy.minimax") as timing:
        if expected_actions is None:
            for action_budget in range(lower_bound, max_actions + 1):
                if can_win(initial_state, initial_belief, action_budget):
                    optimal = action_budget
                    break
        else:
            sufficient = (
                expected_actions >= lower_bound
                and can_win(initial_state, initial_belief, expected_actions)
            )
            minimal = (
                expected_actions == lower_bound
                or (
                    expected_actions > lower_bound
                    and not can_win(initial_state, initial_belief, expected_actions - 1)
                )
            )
            if sufficient and minimal:
                optimal = expected_actions
        timing["memo_entries"] = len(memo)
        timing["branch_entries"] = len(branch_cache)
        timing["interned_states"] = len(states)
        timing["memo_hits"] = memo.hits

    def witness_outcome(signature: BranchSignature, state: WorldState) -> str:
        if isinstance(signature, str):
            return signature
        # Preserve the existing private witness representation while keeping SHA-256 out of
        # hot search-key paths. Witness construction touches only the selected optimal policy.
        payload = state.model_dump(mode="json")
        payload.pop("turn", None)
        resources = payload.get("resources", {})
        resources.pop("actions_remaining", None)
        return "state|" + canonical_hash(payload)

    def build_witness(
        state: WorldState,
        belief: frozenset[int],
        budget: int,
    ) -> PolicyWitnessNode | None:
        if state.terminal_status == TerminalStatus.WON:
            return None
        if budget <= 0:
            raise RuntimeError("cannot build policy witness beyond proved action budget")

        for choice in _macro_choices(episode, state, movement, belief_mode=True):
            if choice.cost > budget:
                continue
            branches = branches_for(state, belief, choice)
            if not branches or useless_probe(belief, choice, branches):
                continue
            remaining = budget - choice.cost
            if not all(
                can_win(next_state, members, remaining)
                for _, next_state, members in branches
            ):
                continue

            interaction_budget = budget - len(choice.route)
            interaction = PolicyWitnessNode(
                action=choice.action.model_dump(mode="json"),
                remaining_budget=interaction_budget,
                branches=tuple(
                    PolicyWitnessBranch(
                        outcome=witness_outcome(signature, next_state),
                        viable_hypotheses=len(members),
                        next=build_witness(next_state, members, remaining),
                    )
                    for signature, next_state, members in branches
                ),
            )

            node = interaction
            for index in range(len(choice.route) - 1, -1, -1):
                move = choice.route[index]
                node = PolicyWitnessNode(
                    action=move.model_dump(mode="json"),
                    remaining_budget=budget - index,
                    branches=(
                        PolicyWitnessBranch(
                            outcome=f"move|{move.target}",
                            viable_hypotheses=len(belief),
                            next=node,
                        ),
                    ),
                )
            return node

        raise RuntimeError("proved policy state has no witness macro")

    with timed_stage("policy.witness"):
        witness = (
            build_witness(initial_state, initial_belief, optimal)
            if optimal is not None
            else None
        )

    def action_value(choice: _MacroChoice) -> PolicyActionValue:
        branches = branches_for(initial_state, initial_belief, choice)
        if not branches:
            return PolicyActionValue(
                action=choice.action,
                worst_case_total_actions=None,
            )

        total_cost: int | None = None
        for candidate_total in range(max(lower_bound, choice.cost), max_actions + 1):
            remaining = candidate_total - choice.cost
            if all(
                can_win(next_state, members, remaining)
                for _, next_state, members in branches
            ):
                total_cost = candidate_total
                break

        outcome_count = len(branches)
        return PolicyActionValue(
            action=choice.action,
            worst_case_total_actions=total_cost,
            outcome_count=outcome_count,
            discriminative=(
                isinstance(choice.action, (ProbeAction, OperateAction))
                and outcome_count > 1
            ),
        )

    immediate_choices = tuple(
        choice
        for choice in _macro_choices(episode, initial_state, movement, belief_mode=True)
        if not choice.route
    )
    requested_identities = (
        None
        if requested_action_values is None
        else frozenset(_action_identity(action) for action in requested_action_values)
    )
    with timed_stage("policy.action_values") as timing:
        initial_values = (
            tuple(
                action_value(choice)
                for choice in immediate_choices
                if requested_identities is None
                or _action_identity(choice.action) in requested_identities
            )
            if include_action_values
            else ()
        )
        timing["memo_entries"] = len(memo)
        timing["branch_entries"] = len(branch_cache)
        timing["interned_states"] = len(states)
        timing["memo_hits"] = memo.hits
        timing["requested_values"] = len(initial_values)

    result = BeliefPolicyResult(
        solvable=optimal is not None,
        viable_hypothesis_count=len(hypothesis_episodes),
        optimal_worst_case_actions=optimal,
        initial_action_values=initial_values,
        witness=witness,
        # Experimental bounds mode counts state/belief intervals rather than exact budgets.
        visited_belief_nodes=len(memo),
        exhausted_action_limit=optimal is None,
    )
    # Cache pure exact results for both optimizer and fixed-cost certificate calls. A successful
    # certificate proves the same exact optimum; an exhausted result is reusable only through its
    # stored bound (enforced by _adapt_cached_result).
    return _cache_result(cache_key, max_actions, result)


def prove_guaranteed_policy_cost(
    episode: PrivateEpisode,
    *,
    candidate_rules_by_machine: dict[str, list[Effect]],
    expected_actions: int,
    max_physical_states: int = 100_000,
    max_hypotheses: int = 256,
    minimum_guaranteed_probes: int | None = None,
) -> BeliefPolicyResult:
    """Certify that expected_actions is the exact minimax policy cost."""
    return solve_guaranteed_policy(
        episode,
        candidate_rules_by_machine=candidate_rules_by_machine,
        max_actions=expected_actions,
        max_physical_states=max_physical_states,
        max_hypotheses=max_hypotheses,
        expected_actions=expected_actions,
        include_action_values=False,
        minimum_guaranteed_probes=minimum_guaranteed_probes,
    )
