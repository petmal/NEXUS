from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from functools import lru_cache
from itertools import permutations

import networkx as nx

from nexus.diagnostics import generation_diagnostics, timed_call, timed_stage
from nexus.presentation import CURRENT, PresentationVersion, attach
from nexus.engine.rules import apply_effect
from nexus.generator.constructed import (
    CONSTRUCTOR_VALUE,
    DISTRACTOR_VALUE,
    MISSION_TARGET_VALUE,
    constant_value_rule,
    constructed_manual,
    constructed_mission_rule,
    constructed_mission_rules,
)
from nexus.generator.difficulty import (
    GENERATION_SOLVER_BUDGET,
    MAX_PHYSICAL_OPTIMAL_ACTIONS,
    artifact_projection,
    chain_requires_both_in_order,
    exploration_allowance,
    machine_count_for_discovery,
    recommended_tool_call_limit,
    required_probe_count,
    resource_allowance,
    room_bounds,
    validate_difficulty_levels,
)
from nexus.generator.discovery import DiscoveryAnalysis, DiscoveryBelief, analyze_discovery
from nexus.generator.evidence import (
    EvidencePlanningError,
    candidates_matching_csv,
    choose_mission_evidence,
    evidence_csv,
    experiment_pool,
    measurement_filename,
)
from nexus.generator.manual import FACILITY_MANUAL
from nexus.generator.randomness import rng_for, scenario_family_id
from nexus.generator.rules import (
    enumerate_transformation_rules,
    rule_ast_metrics,
    sample_transformation_rule,
)
from nexus.models.actions import OperateAction, ProbeAction
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
from nexus.solver.belief import solve_compressed_physical, solve_guaranteed_policy


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
class _SelectiveMechanicsFamily:
    attempt: int
    family_id: str
    selected_rule: Effect
    initial_artifact: Artifact
    target_artifact: Artifact
    target_phase: int
    epistemic_artifact: Artifact
    distractor_artifact: Artifact
    evidence_profile: _EvidenceProfile


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


def _farthest_room(
    rooms: dict[str, Room],
    edges: tuple[tuple[str, str], ...],
    *,
    start: str = "R0",
) -> tuple[str, int]:
    graph = nx.Graph()
    graph.add_nodes_from(rooms)
    graph.add_edges_from(edges)
    distances = nx.single_source_shortest_path_length(graph, start)
    distance = max(distances.values())
    room_id = max(room for room, value in distances.items() if value == distance)
    return room_id, distance


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
@timed_call("core.mechanics_evidence")
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



def _selective_description(*, destination: str, target: Artifact, target_phase: int) -> str:
    return (
        "Transformation Facility. Artifact A1 is the mission payload; A2 and A3 are ordinary "
        "carried samples that may be used for experiments but are not part of the success "
        f"predicate. Use the unknown machine M1 and deliver A1 to {destination}. The final A1 "
        f"must have value {target.value}, polarity {target.polarity.value}, "
        f"orientation {target.orientation.value}, while the facility phase is {target_phase}. "
        "The phase advances only when you wait. The supplied facility_manual.txt defines the "
        "possible machine-law grammar and measurements.csv contains prior M1 experiments. "
        "Infer or experimentally discover the behavior needed to complete the mission, then "
        "finish explicitly."
    )


def _shape_probe_samples(shape: Shape) -> list[Artifact]:
    samples: list[Artifact] = []
    seen: set[tuple[int, str, str]] = set()
    for experiment in experiment_pool():
        artifact = experiment.artifact
        if experiment.phase != 0 or artifact.shape != shape:
            continue
        key = (artifact.value, artifact.polarity.value, artifact.orientation.value)
        if key in seen:
            continue
        seen.add(key)
        samples.append(artifact)
    return samples


