from __future__ import annotations

import hashlib
import random
import secrets

import networkx as nx

from nexus.engine.rules import apply_effect
from nexus.generator.evidence import choose_discriminating_evidence, evidence_csv
from nexus.generator.manual import FACILITY_MANUAL
from nexus.generator.rules import (
    enumerate_transformation_rules,
    rule_ast_metrics,
    sample_transformation_rule,
)
from nexus.models.episode import PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
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


def _random_tree(rng: random.Random, count: int) -> tuple[dict[str, Room], tuple[tuple[str, str], ...]]:
    ids = [f"R{i}" for i in range(count)]
    edges: list[tuple[str, str]] = []
    for index in range(1, count):
        edges.append((ids[index], ids[rng.randrange(index)]))
    rooms = {room_id: Room(id=room_id, label=f"Chamber {room_id[1:]}") for room_id in ids}
    return rooms, tuple(edges)


def _role_rooms(
    rooms: dict[str, Room], edges: tuple[tuple[str, str], ...]
) -> tuple[str, str, str, int]:
    graph = nx.Graph()
    graph.add_nodes_from(rooms)
    graph.add_edges_from(edges)
    start = "R0"
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    best: tuple[int, str, str, str] | None = None
    for artifact_room in rooms:
        if artifact_room == start:
            continue
        for machine_room in rooms:
            if machine_room in {start, artifact_room}:
                continue
            for nexus_room in rooms:
                if nexus_room in {start, artifact_room, machine_room}:
                    continue
                score = (
                    distances[start][artifact_room]
                    + distances[artifact_room][machine_room]
                    + distances[machine_room][nexus_room]
                )
                candidate = (score, artifact_room, machine_room, nexus_room)
                if best is None or candidate > best:
                    best = candidate
    if best is None:
        raise GenerationError("unable to assign distinct role rooms")
    distance_sum, artifact_room, machine_room, nexus_room = best
    return artifact_room, machine_room, nexus_room, distance_sum


def generate_episode(
    seed: int,
    *,
    min_optimal_actions: int = 8,
    max_optimal_actions: int = 15,
    max_attempts: int = 100,
) -> PrivateEpisode:
    all_candidates = enumerate_transformation_rules()

    for attempt in range(max_attempts):
        rng = random.Random((seed << 16) ^ attempt)
        room_count = rng.randint(5, 7)
        rooms, edges = _random_tree(rng, room_count)
        artifact_room, machine_room, nexus_room, distance_sum = _role_rooms(rooms, edges)

        # Sample grammar components independently. The complete law is composed for
        # this episode rather than selected from a hand-authored list of full rules.
        rule = sample_transformation_rule(rng)
        experiments, remaining = choose_discriminating_evidence(rule, all_candidates)
        if len(remaining) != 1 or remaining[0] != rule:
            continue

        initial_artifact = Artifact(
            id="A1",
            location=artifact_room,
            shape=rng.choice(tuple(Shape)),
            pattern=rng.choice(tuple(Pattern)),
            orientation=rng.choice(tuple(Orientation)),
            value=rng.randint(0, 10),
            polarity=rng.choice(tuple(Polarity)),
        )
        target_phase = rng.choice((0, 1))
        transformed = apply_effect(rule, initial_artifact, target_phase)
        if (
            transformed.value == initial_artifact.value
            and transformed.polarity == initial_artifact.polarity
            and transformed.orientation == initial_artifact.orientation
        ):
            continue

        goal = GoalPredicate(
            kind=GoalKind.AND,
            children=(
                GoalPredicate(
                    kind=GoalKind.ARTIFACT_LOCATION,
                    artifact_id="A1",
                    value=nexus_room,
                ),
                GoalPredicate(
                    kind=GoalKind.ARTIFACT_FIELD,
                    artifact_id="A1",
                    field="value",
                    value=transformed.value,
                ),
                GoalPredicate(
                    kind=GoalKind.ARTIFACT_FIELD,
                    artifact_id="A1",
                    field="polarity",
                    value=transformed.polarity.value,
                ),
                GoalPredicate(
                    kind=GoalKind.ARTIFACT_FIELD,
                    artifact_id="A1",
                    field="orientation",
                    value=transformed.orientation.value,
                ),
                GoalPredicate(kind=GoalKind.PHASE_EQUALS, value=target_phase),
            ),
        )

        estimated = distance_sum + 4 + target_phase
        budget = max(estimated + 3, max_optimal_actions + 1)
        initial_state = WorldState(
            phase=0,
            agent_room="R0",
            artifacts={"A1": initial_artifact},
            machines={"M1": Machine(id="M1", room_id=machine_room, uses_remaining=1)},
            resources=Resources(actions_remaining=budget),
        )
        evidence = evidence_csv(rule, experiments)
        episode_id = hashlib.sha256(
            f"nexus|{seed}|{attempt}|{rng.getrandbits(128)}".encode()
        ).hexdigest()[:16]
        description = (
            "Transformation Facility. Recover artifact A1, use the unknown machine M1 as needed, "
            f"and deliver A1 to {nexus_room}. The final artifact must have value {transformed.value}, "
            f"polarity {transformed.polarity.value}, orientation {transformed.orientation.value}, "
            f"while the facility phase is {target_phase}. The phase advances only when you wait. "
            "The supplied facility_manual.txt defines the possible machine-law grammar, while "
            "measurements.csv contains prior experiments performed on M1. Infer the selected "
            "law well enough to complete the mission, then finish explicitly."
        )
        public = PublicEpisode(
            episode_id=episode_id,
            description=description,
            rooms=rooms,
            edges=edges,
            phase_modulus=4,
            initial_state=initial_state,
            goal=goal,
            evidence_files={
                "facility_manual.txt": FACILITY_MANUAL,
                "measurements.csv": evidence,
            },
        )
        rule_nodes, rule_depth = rule_ast_metrics(rule)
        private = PrivateEpisode(
            public=public,
            rules={"machine-rule": rule},
            machine_rules={"M1": "machine-rule"},
            verifier_secret=secrets.token_hex(32),
            construction_seed=seed,
            generation_metadata={
                "generation_attempt": attempt,
                "candidate_rules_before_evidence": len(all_candidates),
                "candidate_rules_after_evidence": len(remaining),
                "evidence_rows": len(experiments),
                "estimated_reference_actions": estimated,
                "rule_ast_nodes": rule_nodes,
                "rule_ast_depth": rule_depth,
            },
        )
        solved = solve(private)
        if not solved.solvable or solved.optimal_action_count is None:
            continue
        if not (min_optimal_actions <= solved.optimal_action_count <= max_optimal_actions):
            continue
        private.reference_plan = tuple(action.model_dump(mode="json") for action in solved.plan)
        private.generation_metadata.update(
            {
                "optimal_action_count": solved.optimal_action_count,
                "solver_visited_states": solved.visited_states,
                "solver_max_frontier_size": solved.max_frontier_size,
            }
        )
        return private

    raise GenerationError(
        f"failed to generate a qualified episode in {max_attempts} attempts for seed {seed}"
    )
