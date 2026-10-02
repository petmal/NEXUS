from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from functools import lru_cache
from itertools import permutations

import networkx as nx

from nexus.engine.rules import apply_effect
from nexus.generator.difficulty import (
    EXECUTION_SLACK,
    GENERATION_SOLVER_BUDGET,
    MAX_PHYSICAL_OPTIMAL_ACTIONS,
    artifact_projection,
    chain_requires_both_in_order,
    exploration_allowance,
    machine_count_for_discovery,
    recommended_tool_call_limit,
    required_probe_count,
    room_bounds,
    validate_difficulty_levels,
)
from nexus.generator.discovery import DiscoveryAnalysis, analyze_discovery
from nexus.generator.evidence import (
    EvidencePlanningError,
    candidates_matching_csv,
    choose_mission_evidence,
    evidence_csv,
    measurement_filename,
)
from nexus.generator.manual import FACILITY_MANUAL
from nexus.generator.randomness import rng_for, scenario_family_id
from nexus.generator.rules import (
    enumerate_transformation_rules,
    rule_ast_metrics,
    sample_transformation_rule,
)
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.rules import Effect
from nexus.models.world import (
    Artifact,
    Machine,
    Orientation,
    Pattern,
    Polarity,
    Resources,
    Room,
    Shape,
    WorldState,
)
from nexus.solver.search import solve


class GenerationError(RuntimeError):
    pass


@dataclass(frozen=True)
class _EvidenceProfile:
    files: dict[str, str]
    candidate_counts: dict[str, int]
    rows_by_machine: dict[str, int]
    prediction_counts: dict[str, int]
    direct_examples: dict[str, bool]
    analysis: DiscoveryAnalysis


@dataclass(frozen=True)
class _MechanicsFamily:
    kind: str
    attempt: int
    family_id: str
    machine_ids: tuple[str, ...]
    selected_rules: dict[str, Effect]
    initial_artifact: Artifact
    phases: dict[str, int]
    target_artifact: Artifact
    evidence_profiles: dict[int, _EvidenceProfile]
    requires_both: bool


def _random_tree(rng, count: int) -> tuple[dict[str, Room], tuple[tuple[str, str], ...]]:
    ids = [f"R{i}" for i in range(count)]
    edges: list[tuple[str, str]] = []
    for index in range(1, count):
        edges.append((ids[index], ids[rng.randrange(index)]))
    rooms = {room_id: Room(id=room_id, label=f"Chamber {room_id[1:]}") for room_id in ids}
    return rooms, tuple(edges)


def _role_rooms(
    rooms: dict[str, Room],
    edges: tuple[tuple[str, str], ...],
    *,
    machine_count: int,
) -> tuple[str, tuple[str, ...], str, int]:
    """Choose distinct role rooms that maximize the intended route length."""
    graph = nx.Graph()
    graph.add_nodes_from(rooms)
    graph.add_edges_from(edges)
    start = "R0"
    distances = dict(nx.all_pairs_shortest_path_length(graph))

    role_count = machine_count + 2
    candidates = [room_id for room_id in rooms if room_id != start]
    if len(candidates) < role_count:
        raise GenerationError("not enough rooms for distinct episode roles")

    best: tuple[int, tuple[str, ...]] | None = None
    for assignment in permutations(candidates, role_count):
        artifact_room = assignment[0]
        machine_rooms = assignment[1 : 1 + machine_count]
        destination = assignment[-1]
        route = (start, artifact_room, *machine_rooms, destination)
        score = sum(distances[left][right] for left, right in zip(route, route[1:]))
        candidate = (score, assignment)
        if best is None or candidate > best:
            best = candidate

    if best is None:
        raise GenerationError("unable to assign distinct role rooms")

    distance_sum, assignment = best
    return (
        assignment[0],
        tuple(assignment[1 : 1 + machine_count]),
        assignment[-1],
        distance_sum,
    )


