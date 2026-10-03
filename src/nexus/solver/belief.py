from __future__ import annotations

import json
from itertools import product

from pydantic import BaseModel, ConfigDict

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
from nexus.solver.search import goal_artifact_ids, goal_location_rooms, neighbors, search_state_key, solve


class PolicyWitnessNode(BaseModel):
    """One action in a private minimax policy witness."""

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


def _normalize_state(state: WorldState, search_budget: int) -> WorldState:
    normalized = state.model_copy(deep=True)
    normalized.turn = 0
    normalized.resources.actions_remaining = search_budget
    return normalized


def _legal_actions(episode: PrivateEpisode, state: WorldState) -> tuple[Action, ...]:
    if state.terminal_status != TerminalStatus.ACTIVE:
        return ()

    actions: list[Action] = []
    if evaluate_goal(episode.public.goal, state):
        actions.append(FinishAction())

    actions.extend(MoveAction(target=room) for room in neighbors(episode, state.agent_room))

    goal_rooms = goal_location_rooms(episode.public.goal)
    for artifact in sorted(state.artifacts.values(), key=lambda item: item.id):
        if artifact.location == state.agent_room:
            actions.append(TakeAction(artifact=artifact.id))
        elif (
            artifact.location == INVENTORY
            and state.agent_room in goal_rooms.get(artifact.id, set())
        ):
            actions.append(DropAction(artifact=artifact.id))

    carried = sorted(artifact.id for artifact in state.carried_artifacts())
    goal_artifacts = goal_artifact_ids(episode.public.goal)
    total_machine_uses = sum(machine.uses_remaining for machine in state.machines.values())
    for machine in sorted(state.machines.values(), key=lambda item: item.id):
        if machine.room_id != state.agent_room:
            continue
        for artifact_id in carried:
            # Probe semantics are intentionally stable across all discovery levels and do not
            # consume a machine use.
            actions.append(ProbeAction(machine=machine.id, artifact=artifact_id))
            if machine.uses_remaining <= 0:
                continue

            # A non-goal operation is dominated by probe only when this would consume the final
            # remaining machine use. If another use remains anywhere, mutating an auxiliary
            # artifact can construct a new context for a later experiment and must stay legal in
            # the exact belief-policy search.
            if artifact_id in goal_artifacts or total_machine_uses > 1:
                actions.append(OperateAction(machine=machine.id, artifact=artifact_id))

    if episode.public.phase_modulus > 1:
        actions.append(WaitAction())

    return tuple(actions)


