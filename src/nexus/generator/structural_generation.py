"""Compile missing operator relationships with an exact reachable-context quotient."""

import secrets
from itertools import product

from nexus.diagnostics import timed_stage
from nexus.engine.canonical import canonical_hash
from nexus.engine.rules import apply_effect
from nexus.generator.structural import CELLS, FAMILY, OPERATIONS, StructuralPrior, operation_effect, structural_belief
from nexus.generator.difficulty import (
    GENERATION_SOLVER_BUDGET, MAX_PHYSICAL_OPTIMAL_ACTIONS, exploration_allowance,
    recommended_tool_call_limit, resource_allowance, room_bounds,
)
from nexus.generator.discovery import analyze_discovery
from nexus.generator.evidence import Experiment, evidence_csv
from nexus.generator.randomness import rng_for, scenario_family_id
from nexus.generator.rules import rule_ast_metrics
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import (
    Artifact, Machine, Orientation, Pattern, Polarity, Resources, Shape, WorldState,
)
from nexus.solver.belief import solve_compressed_physical, solve_guaranteed_policy


def generate_structural_episode(seed: int, *, planning_level: int, max_attempts: int,
                                verifier_secret: str | None) -> PrivateEpisode:
    from nexus.generator.generator import GenerationError, _graph_diameter, _random_tree, _role_rooms

    if verifier_secret == "" or max_attempts < 1:
        raise ValueError("verifier_secret must not be empty; max_attempts must be at least 1")
    with timed_stage("structural.family"):
        rng = rng_for(seed, "t3-structural-mechanics-v1")
        spec = StructuralPrior()
        initial = Artifact(id="A1", location="@inventory", shape=rng.choice(tuple(Shape)),
                           pattern=rng.choice(tuple(Pattern)), value=rng.choice(tuple(range(3, 9))),
                           orientation=rng.choice(tuple(Orientation)),
                           polarity=rng.choice(tuple(Polarity)))
        target_op = rng.choice(OPERATIONS)
        target_value = apply_effect(operation_effect(target_op), initial, 0).value
        choices = [rng.choice(domain) for domain in spec.domains]
        relevant = [i for i, (shape, _) in enumerate(CELLS) if shape == initial.shape]
        viable = [pair for pair in product(OPERATIONS, repeat=2) if target_op in pair]
        for index, op in zip(relevant, rng.choice(viable), strict=True):
            choices[index] = op
        rule = spec.law(tuple(choices))
        phase = next(p for p in range(4) if apply_effect(rule, initial, p).value == target_value)
        target = apply_effect(rule, initial, phase)
        calibration = initial.model_copy(update={
            "shape": next(shape for shape in Shape if shape != initial.shape), "value": 4,
        })
        files = {"facility_manual.txt": spec.manual(), "theory.json": spec.public_json(),
                 "measurements.csv": evidence_csv(rule, (Experiment(phase=0, artifact=calibration),))}
        nodes, depth = rule_ast_metrics(rule)
        family = scenario_family_id(seed, FAMILY, 0)

    for attempt in range(max_attempts):
        with timed_stage("structural.topology"):
            topology = rng_for(seed, "t3-structural-topology-v1", planning_level, attempt)
            rooms, edges = _random_tree(topology, topology.randint(*room_bounds(planning_level, 1)))
            artifact_room, machine_rooms, destination, _ = _role_rooms(rooms, edges, machine_count=1)
            item = initial.model_copy(update={"location": artifact_room})
            goal = GoalPredicate(kind=GoalKind.AND, children=(
                GoalPredicate(kind=GoalKind.ARTIFACT_FIELD, artifact_id="A1", field="value",
                              value=target_value),
                GoalPredicate(kind=GoalKind.ARTIFACT_LOCATION, artifact_id="A1", value=destination),
            ))
            metadata = GenerationMetadata(
                theory_level=3, discovery_level=2, planning_level=planning_level,
                scenario_family_id=family, topology_attempt=attempt,
                machine_count=1, room_count=len(rooms), graph_diameter=_graph_diameter(rooms, edges),
                candidate_rules_before_evidence=729, candidate_rules_after_evidence=9,
                evidence_candidate_counts={"M1": 9}, evidence_rows=1,
                evidence_rows_by_machine={"M1": 1},
                mission_relevant_prediction_counts={"M1": 3},
                required_probe_count=1, viable_causal_hypotheses=5, transformation_phases={"M1": phase},
                rule_ast_nodes=nodes, rule_ast_depth=depth,
                rule_ast_nodes_by_machine={"M1": nodes}, rule_ast_depth_by_machine={"M1": depth},
            )
            world = PrivateEpisode(
                public=PublicEpisode(
                    episode_id=canonical_hash([family, planning_level, attempt])[:16],
                    description=f"Discover the missing relationship. Deliver A1 with value {target_value} to {destination}, then finish.",
                    rooms=rooms, edges=edges, goal=goal, evidence_files=files,
                    initial_state=WorldState(agent_room="R0", phase=0, artifacts={"A1": item},
                        machines={"M1": Machine(id="M1", room_id=machine_rooms[0], uses_remaining=1)},
                        resources=Resources(actions_remaining=GENERATION_SOLVER_BUDGET)),
                ), rules={"law": rule}, machine_rules={"M1": "law"}, construction_seed=seed,
                verifier_secret=verifier_secret if verifier_secret is not None else secrets.token_hex(32),
                generation_metadata=metadata,
            )
        with timed_stage("structural.projection") as metrics:
            belief = structural_belief(world)
            candidates, multiplicity = belief.project(world)
            metrics.update(full_prior=spec.cardinality, after_evidence=belief.cardinality,
                           reachable_classes=len(candidates), multiplicity=multiplicity)
            analysis = analyze_discovery(candidate_rules_by_machine={"M1": candidates},
                                         initial_artifact=item, target_artifact=target, phase_modulus=4)
            if analysis.minimum_guaranteed_probes != 1 or analysis.viable_hypothesis_count != 5:
                raise GenerationError("T3 failed its discovery proof")
        with timed_stage("structural.physical"):
            physical = solve_compressed_physical(world)
        if physical.exhausted_state_limit:
            raise GenerationError("T3 physical search exhausted its proof bound")
        if not physical.solvable or physical.optimal_action_count > MAX_PHYSICAL_OPTIMAL_ACTIONS:
            continue
        with timed_stage("structural.policy"):
            policy = solve_guaranteed_policy(world, candidate_rules_by_machine={"M1": candidates},
                                            max_actions=GENERATION_SOLVER_BUDGET,
                                            include_action_values=False)
        if not policy.solvable or policy.witness is None or policy.optimal_worst_case_actions is None:
            raise GenerationError("T3 has no certified guaranteed policy within the proof bound")
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
    raise GenerationError("T3 exhausted topology attempts without changing the selected mechanics")