@lru_cache(maxsize=256)
@timed_call("core.selective_mechanics_evidence")
def _find_selective_family(seed: int, max_attempts: int) -> _SelectiveMechanicsFamily:
    all_candidates = enumerate_transformation_rules()

    for family_attempt in range(max_attempts):
        rng = rng_for(seed, "mechanics", "selective-one-machine", family_attempt)
        selected_rule = sample_transformation_rule(rng)
        target_phase = rng.choice((0, 1))
        orientation = rng.choice((Orientation.NORTH, Orientation.EAST))
        value = rng.choice((0, 1, 2, 4, 7))
        polarity = rng.choice(tuple(Polarity))

        # Evidence depends on the mission shape but not on which of the other two shapes is later
        # assigned to the epistemic or distractor sample. Analyze each mission shape once, then
        # try both remaining role assignments against that shared exact belief state.
        mission_shapes = list(Shape)
        rng.shuffle(mission_shapes)
        for mission_shape in mission_shapes:
            initial_artifact = Artifact(
                id="A1",
                location="@inventory",
                shape=mission_shape,
                pattern=Pattern.PLAIN,
                orientation=orientation,
                value=value,
                polarity=polarity,
            )
            target_artifact = apply_effect(selected_rule, initial_artifact, target_phase)
            if artifact_projection(target_artifact) == artifact_projection(initial_artifact):
                continue

            try:
                plan = choose_mission_evidence(
                    selected_rule,
                    all_candidates,
                    initial_artifact,
                    target_phase,
                    discovery_level=2,
                )
            except EvidencePlanningError:
                continue

            evidence_text = evidence_csv(selected_rule, plan.experiments)
            candidate_rules = candidates_matching_csv(evidence_text, all_candidates)
            analysis = analyze_discovery(
                candidate_rules_by_machine={"M1": candidate_rules},
                initial_artifact=initial_artifact,
                target_artifact=target_artifact,
                phase_modulus=4,
            )
            if (
                analysis.minimum_guaranteed_probes != 1
                or analysis.viable_hypothesis_count < 2
            ):
                continue

            belief = DiscoveryBelief(
                candidate_rules_by_machine={"M1": candidate_rules},
                initial_artifact=initial_artifact,
                target_artifact=target_artifact,
                phase_modulus=4,
            )

            remaining_shapes = [shape for shape in Shape if shape != mission_shape]
            role_pairs = [
                (remaining_shapes[0], remaining_shapes[1]),
                (remaining_shapes[1], remaining_shapes[0]),
            ]
            rng.shuffle(role_pairs)
            for epistemic_shape, distractor_shape in role_pairs:
                epistemic_samples = _shape_probe_samples(epistemic_shape)
                distractor_samples = _shape_probe_samples(distractor_shape)
                rng.shuffle(epistemic_samples)
                rng.shuffle(distractor_samples)

                epistemic: Artifact | None = None
                epistemic_analysis = None
                for sample in epistemic_samples:
                    candidate = sample.model_copy(update={"id": "A2", "location": "@inventory"})
                    experiment = belief.analyze_probe_context(
                        artifact=candidate,
                        machine_id="M1",
                        phase=0,
                    )
                    if (
                        experiment.discriminative
                        and experiment.mission_relevant
                        and experiment.worst_case_remaining_probes == 0
                    ):
                        epistemic = candidate
                        epistemic_analysis = experiment
                        break
                if epistemic is None or epistemic_analysis is None:
                    continue

                distractor: Artifact | None = None
                distractor_analysis = None
                for sample in distractor_samples:
                    candidate = sample.model_copy(update={"id": "A3", "location": "@inventory"})
                    experiment = belief.analyze_probe_context(
                        artifact=candidate,
                        machine_id="M1",
                        phase=0,
                    )
                    if not experiment.discriminative and experiment.outcome_count == 1:
                        distractor = candidate
                        distractor_analysis = experiment
                        break
                if distractor is None or distractor_analysis is None:
                    continue

                profile = _EvidenceProfile(
                    files={
                        "facility_manual.txt": FACILITY_MANUAL,
                        "measurements.csv": evidence_text,
                    },
                    candidate_counts={"M1": plan.candidate_count},
                    rows_by_machine={"M1": len(plan.experiments)},
                    prediction_counts={"M1": plan.prediction_count},
                    direct_examples={"M1": plan.direct_target_example},
                    analysis=analysis,
                )
                return _SelectiveMechanicsFamily(
                    attempt=family_attempt,
                    family_id=scenario_family_id(
                        seed,
                        "selective-one-machine",
                        family_attempt,
                    ),
                    selected_rule=selected_rule,
                    initial_artifact=initial_artifact,
                    target_artifact=target_artifact,
                    target_phase=target_phase,
                    epistemic_artifact=epistemic,
                    distractor_artifact=distractor,
                    evidence_profile=profile,
                )

    raise GenerationError(
        f"failed to generate a D4 selective-discovery causal world in {max_attempts} attempts "
        f"for seed {seed}"
    )

def _initial_operate_value(policy, machine_id: str, artifact_id: str):
    return next(
        (
            value
            for value in policy.initial_action_values
            if isinstance(value.action, OperateAction)
            and value.action.machine == machine_id
            and value.action.artifact == artifact_id
        ),
        None,
    )


def _initial_probe_value(policy, artifact_id: str):
    return next(
        (
            value
            for value in policy.initial_action_values
            if isinstance(value.action, ProbeAction)
            and value.action.machine == "M1"
            and value.action.artifact == artifact_id
        ),
        None,
    )