def _graph_diameter(rooms: dict[str, Room], edges: tuple[tuple[str, str], ...]) -> int:
    graph = nx.Graph()
    graph.add_nodes_from(rooms)
    graph.add_edges_from(edges)
    return nx.diameter(graph)


def _goal_for(artifact: Artifact, destination: str, phase: int) -> GoalPredicate:
    return GoalPredicate(
        kind=GoalKind.AND,
        children=(
            GoalPredicate(
                kind=GoalKind.ARTIFACT_LOCATION,
                artifact_id="A1",
                value=destination,
            ),
            GoalPredicate(
                kind=GoalKind.ARTIFACT_FIELD,
                artifact_id="A1",
                field="value",
                value=artifact.value,
            ),
            GoalPredicate(
                kind=GoalKind.ARTIFACT_FIELD,
                artifact_id="A1",
                field="polarity",
                value=artifact.polarity.value,
            ),
            GoalPredicate(
                kind=GoalKind.ARTIFACT_FIELD,
                artifact_id="A1",
                field="orientation",
                value=artifact.orientation.value,
            ),
            GoalPredicate(kind=GoalKind.PHASE_EQUALS, value=phase),
        ),
    )


def _description(
    *,
    machine_ids: tuple[str, ...],
    destination: str,
    target: Artifact,
    target_phase: int,
) -> str:
    machines = (
        f"the unknown machine {machine_ids[0]}"
        if len(machine_ids) == 1
        else "the unknown machines " + " and ".join(machine_ids)
    )
    return (
        f"Transformation Facility. Recover artifact A1, use {machines} as needed, "
        f"and deliver A1 to {destination}. The final artifact must have value {target.value}, "
        f"polarity {target.polarity.value}, orientation {target.orientation.value}, "
        f"while the facility phase is {target_phase}. The phase advances only when you wait. "
        "The supplied facility_manual.txt defines the possible machine-law grammar. "
        "Each measurements file contains prior experiments for the machine named by that file. "
        "Infer or experimentally discover the behavior needed to complete the mission, "
        "then finish explicitly."
    )


def _rule_ids(machine_ids: tuple[str, ...]) -> tuple[dict[str, str], dict[str, str]]:
    rules_by_machine: dict[str, str] = {}
    machine_rules: dict[str, str] = {}
    for machine_id in machine_ids:
        rule_id = "machine-rule" if machine_id == "M1" else f"machine-rule-{machine_id}"
        rules_by_machine[machine_id] = rule_id
        machine_rules[machine_id] = rule_id
    return rules_by_machine, machine_rules


