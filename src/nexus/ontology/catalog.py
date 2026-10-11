"""Explicit built-in ontology selection; importing this module never builds a prior.

Episode data selects a registered identifier, never a Python import path. The
catalog contains code-owned definitions only; no player registration is allowed.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nexus.models.episode import PrivateEpisode


@dataclass(frozen=True)
class OntologyDefinition:
    family: str
    specification_version: str

    def runtime(self):
        if self.family == "categorical-chain-poc-v1":
            from nexus.ontology.categorical import runtime

            return runtime
        from nexus.ontology import builtin_runtime

        return builtin_runtime

    def generate(self, seed: int, **kwargs) -> PrivateEpisode:
        if self.family == "categorical-chain-poc-v1":
            raise ValueError(
                "experimental uncalibrated family: use generate_categorical(depth=2 or 3)"
            )
        if self.family == "shared-response-v1":
            from nexus.generator.investigation import generate_investigation

            return generate_investigation(seed, **kwargs)
        if self.family == "coupled-network-v1":
            from nexus.generator.network import generate_network

            return generate_network(seed, **kwargs)
        from nexus.generator.resonance import generate_resonant

        return generate_resonant(seed, **kwargs)

    def qualify(self, episode: PrivateEpisode):
        if self.family == "categorical-chain-poc-v1":
            from nexus.ontology.categorical.qualification import qualify_categorical

            return qualify_categorical(episode)
        if self.family == "shared-response-v1":
            from nexus.generator.investigation_qualify import qualify_investigation

            return qualify_investigation(episode)
        if self.family == "coupled-network-v1":
            from nexus.generator.network_qualify import qualify_network

            return qualify_network(episode)
        from nexus.generator.resonance_qualify import qualify_resonant

        return qualify_resonant(episode)


BUILTINS = MappingProxyType(
    {
        item.family: item
        for item in (
            OntologyDefinition("categorical-chain-poc-v1", "categorical-chain-poc-v1"),
            OntologyDefinition("shared-response-v1", "scientific-v2"),
            OntologyDefinition("coupled-network-v1", "coupled-network-v1"),
            OntologyDefinition("resonant-network-v1", "resonant-network-v1"),
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
