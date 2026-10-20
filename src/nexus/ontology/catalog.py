"""Explicit built-in ontology selection; importing this module never builds a prior.

Episode data selects a registered identifier, never a Python import path. The
catalog contains code-owned definitions only; no player registration is allowed.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nexus.models.episode import PrivateEpisode


@dataclass(frozen=True)
class OntologyDefinition:
    family: str
    specification_version: str
    runtime_module: str = "nexus.ontology.builtin_runtime"
    generator: tuple[str, str] | None = None
    qualifier: tuple[str, str] = ("", "")
    standalone_contract: bool = False
    diagnostic_budget: bool = False

    def runtime(self):
        return import_module(self.runtime_module)

    def action_reference(self):
        """Optional episode-independent contract supplied by the trusted adapter."""
        return self.runtime().public_contract(None) if self.standalone_contract else None

    def generate(self, seed: int, **kwargs) -> PrivateEpisode:
        if self.generator is None:
            raise ValueError(
                f"{self.family} is experimental and unavailable through the general factory"
            )
        module, name = self.generator
        return getattr(import_module(module), name)(seed, **kwargs)

    def qualify(self, episode: PrivateEpisode):
        module, name = self.qualifier
        return getattr(import_module(module), name)(episode)


BUILTINS = MappingProxyType(
    {
        item.family: item
        for item in (
            OntologyDefinition(
                "representation-discovery-v1", "representation-discovery-v1",
                runtime_module="nexus.ontology.representation.runtime",
                generator=("nexus.ontology.representation.generation", "generate_episode"),
                qualifier=("nexus.ontology.discovery.qualification", "qualify"),
                diagnostic_budget=True,
                standalone_contract=True,
            ),
            OntologyDefinition(
                "uncertainty-construction-v1", "uncertainty-construction-v1",
                runtime_module="nexus.ontology.uncertainty.runtime",
                generator=("nexus.ontology.uncertainty.generation", "generate_episode"),
                qualifier=("nexus.ontology.discovery.qualification", "qualify"),
                diagnostic_budget=True,
                standalone_contract=True,
            ),
            OntologyDefinition(
                "joint-assembly-v1", "joint-assembly-v1",
                runtime_module="nexus.ontology.assembly.runtime",
                generator=("nexus.ontology.assembly.generation", "generate_assembly"),
                qualifier=("nexus.ontology.assembly.qualification", "qualify_assembly"),
                diagnostic_budget=True,
                standalone_contract=True,
            ),
            OntologyDefinition(
                "staged-repair-v1", "staged-repair-v1",
                runtime_module="nexus.ontology.staged.runtime",
                generator=("nexus.ontology.staged.generation", "generate_staged"),
                qualifier=("nexus.ontology.staged.qualification", "qualify_staged"),
                diagnostic_budget=True,
                standalone_contract=True,
            ),
            OntologyDefinition(
                "history-coupled-v1", "history-coupled-v1",
                runtime_module="nexus.ontology.history.runtime",
                generator=("nexus.ontology.history.generation", "generate_history"),
                diagnostic_budget=True,
                qualifier=("nexus.ontology.history.qualification", "qualify_history"),
                standalone_contract=True,
            ),
            OntologyDefinition(
                "coupled-transfer-v1", "coupled-transfer-v1",
                runtime_module="nexus.ontology.transfer.runtime",
                generator=("nexus.ontology.transfer.generation", "generate_transfer"),
                diagnostic_budget=True,
                qualifier=("nexus.ontology.transfer.qualification", "qualify_transfer"),
                standalone_contract=True,
            ),
            OntologyDefinition(
                "coupled-evidence-v1", "coupled-evidence-v1",
                runtime_module="nexus.ontology.transfer.runtime",
                generator=("nexus.ontology.transfer.generation", "generate_evidence"),
                diagnostic_budget=True,
                qualifier=("nexus.ontology.transfer.qualification", "qualify_transfer"),
                standalone_contract=True,
            ),
            OntologyDefinition(
                "compositional-repair-v1", "compositional-repair-v1",
                runtime_module="nexus.ontology.compositional.runtime",
                generator=("nexus.ontology.compositional.generation", "generate_compositional"),
                diagnostic_budget=True,
                qualifier=("nexus.ontology.compositional.qualification", "qualify_compositional"),
                standalone_contract=True,
            ),
            OntologyDefinition(
                "coupled-dynamics-v1",
                "coupled-dynamics-v1",
                runtime_module="nexus.ontology.dynamics.runtime",
                generator=("nexus.ontology.dynamics.generation", "generate_dynamics"),
                qualifier=("nexus.ontology.dynamics.qualification", "qualify_dynamics"),
                standalone_contract=True,
            ),
            OntologyDefinition(
                "coupled-repair-v1",
                "coupled-repair-v1",
                runtime_module="nexus.ontology.repair.runtime",
                generator=("nexus.ontology.repair.generation", "generate_qualified_repair"),
                qualifier=("nexus.ontology.repair.qualification", "qualify_repair"),
                standalone_contract=True,
            ),
            OntologyDefinition(
                "categorical-chain-poc-v1",
                "categorical-chain-poc-v1",
                runtime_module="nexus.ontology.categorical.runtime",
                qualifier=("nexus.ontology.categorical.qualification", "qualify_categorical"),
            ),
            OntologyDefinition(
                "shared-response-v1",
                "scientific-v2",
                generator=("nexus.generator.investigation", "generate_investigation"),
                qualifier=("nexus.generator.investigation_qualify", "qualify_investigation"),
            ),
            OntologyDefinition(
                "coupled-network-v1",
                "coupled-network-v1",
                generator=("nexus.generator.network", "generate_network"),
                qualifier=("nexus.generator.network_qualify", "qualify_network"),
            ),
            OntologyDefinition(
                "resonant-network-v1",
                "resonant-network-v1",
                generator=("nexus.generator.resonance", "generate_resonant"),
                qualifier=("nexus.generator.resonance_qualify", "qualify_resonant"),
            ),
            OntologyDefinition(
                "causal-mechanisms-v1",
                "causal-mechanisms-v1",
                runtime_module="nexus.ontology.causal.runtime",
                generator=("nexus.ontology.causal.generation", "generate_causal"),
                qualifier=("nexus.ontology.causal.qualification", "qualify_causal"),
                standalone_contract=True,
            ),
        )
    }
)
_BY_SPEC = MappingProxyType({item.specification_version: item for item in BUILTINS.values()})


def definition_for(spec) -> OntologyDefinition:
    key = getattr(spec, "ontology", getattr(spec, "version", None))
    if not isinstance(key, str) or key not in _BY_SPEC:
        raise ValueError("unknown scientific specification")
    return _BY_SPEC[key]


def runtime_for(spec):
    return definition_for(spec).runtime()