def _compile_evidence_profile(
    *,
    discovery_level: int,
    machine_ids: tuple[str, ...],
    selected_rules: dict[str, Effect],
    all_candidates: list[Effect],
    stage_inputs: dict[str, Artifact],
    initial_artifact: Artifact,
    target_artifact: Artifact,
    phases: dict[str, int],
) -> _EvidenceProfile:
    files = {"facility_manual.txt": FACILITY_MANUAL}
    candidate_counts: dict[str, int] = {}
    rows_by_machine: dict[str, int] = {}
    prediction_counts: dict[str, int] = {}
    direct_examples: dict[str, bool] = {}

    evidence_level = 2 if discovery_level == 3 else discovery_level
    for machine_id in machine_ids:
        plan = choose_mission_evidence(
            selected_rules[machine_id],
            all_candidates,
            stage_inputs[machine_id],
            phases[machine_id],
            discovery_level=evidence_level,
        )
        files[measurement_filename(machine_id)] = evidence_csv(
            selected_rules[machine_id],
            plan.experiments,
        )
        candidate_counts[machine_id] = plan.candidate_count
        rows_by_machine[machine_id] = len(plan.experiments)
        prediction_counts[machine_id] = plan.prediction_count
        direct_examples[machine_id] = plan.direct_target_example

    candidate_rules_by_machine = {
        machine_id: candidates_matching_csv(
            files[measurement_filename(machine_id)],
            all_candidates,
        )
        for machine_id in machine_ids
    }
    analysis = analyze_discovery(
        candidate_rules_by_machine=candidate_rules_by_machine,
        initial_artifact=initial_artifact,
        target_artifact=target_artifact,
        phase_modulus=4,
    )
    if analysis.minimum_guaranteed_probes != required_probe_count(discovery_level):
        raise EvidencePlanningError("evidence does not satisfy the requested guaranteed probe count")

    if discovery_level == 0:
        valid = (
            machine_ids == ("M1",)
            and direct_examples["M1"]
            and candidate_counts["M1"] == 1
            and prediction_counts["M1"] == 1
        )
    elif discovery_level == 1:
        valid = (
            machine_ids == ("M1",)
            and not direct_examples["M1"]
            and prediction_counts["M1"] == 1
        )
    elif discovery_level == 2:
        valid = (
            machine_ids == ("M1",)
            and not direct_examples["M1"]
            and prediction_counts["M1"] > 1
        )
    else:
        valid = (
            machine_ids == ("M1", "M2")
            and all(not direct_examples[machine_id] for machine_id in machine_ids)
            and all(prediction_counts[machine_id] > 1 for machine_id in machine_ids)
        )

    if not valid:
        raise EvidencePlanningError("evidence does not satisfy the discovery profile semantics")

    return _EvidenceProfile(
        files=files,
        candidate_counts=candidate_counts,
        rows_by_machine=rows_by_machine,
        prediction_counts=prediction_counts,
        direct_examples=direct_examples,
        analysis=analysis,
    )


@lru_cache(maxsize=256)
def _find_mechanics_family(
    seed: int,
    family_kind: str,
    max_attempts: int,
) -> _MechanicsFamily:
    if family_kind not in {"one-machine", "two-machine"}:
        raise ValueError(f"unknown scenario family kind: {family_kind}")
    machine_count = 2 if family_kind == "two-machine" else 1
    machine_ids = tuple(f"M{index + 1}" for index in range(machine_count))
    required_profiles = (3,) if family_kind == "two-machine" else (0, 1, 2)
    all_candidates = enumerate_transformation_rules()

    for family_attempt in range(max_attempts):
        rng = rng_for(seed, "mechanics", family_kind, family_attempt)
        selected_rules = {
            machine_id: sample_transformation_rule(rng) for machine_id in machine_ids
        }
        initial_artifact = Artifact(
            id="A1",
            location="@inventory",
            shape=rng.choice(tuple(Shape)),
            pattern=rng.choice(tuple(Pattern)),
            orientation=rng.choice(tuple(Orientation)),
            value=rng.randint(0, 10),
            polarity=rng.choice(tuple(Polarity)),
        )
        phases = {machine_id: rng.choice((0, 1)) for machine_id in machine_ids}

        stage_inputs: dict[str, Artifact] = {}
        current = initial_artifact
        chain_changed = True
        for machine_id in machine_ids:
            stage_inputs[machine_id] = current
            transformed = apply_effect(selected_rules[machine_id], current, phases[machine_id])
            if artifact_projection(transformed) == artifact_projection(current):
                chain_changed = False
                break
            current = transformed
        if not chain_changed:
            continue

        target_artifact = current
        requires_both = False
        if machine_count == 2:
            requires_both = chain_requires_both_in_order(
                initial_artifact,
                selected_rules["M1"],
                selected_rules["M2"],
                target_artifact,
                phase_modulus=4,
            )
            if not requires_both:
                continue

        try:
            profiles = {
                profile_level: _compile_evidence_profile(
                    discovery_level=profile_level,
                    machine_ids=machine_ids,
                    selected_rules=selected_rules,
                    all_candidates=all_candidates,
                    stage_inputs=stage_inputs,
                    initial_artifact=initial_artifact,
                    target_artifact=target_artifact,
                    phases=phases,
                )
                for profile_level in required_profiles
            }
        except EvidencePlanningError:
            continue

        return _MechanicsFamily(
            kind=family_kind,
            attempt=family_attempt,
            family_id=scenario_family_id(seed, family_kind, family_attempt),
            machine_ids=machine_ids,
            selected_rules=selected_rules,
            initial_artifact=initial_artifact,
            phases=phases,
            target_artifact=target_artifact,
            evidence_profiles=profiles,
            requires_both=requires_both,
        )

    raise GenerationError(
        f"failed to generate a scenario-family-compatible causal world in {max_attempts} "
        f"attempts for seed {seed} (discovery family={family_kind})"
    )