def _generate_selective_episode(
    seed: int,
    *,
    planning_level: int,
    max_attempts: int,
    verifier_secret: str | None,
    qualify_result: bool = True,
) -> PrivateEpisode:
    family = _find_selective_family(seed, max_attempts)
    profile = family.evidence_profile
    min_rooms, max_rooms = room_bounds(planning_level, 1)

    for topology_attempt in range(max_attempts):
        topology_rng = rng_for(
            seed,
            "topology",
            "selective-one-machine",
            family.attempt,
            planning_level,
            topology_attempt,
        )
        room_count = topology_rng.randint(min_rooms, max_rooms)
        rooms, edges = _random_tree(topology_rng, room_count)
        nexus_room, delivery_distance = _farthest_room(rooms, edges)

        artifacts = {
            "A1": family.initial_artifact.model_copy(
                update={"id": "A1", "location": "@inventory"}
            ),
            "A2": family.epistemic_artifact.model_copy(deep=True),
            "A3": family.distractor_artifact.model_copy(deep=True),
        }
        initial_state = WorldState(
            phase=0,
            agent_room="R0",
            artifacts=artifacts,
            machines={"M1": Machine(id="M1", room_id="R0", uses_remaining=1)},
            resources=Resources(actions_remaining=GENERATION_SOLVER_BUDGET),
        )
        goal = _goal_for(
            family.target_artifact,
            nexus_room,
            family.target_phase,
        )
        episode_id = hashlib.sha256(
            (
                f"nexus-episode|{family.family_id}|d4|p{planning_level}|"
                f"t{topology_attempt}"
            ).encode("utf-8")
        ).hexdigest()[:16]
        public = PublicEpisode(
            episode_id=episode_id,
            description=_selective_description(
                destination=nexus_room,
                target=family.target_artifact,
                target_phase=family.target_phase,
            ),
            rooms=rooms,
            edges=edges,
            phase_modulus=4,
            initial_state=initial_state,
            goal=goal,
            evidence_files=dict(profile.files),
        )
        nodes, depth = rule_ast_metrics(family.selected_rule)
        metadata = GenerationMetadata(
            generation_attempt=family.attempt,
            scenario_family_id=family.family_id,
            scenario_family_attempt=family.attempt,
            topology_attempt=topology_attempt,
            discovery_level=4,
            planning_level=planning_level,
            machine_count=1,
            room_count=room_count,
            graph_diameter=_graph_diameter(rooms, edges),
            candidate_rules_before_evidence=len(enumerate_transformation_rules()),
            candidate_rules_after_evidence=profile.candidate_counts["M1"],
            evidence_candidate_counts=dict(profile.candidate_counts),
            evidence_rows=profile.rows_by_machine["M1"],
            evidence_rows_by_machine=dict(profile.rows_by_machine),
            mission_relevant_prediction_counts=dict(profile.prediction_counts),
            direct_target_example=any(profile.direct_examples.values()),
            required_probe_count=1,
            viable_causal_hypotheses=profile.analysis.viable_hypothesis_count,
            transformation_phases={"M1": family.target_phase},
            epistemic_artifact_id="A2",
            distractor_artifact_id="A3",
            estimated_reference_actions=delivery_distance + 3,
            rule_ast_nodes=nodes,
            rule_ast_depth=depth,
            rule_ast_nodes_by_machine={"M1": nodes},
            rule_ast_depth_by_machine={"M1": depth},
        )
        private = PrivateEpisode(
            public=public,
            rules={"machine-rule": family.selected_rule},
            machine_rules={"M1": "machine-rule"},
            verifier_secret=(
                verifier_secret if verifier_secret is not None else secrets.token_hex(32)
            ),
            construction_seed=seed,
            generation_metadata=metadata,
        )

        physical = solve_compressed_physical(private)
        if (
            not physical.solvable
            or physical.optimal_action_count is None
            or physical.optimal_action_count > MAX_PHYSICAL_OPTIMAL_ACTIONS
        ):
            continue
        operation_count = sum(
            getattr(action, "type", None) == "operate" for action in physical.plan
        )
        if operation_count != 1:
            continue

        candidates = candidates_matching_csv(
            profile.files["measurements.csv"],
            enumerate_transformation_rules(),
        )
        policy_bound = min(
            GENERATION_SOLVER_BUDGET,
            physical.optimal_action_count + 16,
        )
        policy = solve_guaranteed_policy(
            private,
            candidate_rules_by_machine={"M1": candidates},
            max_actions=policy_bound,
            requested_action_values=(
                ProbeAction(machine="M1", artifact="A1"),
                ProbeAction(machine="M1", artifact="A2"),
                ProbeAction(machine="M1", artifact="A3"),
            ),
        )
        if (
            not policy.solvable
            or policy.optimal_worst_case_actions is None
            or policy.viable_hypothesis_count < 2
        ):
            continue

        mission_probe = _initial_probe_value(policy, "A1")
        epistemic_probe = _initial_probe_value(policy, "A2")
        distractor_probe = _initial_probe_value(policy, "A3")
        if (
            mission_probe is None
            or epistemic_probe is None
            or distractor_probe is None
            or mission_probe.worst_case_total_actions
            != policy.optimal_worst_case_actions
            or not epistemic_probe.discriminative
            or epistemic_probe.worst_case_total_actions
            != policy.optimal_worst_case_actions
            or distractor_probe.discriminative
            or distractor_probe.outcome_count != 1
            or distractor_probe.worst_case_total_actions
            != policy.optimal_worst_case_actions + 1
        ):
            continue

        exploration = exploration_allowance(room_count)
        allowance = resource_allowance(room_count, 0)
        action_budget = policy.optimal_worst_case_actions + allowance
        private.public.initial_state.resources.actions_remaining = action_budget

        private.reference_plan = tuple(
            action.model_dump(mode="json") for action in physical.plan
        )
        metadata = private.generation_metadata
        metadata.estimated_reference_actions = physical.optimal_action_count
        metadata.optimal_action_count = physical.optimal_action_count
        metadata.guaranteed_policy_action_count = policy.optimal_worst_case_actions
        metadata.guaranteed_policy_witness = (
            policy.witness.model_dump(mode="json") if policy.witness is not None else {}
        )
        metadata.epistemic_probe_outcomes = epistemic_probe.outcome_count
        metadata.distractor_probe_outcomes = distractor_probe.outcome_count
        metadata.epistemic_probe_action_cost = (
            epistemic_probe.worst_case_total_actions or 0
        )
        metadata.distractor_probe_action_cost = (
            distractor_probe.worst_case_total_actions or 0
        )
        metadata.action_budget = action_budget
        metadata.exploration_allowance = exploration
        metadata.resource_allowance = allowance
        metadata.recommended_tool_call_limit = recommended_tool_call_limit(
            action_budget,
            len(profile.files),
        )
        metadata.solver_visited_states = physical.visited_states
        metadata.solver_max_frontier_size = physical.max_frontier_size

        if not qualify_result:
            return private
        from nexus.generator.qualify import qualify_episode

        if qualify_episode(private).passed:
            return private

    raise GenerationError(
        f"selective scenario family {family.family_id} was valid but no topology qualified in "
        f"{max_attempts} attempts for seed {seed} (discovery_level=4, "
        f"planning_level={planning_level})"
    )




