"""Small structural contracts for trusted ontology implementations.

An adapter is stateless. Only configure/assess_mission may mutate the engine's
private working copy. No adapter owns turns, resource consumption or receipts.
Public projections accept no private episode. Inference sees observations, never
selected truth. New domains keep payload validation in data-only schema modules.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from nexus.ontology.inference import Belief, Measurement

if TYPE_CHECKING:
    from nexus.models.actions import Action, ConfigureAction
    from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainStock
    from nexus.models.episode import PrivateEpisode
    from nexus.models.events import TraceRecord
    from nexus.models.investigation import InvestigationSpec, SpecimenStock
    from nexus.models.network import NetworkSpec, NetworkStock
    from nexus.models.world import Artifact, WorldState

    type ScientificSpec = InvestigationSpec | NetworkSpec | DomainInvestigation
    type ScientificArtifact = Artifact | DomainArtifact
    type ScientificStock = SpecimenStock | NetworkStock | DomainStock


class ScientificRuntime(Protocol):
    performance_style: str

    def spawn(self, stock: ScientificStock, artifact_id: str) -> ScientificArtifact: ...
    def transform(
        self,
        artifact: ScientificArtifact,
        machine: str,
        episode: PrivateEpisode,
        instrument_settings: tuple[int, ...] | None = None,
    ) -> ScientificArtifact: ...
    def configure(
        self, episode: PrivateEpisode, state: WorldState, action: ConfigureAction
    ) -> None: ...
    def assess_mission(self, episode: PrivateEpisode, state: WorldState) -> None: ...
    def public_contract(self, spec: ScientificSpec) -> dict: ...
    def mission_room(self, spec: ScientificSpec) -> str: ...
    def mission_machine(self, spec: ScientificSpec) -> str: ...
    def expected(self, episode: PrivateEpisode) -> tuple[int, ...]: ...
    def submitted(self, state: WorldState) -> tuple[int, ...] | None: ...
    def physical_plan(self, episode: PrivateEpisode) -> tuple[Action, ...]: ...
    def belief(self, spec: ScientificSpec) -> Belief: ...
    def measurement(self, record: TraceRecord) -> Measurement | None: ...
    def log_terminal(
        self,
        spec: ScientificSpec,
        calibration_count: int,
        no_signal_count: int,
        after_resolved_count: int,
        first_classes: int | None,
    ) -> None: ...