def generate_episode(
    seed: int,
    *,
    discovery_level: int = 0,
    planning_level: int = 1,
    max_attempts: int = 250,
    verifier_secret: str | None = None,
) -> PrivateEpisode:
    """Generate a deterministic, solver-qualified Transformation Facility episode.

    D0-D2 are compiled from one shared one-machine scenario family for a given seed. D3 uses a
    separate two-machine family. Topology has its own deterministic stream so changing planning
    level cannot reroll causal mechanics or evidence.
    """
    validate_difficulty_levels(discovery_level, planning_level)
    if verifier_secret == "":
        raise ValueError("verifier_secret must not be empty")
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    all_candidates = enumerate_transformation_rules()
    family_kind = "two-machine" if discovery_level == 3 else "one-machine"
    family = _find_mechanics_family(seed, family_kind, max_attempts)
    profile = family.evidence_profiles[discovery_level]
    machine_ids = family.machine_ids
    machine_count = len(machine_ids)
    min_rooms, max_rooms = room_bounds(planning_level, machine_count)
    probe_count = required_probe_count(discovery_level)

    # Once mechanics are selected they are never rerolled because of topology. This is the
    # scenario-pairing guarantee: topology retries stay entirely inside their named RNG stream.
    for topology_attempt in range(max_attempts):
        topology_rng = rng_for(
            seed,
            "topology",
            family.kind,
            family.attempt,
            planning_level,
            topology_attempt,
        )
        room_count = topology_rng.randint(min_rooms, max_rooms)
        rooms, edges = _random_tree(topology_rng, room_count)
        artifact_room, machine_rooms, nexus_room, distance_sum = _role_rooms(
            rooms,
            edges,
            machine_count=machine_count,
        )

        initial_artifact = family.initial_artifact.model_copy(
            update={"location": artifact_room}
        )
        target_artifact = family.target_artifact
        goal = _goal_for(
            target_artifact,
            nexus_room,
            family.phases[machine_ids[-1]],
        )
        machines = {
            machine_id: Machine(id=machine_id, room_id=room_id, uses_remaining=1)
            for machine_id, room_id in zip(machine_ids, machine_rooms)
        }
        initial_state = WorldState(
            phase=0,
            agent_room="R0",
            artifacts={"A1": initial_artifact},
            machines=machines,
            resources=Resources(actions_remaining=GENERATION_SOLVER_BUDGET),
        )

        episode_id = hashlib.sha256(
            (
                f"nexus-episode|{family.family_id}|d{discovery_level}|p{planning_level}|"
                f"t{topology_attempt}"
            ).encode("utf-8")
        ).hexdigest()[:16]

        public = PublicEpisode(
            episode_id=episode_id,
            description=_description(
                machine_ids=machine_ids,
                destination=nexus_room,
                target=target_artifact,
                target_phase=family.phases[machine_ids[-1]],
            ),
            rooms=rooms,
            edges=edges,
            phase_modulus=4,
            initial_state=initial_state,
            goal=goal,
            evidence_files=dict(profile.files),
        )

        rule_ids, machine_rules = _rule_ids(machine_ids)
        rules = {
            rule_ids[machine_id]: family.selected_rules[machine_id]
            for machine_id in machine_ids
        }
        node_metrics = {
            machine_id: rule_ast_metrics(family.selected_rules[machine_id])
            for machine_id in machine_ids
        }

        metadata = GenerationMetadata(
            generation_attempt=family.attempt,
            scenario_family_id=family.family_id,
            scenario_family_attempt=family.attempt,
            topology_attempt=topology_attempt,
            discovery_level=discovery_level,
            planning_level=planning_level,
            machine_count=machine_count,
            room_count=room_count,
            graph_diameter=_graph_diameter(rooms, edges),
            candidate_rules_before_evidence=len(all_candidates),
            candidate_rules_after_evidence=profile.candidate_counts["M1"],
            evidence_candidate_counts=dict(profile.candidate_counts),
            evidence_rows=profile.rows_by_machine["M1"],
            evidence_rows_by_machine=dict(profile.rows_by_machine),
            mission_relevant_prediction_counts=dict(profile.prediction_counts),
            direct_target_example=any(profile.direct_examples.values()),
            required_probe_count=probe_count,
            viable_causal_hypotheses=profile.analysis.viable_hypothesis_count,
            transformation_phases=dict(family.phases),
            requires_both_machines=family.requires_both,
            reverse_order_reaches_goal=False,
            estimated_reference_actions=distance_sum + machine_count + 3,
            rule_ast_nodes=max(nodes for nodes, _ in node_metrics.values()),
            rule_ast_depth=max(depth for _, depth in node_metrics.values()),
            rule_ast_nodes_by_machine={
                machine_id: metrics[0] for machine_id, metrics in node_metrics.items()
            },
            rule_ast_depth_by_machine={
                machine_id: metrics[1] for machine_id, metrics in node_metrics.items()
            },
        )

        private = PrivateEpisode(
            public=public,
            rules=rules,
            machine_rules=machine_rules,
            verifier_secret=(
                verifier_secret if verifier_secret is not None else secrets.token_hex(32)
            ),
            construction_seed=seed,
            generation_metadata=metadata,
        )

        solved = solve(private)
        if not solved.solvable or solved.optimal_action_count is None:
            continue
        if solved.optimal_action_count > MAX_PHYSICAL_OPTIMAL_ACTIONS:
            continue

        operations = [
            action.machine for action in solved.plan if getattr(action, "type", None) == "operate"
        ]
        if machine_count == 2 and operations != ["M1", "M2"]:
            continue

        allowance = exploration_allowance(room_count)
        action_budget = (
            solved.optimal_action_count
            + probe_count
            + allowance
            + EXECUTION_SLACK
        )
        private.public.initial_state.resources.actions_remaining = action_budget

        final_solve = solve(private)
        if (
            not final_solve.solvable
            or final_solve.optimal_action_count != solved.optimal_action_count
        ):
            continue

        private.reference_plan = tuple(
            action.model_dump(mode="json") for action in final_solve.plan
        )
        private.generation_metadata.estimated_reference_actions = final_solve.optimal_action_count
        private.generation_metadata.optimal_action_count = final_solve.optimal_action_count
        private.generation_metadata.action_budget = action_budget
        private.generation_metadata.exploration_allowance = allowance
        private.generation_metadata.recommended_tool_call_limit = recommended_tool_call_limit(
            action_budget,
            len(profile.files),
        )
        private.generation_metadata.solver_visited_states = final_solve.visited_states
        private.generation_metadata.solver_max_frontier_size = final_solve.max_frontier_size

        from nexus.generator.qualify import qualify_episode

        if not qualify_episode(private).passed:
            continue
        return private

    raise GenerationError(
        f"scenario family {family.family_id} was valid but no topology qualified in "
        f"{max_attempts} attempts for seed {seed} "
        f"(discovery_level={discovery_level}, planning_level={planning_level}); "
        "mechanics were intentionally not rerolled"
    )