def _constructed_goal(destination: str) -> GoalPredicate:
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
                value=MISSION_TARGET_VALUE,
            ),
        ),
    )


def _constructed_description(*, destination: str) -> str:
    return (
        "Transformation Facility. A1 is the mission payload; A2 and A3 are ordinary auxiliary "
        "samples. M1 is the mission machine and M2/M3 are calibration machines. Deliver A1 to "
        f"{destination} with value {MISSION_TARGET_VALUE}. The final facility phase is unrestricted. "
        "The supplied facility_manual.txt defines the complete generated law family. Probe and "
        "operate retain their ordinary NEXUS semantics. Infer an efficient information-acquisition "
        "policy, execute the mission transformation, and finish explicitly."
    )


def _generate_constructed_episode(
    seed: int,
    *,
    planning_level: int,
    max_attempts: int,
    verifier_secret: str | None,
    qualify_result: bool = True,
) -> PrivateEpisode:
    # D5 is constructive rather than rejection-sampled at the causal layer. The same named RNG
    # stream defines mechanics for every planning variant; only topology uses planning_level.
    mechanics_rng = rng_for(seed, "mechanics", "constructed-three-machine", 0)
    shapes = list(Shape)
    mechanics_rng.shuffle(shapes)
    mission_shape, diagnostic_shape, distractor_shape = shapes
    winning_phase = mechanics_rng.randrange(4)

    def artifact(artifact_id: str, shape: Shape) -> Artifact:
        return Artifact(
            id=artifact_id,
            location="@inventory",
            shape=shape,
            pattern=mechanics_rng.choice(tuple(Pattern)),
            orientation=mechanics_rng.choice(tuple(Orientation)),
            value=mechanics_rng.choice((0, 1, 2, 3, 4, 5, 6)),
            polarity=mechanics_rng.choice(tuple(Polarity)),
        )

    artifacts_template = {
        "A1": artifact("A1", mission_shape),
        "A2": artifact("A2", diagnostic_shape),
        "A3": artifact("A3", distractor_shape),
    }
    mission_rule = constructed_mission_rule(winning_phase, diagnostic_shape)
    constructor_rule = constant_value_rule(CONSTRUCTOR_VALUE)
    distractor_rule = constant_value_rule(DISTRACTOR_VALUE)
    candidate_rules_by_machine = {
        "M1": list(constructed_mission_rules(diagnostic_shape)),
        "M2": [constructor_rule],
        "M3": [distractor_rule],
    }
    family_id = scenario_family_id(seed, "constructed-three-machine", 0)

    # D5 co-locates its experiment-construction apparatus in R0. Planning difficulty continues to
    # vary the delivery topology independently instead of inventing discovery differences.
    min_rooms, max_rooms = room_bounds(planning_level, 1)
    for topology_attempt in range(max_attempts):
        topology_rng = rng_for(
            seed,
            "topology",
            "constructed-three-machine",
            0,
            planning_level,
            topology_attempt,
        )
        room_count = topology_rng.randint(min_rooms, max_rooms)
        rooms, edges = _random_tree(topology_rng, room_count)
        nexus_room, delivery_distance = _farthest_room(rooms, edges)

        initial_state = WorldState(
            phase=0,
            agent_room="R0",
            artifacts={
                artifact_id: item.model_copy(deep=True)
                for artifact_id, item in artifacts_template.items()
            },
            machines={
                "M1": Machine(id="M1", room_id="R0", uses_remaining=1),
                "M2": Machine(id="M2", room_id="R0", uses_remaining=1),
                "M3": Machine(id="M3", room_id="R0", uses_remaining=1),
            },
            resources=Resources(actions_remaining=GENERATION_SOLVER_BUDGET),
        )
        public = PublicEpisode(
            episode_id=hashlib.sha256(
                (
                    f"nexus-episode|{family_id}|d5|p{planning_level}|"
                    f"t{topology_attempt}"
                ).encode("utf-8")
            ).hexdigest()[:16],
            description=_constructed_description(destination=nexus_room),
            rooms=rooms,
            edges=edges,
            phase_modulus=4,
            initial_state=initial_state,
            goal=_constructed_goal(nexus_room),
            evidence_files={
                "facility_manual.txt": constructed_manual(diagnostic_shape),
            },
        )
        rules = {
            "mission-rule": mission_rule,
            "constructor-rule": constructor_rule,
            "distractor-rule": distractor_rule,
        }
        node_metrics = {
            "M1": rule_ast_metrics(mission_rule),
            "M2": rule_ast_metrics(constructor_rule),
            "M3": rule_ast_metrics(distractor_rule),
        }
        metadata = GenerationMetadata(
            generation_attempt=0,
            scenario_family_id=family_id,
            scenario_family_attempt=0,
            topology_attempt=topology_attempt,
            discovery_level=5,
            planning_level=planning_level,
            machine_count=3,
            room_count=room_count,
            graph_diameter=_graph_diameter(rooms, edges),
            candidate_rules_before_evidence=4,
            candidate_rules_after_evidence=4,
            evidence_candidate_counts={"M1": 4, "M2": 1, "M3": 1},
            evidence_rows=0,
            evidence_rows_by_machine={"M1": 0, "M2": 0, "M3": 0},
            mission_relevant_prediction_counts={"M1": 2, "M2": 1, "M3": 1},
            direct_target_example=False,
            required_probe_count=1,
            viable_causal_hypotheses=4,
            transformation_phases={"M1": winning_phase, "M2": 0, "M3": 0},
            epistemic_artifact_id="A2",
            distractor_artifact_id="A3",
            epistemic_machine_id="M2",
            distractor_machine_id="M3",
            estimated_reference_actions=delivery_distance + winning_phase + 3,
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
            machine_rules={
                "M1": "mission-rule",
                "M2": "constructor-rule",
                "M3": "distractor-rule",
            },
            verifier_secret=(
                verifier_secret if verifier_secret is not None else secrets.token_hex(32)
            ),
            construction_seed=seed,
            generation_metadata=metadata,
        )

        physical = solve_compressed_physical(private)
        if (
            not physical.solvable
            or physical.optimal_action_count is None
            or physical.optimal_action_count > MAX_PHYSICAL_OPTIMAL_ACTIONS
        ):
            continue

        policy_bound = min(
            GENERATION_SOLVER_BUDGET,
            physical.optimal_action_count + 16,
        )
        policy = solve_guaranteed_policy(
            private,
            candidate_rules_by_machine=candidate_rules_by_machine,
            max_actions=policy_bound,
            requested_action_values=(
                OperateAction(machine="M2", artifact="A2"),
                ProbeAction(machine="M1", artifact="A1"),
                OperateAction(machine="M3", artifact="A3"),
            ),
        )
        if (
            not policy.solvable
            or policy.viable_hypothesis_count != 4
            or policy.optimal_worst_case_actions is None
        ):
            continue

        constructor = _initial_operate_value(policy, "M2", "A2")
        direct_probe = _initial_probe_value(policy, "A1")
        distractor = _initial_operate_value(policy, "M3", "A3")
        if (
            constructor is None
            or constructor.worst_case_total_actions
            != policy.optimal_worst_case_actions
            or direct_probe is None
            or direct_probe.worst_case_total_actions is None
            or direct_probe.worst_case_total_actions
            <= policy.optimal_worst_case_actions
            or distractor is None
            or distractor.worst_case_total_actions is None
            or distractor.worst_case_total_actions
            <= policy.optimal_worst_case_actions
        ):
            continue

        constructed_artifact = apply_effect(constructor_rule, artifacts_template["A2"], 0)
        constructed_outputs = {
            artifact_projection(apply_effect(rule, constructed_artifact, 0))
            for rule in candidate_rules_by_machine["M1"]
        }
        if len(constructed_outputs) != 4:
            continue

        exploration = exploration_allowance(room_count)
        allowance = resource_allowance(room_count, 0)
        action_budget = policy.optimal_worst_case_actions + allowance
        private.public.initial_state.resources.actions_remaining = action_budget

        private.reference_plan = tuple(
            action.model_dump(mode="json") for action in physical.plan
        )
        metadata = private.generation_metadata
        metadata.estimated_reference_actions = physical.optimal_action_count
        metadata.optimal_action_count = physical.optimal_action_count
        metadata.guaranteed_policy_action_count = policy.optimal_worst_case_actions
        metadata.guaranteed_policy_witness = (
            policy.witness.model_dump(mode="json") if policy.witness is not None else {}
        )
        metadata.constructed_probe_outcomes = len(constructed_outputs)
        metadata.direct_probe_action_cost = direct_probe.worst_case_total_actions
        metadata.constructor_action_cost = constructor.worst_case_total_actions or 0
        metadata.distractor_action_cost = distractor.worst_case_total_actions or 0
        metadata.action_budget = action_budget
        metadata.exploration_allowance = exploration
        metadata.resource_allowance = allowance
        metadata.recommended_tool_call_limit = recommended_tool_call_limit(
            action_budget,
            len(public.evidence_files),
        )
        metadata.solver_visited_states = physical.visited_states
        metadata.solver_max_frontier_size = physical.max_frontier_size

        if not qualify_result:
            return private
        from nexus.generator.qualify import qualify_episode

        if qualify_episode(private).passed:
            return private

    raise GenerationError(
        f"constructed D5 scenario family {family_id} failed qualification in {max_attempts} "
        f"topology attempts for seed {seed} (planning_level={planning_level})"
    )



