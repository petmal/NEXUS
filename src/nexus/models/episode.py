from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from nexus.models.actions import action_contract
from nexus.models.goals import GoalPredicate
from nexus.models.rules import Effect
from nexus.models.world import Room, WorldState


class PublicEpisode(BaseModel):
    """Non-secret compiled episode data used by the trusted runner.

    This model intentionally contains canonical initial state and is therefore
    not the player-facing manifest. Use PlayerManifest for data safe to hand to
    an evaluated agent.
    """

    model_config = ConfigDict(extra="forbid")

    protocol_version: str = "nexus-0.2"
    episode_id: str
    description: str
    rooms: dict[str, Room]
    edges: tuple[tuple[str, str], ...]
    phase_modulus: int = Field(default=4, ge=1)
    initial_state: WorldState
    goal: GoalPredicate
    evidence_files: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_world(self) -> "PublicEpisode":
        if self.initial_state.agent_room not in self.rooms:
            raise ValueError("agent starts in unknown room")
        for left, right in self.edges:
            if left not in self.rooms or right not in self.rooms or left == right:
                raise ValueError(f"invalid edge {(left, right)!r}")
        room_ids = set(self.rooms)
        for artifact in self.initial_state.artifacts.values():
            if artifact.location != "@inventory" and artifact.location not in room_ids:
                raise ValueError(f"artifact {artifact.id} has unknown location")
        for machine in self.initial_state.machines.values():
            if machine.room_id not in room_ids:
                raise ValueError(f"machine {machine.id} has unknown room")
        return self


class PlayerManifest(BaseModel):
    """Player-safe episode metadata. Contains no canonical world state or latent rules."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    protocol_version: str
    episode_id: str
    description: str
    goal: GoalPredicate
    evidence_files: tuple[str, ...] = ()
    action_contract: dict = Field(default_factory=dict)

    @classmethod
    def from_episode(cls, episode: PublicEpisode) -> "PlayerManifest":
        return cls(
            protocol_version=episode.protocol_version,
            episode_id=episode.episode_id,
            description=episode.description,
            goal=episode.goal,
            evidence_files=tuple(sorted(episode.evidence_files)),
            action_contract=action_contract(),
        )


class GenerationMetadata(BaseModel):
    """Trusted operator metadata produced and mechanically checked during generation."""

    model_config = ConfigDict(extra="forbid")

    # generation_attempt is retained for compatibility and mirrors scenario_family_attempt.
    generation_attempt: int = 0
    scenario_family_id: str = ""
    scenario_family_attempt: int = 0
    topology_attempt: int = 0

    discovery_level: int = 0
    planning_level: int = 1
    machine_count: int = 1
    room_count: int = 0
    graph_diameter: int = 0

    candidate_rules_before_evidence: int = 0
    candidate_rules_after_evidence: int = 0
    evidence_candidate_counts: dict[str, int] = Field(default_factory=dict)
    evidence_rows: int = 0
    evidence_rows_by_machine: dict[str, int] = Field(default_factory=dict)
    mission_relevant_prediction_counts: dict[str, int] = Field(default_factory=dict)
    direct_target_example: bool = False
    required_probe_count: int = 0
    viable_causal_hypotheses: int = 0

    transformation_phases: dict[str, int] = Field(default_factory=dict)
    requires_both_machines: bool = False
    reverse_order_reaches_goal: bool = False

    epistemic_artifact_id: str | None = None
    distractor_artifact_id: str | None = None
    epistemic_machine_id: str | None = None
    distractor_machine_id: str | None = None
    epistemic_probe_outcomes: int = 0
    distractor_probe_outcomes: int = 0
    epistemic_probe_action_cost: int = 0
    distractor_probe_action_cost: int = 0
    constructed_probe_outcomes: int = 0
    direct_probe_action_cost: int = 0
    constructor_action_cost: int = 0
    distractor_action_cost: int = 0

    estimated_reference_actions: int = 0
    optimal_action_count: int = 0
    guaranteed_policy_action_count: int = 0
    action_budget: int = 0
    exploration_allowance: int = 0
    recommended_tool_call_limit: int = 0

    rule_ast_nodes: int = 0
    rule_ast_depth: int = 0
    rule_ast_nodes_by_machine: dict[str, int] = Field(default_factory=dict)
    rule_ast_depth_by_machine: dict[str, int] = Field(default_factory=dict)

    solver_visited_states: int = 0
    solver_max_frontier_size: int = 0


class PrivateEpisode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    public: PublicEpisode
    rules: dict[str, Effect]
    machine_rules: dict[str, str]
    verifier_secret: str
    construction_seed: int | None = None
    reference_plan: tuple[dict, ...] = ()
    generation_metadata: GenerationMetadata = Field(default_factory=GenerationMetadata)

    @model_validator(mode="after")
    def validate_private_links(self) -> "PrivateEpisode":
        for machine_id, rule_id in self.machine_rules.items():
            if machine_id not in self.public.initial_state.machines:
                raise ValueError(f"machine rule references unknown machine {machine_id}")
            if rule_id not in self.rules:
                raise ValueError(f"machine {machine_id} references unknown rule {rule_id}")
        return self
