from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

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

    protocol_version: str = "nexus-0.1"
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

    @classmethod
    def from_episode(cls, episode: PublicEpisode) -> "PlayerManifest":
        return cls(
            protocol_version=episode.protocol_version,
            episode_id=episode.episode_id,
            description=episode.description,
            goal=episode.goal,
            evidence_files=tuple(sorted(episode.evidence_files)),
        )


class PrivateEpisode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    public: PublicEpisode
    rules: dict[str, Effect]
    machine_rules: dict[str, str]
    verifier_secret: str
    construction_seed: int | None = None
    reference_plan: tuple[dict, ...] = ()
    generation_metadata: dict[str, int | str | bool] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_private_links(self) -> "PrivateEpisode":
        for machine_id, rule_id in self.machine_rules.items():
            if machine_id not in self.public.initial_state.machines:
                raise ValueError(f"machine rule references unknown machine {machine_id}")
            if rule_id not in self.rules:
                raise ValueError(f"machine {machine_id} references unknown rule {rule_id}")
        return self