def _goal_location(goal: GoalPredicate, artifact_id: str) -> str | None:
    if (
        goal.kind == GoalKind.ARTIFACT_LOCATION
        and goal.artifact_id == artifact_id
        and isinstance(goal.value, str)
    ):
        return goal.value
    for child in goal.children:
        found = _goal_location(child, artifact_id)
        if found is not None:
            return found
    return None


def _candidate_rules_for_episode(episode: PrivateEpisode) -> dict[str, list[Effect]]:
    """Reconstruct the public causal hypothesis set for exact-policy qualification."""
    if episode.generation_metadata.discovery_level == 5:
        diagnostic_shape = episode.public.initial_state.artifacts["A2"].shape
        return {
            "M1": list(constructed_mission_rules(diagnostic_shape)),
            "M2": [constant_value_rule(CONSTRUCTOR_VALUE)],
            "M3": [constant_value_rule(DISTRACTOR_VALUE)],
        }

    if episode.generation_metadata.theory_level == 1:
        from nexus.generator.theory import theory_universe, validate_public_theory

        validate_public_theory(episode.public.evidence_files)
        return {
            machine: theory_universe().candidates(
                episode.public.evidence_files[measurement_filename(machine)],
                ceiling=12 if len(episode.machine_rules) == 2 else 32,
            )
            for machine in sorted(episode.machine_rules)
        }
    if episode.generation_metadata.theory_level == 3:
        from nexus.generator.structural import structural_belief
        return {"M1": structural_belief(episode).project(episode)[0]}
    if episode.generation_metadata.theory_level == 2:
        from nexus.generator.correction import read_correction_prior
        catalog = read_correction_prior(episode.public.evidence_files).hypotheses()
    else:
        catalog = enumerate_transformation_rules()
    result: dict[str, list[Effect]] = {}
    for machine_id in sorted(episode.machine_rules):
        evidence = episode.public.evidence_files.get(measurement_filename(machine_id))
        if evidence is None:
            raise GenerationError(f"missing public evidence for machine {machine_id}")
        result[machine_id] = candidates_matching_csv(evidence, catalog)
    return result


