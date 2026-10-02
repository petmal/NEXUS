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
from nexus.models.actions import ProbeAction
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
from nexus.solver.belief import solve_guaranteed_policy
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
def _find_selective_family(seed: int, max_attempts: int) -> _SelectiveMechanicsFamily:
    all_candidates = enumerate_transformation_rules()

    for family_attempt in range(max_attempts):
        rng = rng_for(seed, "mechanics", "selective-one-machine", family_attempt)
        selected_rule = sample_transformation_rule(rng)
        initial_artifact = Artifact(
            id="A1",
            location="@inventory",
            shape=Shape.SQUARE,
            pattern=Pattern.PLAIN,
            orientation=rng.choice((Orientation.NORTH, Orientation.EAST)),
            value=rng.choice((0, 1, 2, 4, 7)),
            polarity=rng.choice(tuple(Polarity)),
        )
        target_phase = rng.choice((0, 1))
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

        epistemic_samples = _shape_probe_samples(Shape.CIRCLE)
        distractor_samples = _shape_probe_samples(Shape.TRIANGLE)
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

        physical = solve(private)
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

        allowance = exploration_allowance(room_count)
        action_budget = policy.optimal_worst_case_actions + allowance + EXECUTION_SLACK
        private.public.initial_state.resources.actions_remaining = action_budget

        final_solve = solve(private)
        if (
            not final_solve.solvable
            or final_solve.optimal_action_count != physical.optimal_action_count
        ):
            continue

        private.reference_plan = tuple(
            action.model_dump(mode="json") for action in final_solve.plan
        )
        metadata = private.generation_metadata
        metadata.estimated_reference_actions = final_solve.optimal_action_count
        metadata.optimal_action_count = final_solve.optimal_action_count
        metadata.guaranteed_policy_action_count = policy.optimal_worst_case_actions
        metadata.epistemic_probe_outcomes = epistemic_probe.outcome_count
        metadata.distractor_probe_outcomes = distractor_probe.outcome_count
        metadata.epistemic_probe_action_cost = (
            epistemic_probe.worst_case_total_actions or 0
        )
        metadata.distractor_probe_action_cost = (
            distractor_probe.worst_case_total_actions or 0
        )
        metadata.action_budget = action_budget
        metadata.exploration_allowance = allowance
        metadata.recommended_tool_call_limit = recommended_tool_call_limit(
            action_budget,
            len(profile.files),
        )
        metadata.solver_visited_states = final_solve.visited_states
        metadata.solver_max_frontier_size = final_solve.max_frontier_size

        from nexus.generator.qualify import qualify_episode

        if qualify_episode(private).passed:
            return private

    raise GenerationError(
        f"selective scenario family {family.family_id} was valid but no topology qualified in "
        f"{max_attempts} attempts for seed {seed} (discovery_level=4, "
        f"planning_level={planning_level})"
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

    if discovery_level == 4:
        return _generate_selective_episode(
            seed,
            planning_level=planning_level,
            max_attempts=max_attempts,
            verifier_secret=verifier_secret,
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
