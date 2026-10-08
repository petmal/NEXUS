"""Compile the bounded correction family using the ordinary engine and exact solver."""

import secrets

from nexus.diagnostics import timed_stage
from nexus.engine.canonical import canonical_hash
from nexus.engine.rules import apply_effect
from nexus.generator.correction import CorrectionPrior
from nexus.generator.difficulty import (
    GENERATION_SOLVER_BUDGET, MAX_PHYSICAL_OPTIMAL_ACTIONS, exploration_allowance,
    recommended_tool_call_limit, resource_allowance, room_bounds,
)
from nexus.generator.discovery import analyze_discovery
from nexus.generator.evidence import Experiment, evidence_csv, mission_prediction_count
from nexus.generator.randomness import rng_for, scenario_family_id
from nexus.generator.rules import rule_ast_metrics
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import (
    Artifact, Machine, Orientation, Pattern, Polarity, Resources, Shape, WorldState,
)
from nexus.solver.belief import solve_compressed_physical, solve_guaranteed_policy


def generate_correction_episode(seed: int, *, planning_level: int, max_attempts: int,
                                verifier_secret: str | None) -> PrivateEpisode:
    from nexus.generator.generator import GenerationError, _graph_diameter, _random_tree, _role_rooms

    if verifier_secret == "" or max_attempts < 1:
        raise ValueError("verifier_secret must not be empty; max_attempts must be at least 1")
    with timed_stage("correction.family"):
        rng = rng_for(seed, "t2-correction-mechanics-v1")
        spec = CorrectionPrior(effective_add=rng.choice((1, 2, 3)))
        initial = Artifact(id="A1", location="@inventory", shape=rng.choice(tuple(Shape)),
                           pattern=rng.choice(tuple(Pattern)), value=rng.randrange(11),
                           orientation=rng.choice(tuple(Orientation)),
                           polarity=rng.choice(tuple(Polarity)))
        target_value = (initial.value + spec.effective_add + 1) % spec.modulus
        candidates = spec.hypotheses()
        # One use: exactly the laws with correction 1 in at least one odd phase are viable.
        viable = [law for law in candidates if any(
            apply_effect(law, initial, phase).value == target_value for phase in range(4)
        )]
        rule = rng.choice(viable)
        phase = next(p for p in range(4) if apply_effect(rule, initial, p).value == target_value)
        target = apply_effect(rule, initial, phase)
        analysis = analyze_discovery(candidate_rules_by_machine={"M1": candidates},
                                     initial_artifact=initial, target_artifact=target,
                                     phase_modulus=4)
        if analysis.minimum_guaranteed_probes != 1 or analysis.viable_hypothesis_count != 5:
            raise GenerationError("T2 correction family failed its discovery proof")
        files = {"facility_manual.txt": spec.manual(), "theory.json": spec.public_json(),
                 "measurements.csv": evidence_csv(rule, tuple(
                     Experiment(phase=p, artifact=initial) for p in spec.validity_phases
                 ))}
        nodes, depth = rule_ast_metrics(rule)
        family = scenario_family_id(seed, spec.family, 0)

    for attempt in range(max_attempts):
        with timed_stage("correction.topology"):
            topology = rng_for(seed, "t2-correction-topology-v1", planning_level, attempt)
            rooms, edges = _random_tree(topology, topology.randint(*room_bounds(planning_level, 1)))
            artifact_room, machine_rooms, destination, _ = _role_rooms(rooms, edges, machine_count=1)
            item = initial.model_copy(update={"location": artifact_room})
            goal = GoalPredicate(kind=GoalKind.AND, children=(
                GoalPredicate(kind=GoalKind.ARTIFACT_FIELD, artifact_id="A1", field="value",
                              value=target_value),
                GoalPredicate(kind=GoalKind.ARTIFACT_LOCATION, artifact_id="A1", value=destination),
            ))
            metadata = GenerationMetadata(
                theory_level=2, discovery_level=2, planning_level=planning_level,
                scenario_family_id=family, topology_attempt=attempt,
                machine_count=1, room_count=len(rooms), graph_diameter=_graph_diameter(rooms, edges),
                candidate_rules_before_evidence=9, candidate_rules_after_evidence=9,
                evidence_candidate_counts={"M1": 9}, evidence_rows=2,
                evidence_rows_by_machine={"M1": 2},
                mission_relevant_prediction_counts={"M1": mission_prediction_count(candidates, item, phase)},
                required_probe_count=1, viable_causal_hypotheses=5, transformation_phases={"M1": phase},
                rule_ast_nodes=nodes, rule_ast_depth=depth,
                rule_ast_nodes_by_machine={"M1": nodes}, rule_ast_depth_by_machine={"M1": depth},
            )
            world = PrivateEpisode(
                public=PublicEpisode(
                    episode_id=canonical_hash([family, planning_level, attempt])[:16],
                    description=f"Refine the effective theory. Deliver A1 with value {target_value} to {destination}, then finish.",
                    rooms=rooms, edges=edges, goal=goal, evidence_files=files,
                    initial_state=WorldState(agent_room="R0", phase=0, artifacts={"A1": item},
                        machines={"M1": Machine(id="M1", room_id=machine_rooms[0], uses_remaining=1)},
                        resources=Resources(actions_remaining=GENERATION_SOLVER_BUDGET)),
                ), rules={"law": rule}, machine_rules={"M1": "law"}, construction_seed=seed,
                verifier_secret=verifier_secret if verifier_secret is not None else secrets.token_hex(32),
                generation_metadata=metadata,
            )
        with timed_stage("correction.physical"):
            physical = solve_compressed_physical(world)
        if physical.exhausted_state_limit:
            raise GenerationError("T2 physical search exhausted its proof bound")
        if not physical.solvable or physical.optimal_action_count > MAX_PHYSICAL_OPTIMAL_ACTIONS:
            continue
        with timed_stage("correction.policy"):
            policy = solve_guaranteed_policy(world, candidate_rules_by_machine={"M1": candidates},
                                            max_actions=GENERATION_SOLVER_BUDGET,
                                            include_action_values=False)
        if not policy.solvable or policy.witness is None or policy.optimal_worst_case_actions is None:
            raise GenerationError("T2 has no certified guaranteed policy within the proof bound")
        metadata.optimal_action_count = metadata.estimated_reference_actions = physical.optimal_action_count
        metadata.guaranteed_policy_action_count = policy.optimal_worst_case_actions
        metadata.guaranteed_policy_witness = policy.witness.model_dump(mode="json")
        metadata.exploration_allowance = exploration_allowance(len(rooms))
        metadata.resource_allowance = resource_allowance(len(rooms), 0)
        metadata.action_budget = policy.optimal_worst_case_actions + metadata.resource_allowance
        metadata.recommended_tool_call_limit = recommended_tool_call_limit(metadata.action_budget, len(files))
        metadata.solver_visited_states = physical.visited_states
        metadata.solver_max_frontier_size = physical.max_frontier_size
        world.public.initial_state.resources.actions_remaining = metadata.action_budget
        world.reference_plan = tuple(a.model_dump(mode="json") for a in physical.plan)
        return world
    raise GenerationError("T2 exhausted topology attempts without changing the selected mechanics")