def _with_delivery_dependency(
    goal: GoalPredicate,
    artifact_id: str,
    destination: str,
) -> GoalPredicate:
    return GoalPredicate(
        kind=GoalKind.AND,
        children=(
            goal,
            GoalPredicate(
                kind=GoalKind.ARTIFACT_LOCATION,
                artifact_id=artifact_id,
                value=destination,
            ),
        ),
    )


def _add_planning_dependency(episode: PrivateEpisode) -> PrivateEpisode:
    """Compile P3 from the paired P2 world without changing mechanics or topology.

    The extra cargo duplicates an already available artifact context, so it cannot introduce a
    new causal experiment. Qualification still recomputes the exact guaranteed policy and accepts
    the P3 world only when its entire cost increase is attributable to the delivery dependency.
    """
    base = episode
    metadata = base.generation_metadata
    if metadata.planning_level != 2:
        raise GenerationError("P3 dependency compilation requires a P2 base episode")

    destination = _goal_location(base.public.goal, "A1")
    if destination is None:
        raise GenerationError("P3 requires an A1 delivery-location goal")

    artifacts = base.public.initial_state.artifacts
    if "A3" in artifacts:
        source = artifacts["A3"]
        dependency_id = "A4"
    else:
        source = artifacts["A1"]
        dependency_id = "A2"

    graph = nx.Graph()
    graph.add_nodes_from(base.public.rooms)
    graph.add_edges_from(base.public.edges)
    direct_distance = nx.shortest_path_length(graph, "R0", destination)
    candidate_rooms = [
        room_id for room_id in base.public.rooms if room_id != destination
    ]
    candidate_rooms.sort(
        key=lambda room_id: (
            nx.shortest_path_length(graph, "R0", room_id)
            + nx.shortest_path_length(graph, room_id, destination)
            - direct_distance,
            room_id,
        ),
        reverse=True,
    )

    base_physical = metadata.optimal_action_count
    base_guaranteed = metadata.guaranteed_policy_action_count
    candidate_rules = _candidate_rules_for_episode(base)

    for cargo_room in candidate_rooms:
        trial = base.model_copy(deep=True)
        cargo = source.model_copy(
            deep=True,
            update={"id": dependency_id, "location": cargo_room},
        )
        trial.public.initial_state.artifacts[dependency_id] = cargo
        trial.public.goal = _with_delivery_dependency(
            trial.public.goal,
            dependency_id,
            destination,
        )
        trial.public.description += (
            f" Planning dependency: also recover {dependency_id} and deliver it to "
            f"{destination} before finishing."
        )
        trial.public.episode_id = hashlib.sha256(
            f"{base.public.episode_id}|planning-p3|{cargo_room}".encode("utf-8")
        ).hexdigest()[:16]

        physical = solve_compressed_physical(trial)
        if not physical.solvable or physical.optimal_action_count is None:
            continue
        overhead = physical.optimal_action_count - base_physical
        if overhead < 2:
            continue

        needs_decision_values = metadata.discovery_level >= 4
        requested_action_values = None
        if metadata.discovery_level == 4:
            requested_action_values = (
                ProbeAction(machine="M1", artifact="A1"),
                ProbeAction(machine="M1", artifact="A2"),
                ProbeAction(machine="M1", artifact="A3"),
            )
        elif metadata.discovery_level == 5:
            requested_action_values = (
                OperateAction(machine="M2", artifact="A2"),
                ProbeAction(machine="M1", artifact="A1"),
                OperateAction(machine="M3", artifact="A3"),
            )
        policy_options = {
            "candidate_rules_by_machine": candidate_rules,
            "max_actions": min(GENERATION_SOLVER_BUDGET, base_guaranteed + overhead + 8),
            "include_action_values": needs_decision_values,
            "requested_action_values": requested_action_values,
        }
        if base_guaranteed + overhead > policy_options["max_actions"]:
            policy = solve_guaranteed_policy(trial, **policy_options)
        else:
            policy = solve_guaranteed_policy(
                trial, expected_actions=base_guaranteed + overhead, **policy_options
            )
            if not policy.solvable:
                # Preserve ordinary candidate rejection and exact diagnostic semantics.
                policy = solve_guaranteed_policy(trial, **policy_options)

        if (
            not policy.solvable
            or policy.optimal_worst_case_actions is None
            or policy.witness is None
            or policy.optimal_worst_case_actions != base_guaranteed + overhead
        ):
            continue

        if metadata.discovery_level == 4:
            epistemic_probe = _initial_probe_value(policy, "A2")
            distractor_probe = _initial_probe_value(policy, "A3")
            if (
                epistemic_probe is None
                or epistemic_probe.worst_case_total_actions is None
                or distractor_probe is None
                or distractor_probe.worst_case_total_actions is None
            ):
                continue
            trial.generation_metadata.epistemic_probe_outcomes = epistemic_probe.outcome_count
            trial.generation_metadata.distractor_probe_outcomes = distractor_probe.outcome_count
            trial.generation_metadata.epistemic_probe_action_cost = (
                epistemic_probe.worst_case_total_actions
            )
            trial.generation_metadata.distractor_probe_action_cost = (
                distractor_probe.worst_case_total_actions
            )
        elif metadata.discovery_level == 5:
            constructor = _initial_operate_value(policy, "M2", "A2")
            direct_probe = _initial_probe_value(policy, "A1")
            distractor = _initial_operate_value(policy, "M3", "A3")
            if (
                constructor is None
                or constructor.worst_case_total_actions is None
                or direct_probe is None
                or direct_probe.worst_case_total_actions is None
                or distractor is None
                or distractor.worst_case_total_actions is None
            ):
                continue
            trial.generation_metadata.constructor_action_cost = (
                constructor.worst_case_total_actions
            )
            trial.generation_metadata.direct_probe_action_cost = (
                direct_probe.worst_case_total_actions
            )
            trial.generation_metadata.distractor_action_cost = (
                distractor.worst_case_total_actions
            )

        trial.generation_metadata.planning_level = 3
        trial.generation_metadata.planning_dependency_artifact_id = dependency_id
        trial.generation_metadata.planning_dependency_action_cost = overhead
        trial.generation_metadata.optimal_action_count = physical.optimal_action_count
        trial.generation_metadata.estimated_reference_actions = physical.optimal_action_count
        trial.generation_metadata.guaranteed_policy_action_count = (
            policy.optimal_worst_case_actions
        )
        trial.generation_metadata.guaranteed_policy_witness = policy.witness.model_dump(
            mode="json"
        )
        trial.generation_metadata.solver_visited_states = physical.visited_states
        trial.generation_metadata.solver_max_frontier_size = physical.max_frontier_size

        allowance = resource_allowance(metadata.room_count, 0)
        trial.generation_metadata.resource_pressure = 0
        trial.generation_metadata.resource_allowance = allowance
        trial.generation_metadata.exploration_allowance = exploration_allowance(
            metadata.room_count
        )
        trial.generation_metadata.action_budget = (
            policy.optimal_worst_case_actions + allowance
        )
        trial.public.initial_state.resources.actions_remaining = (
            trial.generation_metadata.action_budget
        )
        trial.generation_metadata.recommended_tool_call_limit = recommended_tool_call_limit(
            trial.generation_metadata.action_budget,
            len(trial.public.evidence_files),
        )

        trial.reference_plan = tuple(
            action.model_dump(mode="json") for action in physical.plan
        )
        return trial

    raise GenerationError(
        f"unable to compile a mechanically isolated P3 dependency for "
        f"{base.public.episode_id}"
    )