def _episode_for_hypothesis(
    episode: PrivateEpisode,
    rules_by_machine: dict[str, Effect],
    *,
    search_budget: int,
) -> PrivateEpisode:
    candidate = episode.model_copy(deep=True)
    candidate.public.initial_state.resources.actions_remaining = search_budget
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
) -> BeliefPolicyResult:
    """Solve the minimum worst-case total-action policy over evidence-consistent worlds.

    The policy state is an observable physical state plus a set of still-viable latent rule
    combinations. Actions may branch on probe or operate observations. Every branch must remain
    winnable for a policy to be guaranteed.

    Candidate worlds that are physically impossible despite NEXUS's public winnability guarantee
    are removed before policy search, matching the existing causal-discovery semantics.

    The returned private witness is one optimal branching policy. Its branch labels encode only
    observations available after the corresponding action; it is never included in player-facing
    episode data.

    This solver deliberately ignores the episode's current action budget while proving policy
    cost. The caller chooses max_actions as a proof bound and may derive a runtime budget from
    the resulting optimum afterwards.
    """
    if max_actions < 1:
        raise ValueError("max_actions must be at least 1")

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

    engine_budget = max(512, max_actions + 8)
    hypothesis_episodes: list[PrivateEpisode] = []
    for rules_by_machine in combinations:
        candidate = _episode_for_hypothesis(
            episode,
            rules_by_machine,
            search_budget=engine_budget,
        )
        physical = solve(candidate, max_states=max_physical_states)
        if physical.solvable:
            hypothesis_episodes.append(candidate)

    if not hypothesis_episodes:
        return BeliefPolicyResult(solvable=False, viable_hypothesis_count=0)

    initial_belief = frozenset(range(len(hypothesis_episodes)))
    initial_state = _normalize_state(episode.public.initial_state, engine_budget)

    # Branch tuple: observable signature, representative physical state, surviving hypotheses.
    Branch = tuple[str, WorldState, frozenset[int]]
    memo: dict[tuple[str, frozenset[int], int], bool] = {}
    visited_nodes: set[tuple[str, frozenset[int], int]] = set()

    def branches_for(
        state: WorldState,
        belief: frozenset[int],
        action: Action,
    ) -> tuple[Branch, ...] | None:
        grouped: dict[str, tuple[WorldState, set[int]]] = {}

        for hypothesis_index in belief:
            result = step(state, action, hypothesis_episodes[hypothesis_index])
            if not result.ok:
                return None

            next_state = _normalize_state(result.state, engine_budget)
            if isinstance(action, ProbeAction):
                signature = "probe|" + _probe_observation_key(result)
            else:
                signature = "state|" + search_state_key(next_state)

            existing = grouped.get(signature)
            if existing is None:
                grouped[signature] = (next_state, {hypothesis_index})
            else:
                representative, members = existing
                members.add(hypothesis_index)
                grouped[signature] = (representative, members)

        return tuple(
            (signature, state_value, frozenset(members))
            for signature, (state_value, members) in sorted(grouped.items())
        )

    def useless_probe(
        state: WorldState,
        belief: frozenset[int],
        action: Action,
        branches: tuple[Branch, ...],
    ) -> bool:
        return (
            isinstance(action, ProbeAction)
            and len(branches) == 1
            and branches[0][2] == belief
            and search_state_key(branches[0][1]) == search_state_key(state)
        )

    def can_win(state: WorldState, belief: frozenset[int], budget: int) -> bool:
        if state.terminal_status == TerminalStatus.WON:
            return True
        if state.terminal_status != TerminalStatus.ACTIVE or budget <= 0:
            return False

        key = (search_state_key(state), belief, budget)
        cached = memo.get(key)
        if cached is not None:
            return cached
        visited_nodes.add(key)

        for action in _legal_actions(episode, state):
            branches = branches_for(state, belief, action)
            if not branches:
                continue
            if useless_probe(state, belief, action, branches):
                continue
            if all(
                can_win(next_state, members, budget - 1)
                for _, next_state, members in branches
            ):
                memo[key] = True
                return True

        memo[key] = False
        return False

    optimal: int | None = None
    for action_budget in range(1, max_actions + 1):
        if can_win(initial_state, initial_belief, action_budget):
            optimal = action_budget
            break

    def build_witness(
        state: WorldState,
        belief: frozenset[int],
        budget: int,
    ) -> PolicyWitnessNode | None:
        if state.terminal_status == TerminalStatus.WON:
            return None
        if budget <= 0:
            raise RuntimeError("cannot build policy witness beyond proved action budget")

        for action in _legal_actions(episode, state):
            branches = branches_for(state, belief, action)
            if not branches or useless_probe(state, belief, action, branches):
                continue
            if not all(
                can_win(next_state, members, budget - 1)
                for _, next_state, members in branches
            ):
                continue

            witness_branches = tuple(
                PolicyWitnessBranch(
                    outcome=signature,
                    viable_hypotheses=len(members),
                    next=build_witness(next_state, members, budget - 1),
                )
                for signature, next_state, members in branches
            )
            return PolicyWitnessNode(
                action=action.model_dump(mode="json"),
                remaining_budget=budget,
                branches=witness_branches,
            )

        raise RuntimeError("proved policy state has no witness action")

    witness = (
        build_witness(initial_state, initial_belief, optimal)
        if optimal is not None
        else None
    )

    def action_value(action: Action) -> PolicyActionValue:
        branches = branches_for(initial_state, initial_belief, action)
        if not branches:
            return PolicyActionValue(action=action, worst_case_total_actions=None)

        total_cost: int | None = None
        for candidate_total in range(1, max_actions + 1):
            if all(
                can_win(next_state, members, candidate_total - 1)
                for _, next_state, members in branches
            ):
                total_cost = candidate_total
                break

        outcome_count = len(branches)
        return PolicyActionValue(
            action=action,
            worst_case_total_actions=total_cost,
            outcome_count=outcome_count,
            discriminative=isinstance(action, (ProbeAction, OperateAction)) and outcome_count > 1,
        )

    initial_values = tuple(action_value(action) for action in _legal_actions(episode, initial_state))

    return BeliefPolicyResult(
        solvable=optimal is not None,
        viable_hypothesis_count=len(hypothesis_episodes),
        optimal_worst_case_actions=optimal,
        initial_action_values=initial_values,
        witness=witness,
        visited_belief_nodes=len(visited_nodes),
        exhausted_action_limit=optimal is None,
    )