def _apply_resource_pressure(
    episode: PrivateEpisode,
    resource_pressure: int,
) -> PrivateEpisode:
    # R0 is already the fully qualified default produced by every core generator. Returning the
    # same object avoids a deep copy and a redundant physical solve on the common path. R1/R2
    # change only the action allowance; generate_episode performs one final full qualification
    # after that budget-only transformation.
    if resource_pressure == 0:
        return episode

    trial = episode.model_copy(deep=True)
    metadata = trial.generation_metadata
    allowance = resource_allowance(metadata.room_count, resource_pressure)
    budget = metadata.guaranteed_policy_action_count + allowance
    if budget < metadata.optimal_action_count:
        raise GenerationError("resource-pressure budget falls below physical optimum")

    metadata.resource_pressure = resource_pressure
    metadata.resource_allowance = allowance
    metadata.action_budget = budget
    trial.public.initial_state.resources.actions_remaining = budget
    metadata.recommended_tool_call_limit = recommended_tool_call_limit(
        budget,
        len(trial.public.evidence_files),
    )
    trial.public.episode_id = hashlib.sha256(
        f"{trial.public.episode_id}|resource-r{resource_pressure}".encode("utf-8")
    ).hexdigest()[:16]

    # The existing physical reference plan remains valid because
    # optimal_action_count <= guaranteed_policy_action_count <= budget.
    return trial


def _generate_episode_core(
    seed: int,
    *,
    discovery_level: int = 0,
    planning_level: int = 1,
    max_attempts: int = 250,
    verifier_secret: str | None = None,
    qualify_result: bool = True,
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

    if discovery_level == 5:
        return _generate_constructed_episode(
            seed,
            planning_level=planning_level,
            max_attempts=max_attempts,
            verifier_secret=verifier_secret,
            qualify_result=qualify_result,
        )

    if discovery_level == 4:
        return _generate_selective_episode(
            seed,
            planning_level=planning_level,
            max_attempts=max_attempts,
            verifier_secret=verifier_secret,
            qualify_result=qualify_result,
        )

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

        solved = solve_compressed_physical(private)
        if not solved.solvable or solved.optimal_action_count is None:
            continue
        if solved.optimal_action_count > MAX_PHYSICAL_OPTIMAL_ACTIONS:
            continue

        operations = [
            action.machine for action in solved.plan if getattr(action, "type", None) == "operate"
        ]
        if machine_count == 2 and operations != ["M1", "M2"]:
            continue

        candidate_rules_by_machine = {
            machine_id: candidates_matching_csv(
                profile.files[measurement_filename(machine_id)],
                all_candidates,
            )
            for machine_id in machine_ids
        }
        policy = solve_guaranteed_policy(
            private,
            candidate_rules_by_machine=candidate_rules_by_machine,
            max_actions=GENERATION_SOLVER_BUDGET,
            include_action_values=False,
        )
        if (
            not policy.solvable
            or policy.optimal_worst_case_actions is None
            or policy.witness is None
        ):
            continue

        exploration = exploration_allowance(room_count)
        allowance = resource_allowance(room_count, 0)
        action_budget = policy.optimal_worst_case_actions + allowance
        private.public.initial_state.resources.actions_remaining = action_budget

        private.reference_plan = tuple(
            action.model_dump(mode="json") for action in solved.plan
        )
        private.generation_metadata.estimated_reference_actions = solved.optimal_action_count
        private.generation_metadata.optimal_action_count = solved.optimal_action_count
        private.generation_metadata.guaranteed_policy_action_count = (
            policy.optimal_worst_case_actions
        )
        private.generation_metadata.guaranteed_policy_witness = (
            policy.witness.model_dump(mode="json") if policy.witness is not None else {}
        )
        private.generation_metadata.action_budget = action_budget
        private.generation_metadata.exploration_allowance = exploration
        private.generation_metadata.resource_allowance = allowance
        private.generation_metadata.recommended_tool_call_limit = recommended_tool_call_limit(
            action_budget,
            len(profile.files),
        )
        private.generation_metadata.solver_visited_states = solved.visited_states
        private.generation_metadata.solver_max_frontier_size = solved.max_frontier_size

        if qualify_result:
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



@generation_diagnostics
def generate_episode(
    seed: int,
    *,
    discovery_level: int = 0,
    planning_level: int = 1,
    resource_pressure: int = 0,
    theory_level: int = 0,
    max_attempts: int = 250,
    verifier_secret: str | None = None,
    axis_version: int = 1,
    science_family: str = "shared-response-v1",
    budget_profile: str = "standard",
    presentation_version: PresentationVersion | None = CURRENT,
    ontology_options: dict | None = None,
) -> PrivateEpisode:
    """Generate a deterministic, solver-qualified NEXUS episode.

    P3 is compiled from the paired P2 topology by adding a mechanically isolated delivery
    dependency. Resource pressure changes only the action allowance above the exact guaranteed
    policy cost.
    """
    from nexus.ontology.catalog import BUILTINS
    if ontology_options is not None and not isinstance(ontology_options, dict):
        raise ValueError("ontology options must be a JSON object")
    if budget_profile not in ("standard", "diagnostic-plus6"):
        raise ValueError("unknown budget profile")
    budget_families = {name for name, definition in BUILTINS.items() if definition.diagnostic_budget}
    if budget_profile != "standard" and science_family not in budget_families:
        raise ValueError("diagnostic budget profile is unsupported by this family")
    if presentation_version not in (None, CURRENT):
        raise ValueError("unsupported presentation version")
    if science_family not in BUILTINS:
        raise ValueError("unknown scientific family")
    if science_family != "shared-response-v1" and axis_version != 2:
        raise ValueError(f"{science_family} requires axis_version=2")
    if axis_version == 2:
        episode = BUILTINS[science_family].generate(
            seed, discovery_level=discovery_level, planning_level=planning_level,
            resource_pressure=resource_pressure, theory_level=theory_level,
            verifier_secret=verifier_secret,
            ontology_options=ontology_options,
            **({"budget_profile": budget_profile} if science_family in budget_families else {}),
        )
        return attach(episode, presentation_version)
    if axis_version != 1:
        raise ValueError("axis_version must be 1 (legacy) or 2 (scientific)")
    if ontology_options:
        raise ValueError("ontology options require axes v2")
    from nexus.generator.theory import validate_theory_profile

    validate_theory_profile(theory_level, discovery_level)
    validate_difficulty_levels(discovery_level, planning_level, resource_pressure)
    core_planning = 2 if planning_level == 3 else planning_level
    with timed_stage("generation.core"):
        if theory_level == 3:
            from nexus.generator.structural_generation import generate_structural_episode
            episode = generate_structural_episode(
                seed, planning_level=core_planning, max_attempts=max_attempts,
                verifier_secret=verifier_secret,
            )
        elif theory_level == 2:
            from nexus.generator.correction_generation import generate_correction_episode
            episode = generate_correction_episode(
                seed, planning_level=core_planning, max_attempts=max_attempts,
                verifier_secret=verifier_secret,
            )
        else:
            episode = _generate_episode_core(
                seed,
                discovery_level=discovery_level,
                planning_level=core_planning,
                max_attempts=max_attempts,
                verifier_secret=verifier_secret,
                qualify_result=planning_level != 3,
            )
    transformed = planning_level == 3 or resource_pressure != 0 or theory_level != 0
    if planning_level == 3:
        with timed_stage("generation.planning_dependency"):
            episode = _add_planning_dependency(episode)
    if theory_level == 1:
        from nexus.generator.theory_generation import compile_theory

        with timed_stage("generation.theory"):
            try:
                episode = compile_theory(episode)
            except EvidencePlanningError as exc:
                raise GenerationError(str(exc)) from exc
    with timed_stage("generation.resource_pressure"):
        episode = _apply_resource_pressure(episode, resource_pressure)

    # Core P0-P2/R0 generators already perform complete qualification before returning. Only
    # post-generation P3 or R1/R2 transformations need another full qualification pass.
    if transformed:
        from nexus.generator.qualify import qualify_episode

        with timed_stage("generation.qualification"):
            report = qualify_episode(episode)
        if not report.passed:
            raise GenerationError(
                "generated episode failed final profile qualification: "
                + ", ".join(name for name, passed in report.checks.items() if not passed)
            )
    return attach(episode, presentation_version)
