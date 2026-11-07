"""Explicit built-in ontology selection; importing this module never builds a prior.

Episode data selects a registered identifier, never a Python import path. The
catalog contains code-owned definitions only; no player registration is allowed.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import cached_property
from importlib import import_module
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nexus.models.episode import PrivateEpisode


@dataclass(frozen=True)
class OntologyDefinition:
    """One trusted registration; payload lookup never imports the runtime.

    Register code here, not in episode JSON. Optional generation options are
    validated by the ontology's own data schema before its factory is called.
    """

    family: str
    specification_version: str
    runtime_module: str = "nexus.ontology.builtin_runtime"
    generator: tuple[str, str] | None = None
    qualifier: tuple[str, str] = ("", "")
    standalone_contract: bool = False
    diagnostic_budget: bool = False
    schema_module: str | None = None
    options_schema: tuple[str, str] | None = None
    api_version: int = 1
    # Opt in only for planners with an independent minimum-cost argument.
    exact_physical_plan: bool = False

    def __post_init__(self):
        if type(self.api_version) is not int or self.api_version != 1:
            raise ValueError(f"{self.family}: unsupported ontology API version")
        if not self.family or not self.specification_version:
            raise ValueError("ontology family and specification version are required")
        targets = [self.runtime_module]
        if self.schema_module is not None:
            targets.append(self.schema_module)
        for target in (self.generator, self.qualifier, self.options_schema):
            if target is not None:
                if len(target) != 2 or not all(target):
                    raise ValueError(f"{self.family}: incomplete import target")
                targets.extend(target)
        if any(not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", t) for t in targets):
            raise ValueError(f"{self.family}: invalid trusted import target")

    @cached_property
    def schemas(self):
        from pydantic import BaseModel

        if self.schema_module is None:
            return MappingProxyType({})
        schemas = getattr(import_module(self.schema_module), "SCHEMAS", None)
        required = {"artifact", "investigation", "truth"}
        if not isinstance(schemas, Mapping) or not required <= schemas.keys():
            raise ValueError(f"{self.family}: schemas require artifact, investigation and truth")
        if not schemas.keys() <= required | {"stock"} or any(
            not isinstance(value, type) or not issubclass(value, BaseModel)
            for value in schemas.values()
        ):
            raise ValueError(f"{self.family}: invalid payload role or Pydantic schema")
        return MappingProxyType(dict(schemas))

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
        options = kwargs.pop("ontology_options", None)
        if self.options_schema is None:
            if options:
                raise ValueError(f"{self.family}: generation options are not supported")
        else:
            module, name = self.options_schema
            kwargs["options"] = getattr(import_module(module), name).model_validate(
                {} if options is None else options
            )
        module, name = self.generator
        return getattr(import_module(module), name)(seed, **kwargs)

    def qualify(self, episode: PrivateEpisode):
        module, name = self.qualifier
        return getattr(import_module(module), name)(episode)


@dataclass(frozen=True)
class OntologyRegistry:
    """Immutable indexes; conflicts fail before a definition can be overwritten."""

    families: Mapping[str, OntologyDefinition]
    specifications: Mapping[str, OntologyDefinition]

    def __post_init__(self):
        families, specifications = dict(self.families), dict(self.specifications)
        if (
            len(families) != len(specifications)
            or any(key != value.family for key, value in families.items())
            or any(key != value.specification_version for key, value in specifications.items())
            or {value.specification_version: value for value in families.values()} != specifications
        ):
            raise ValueError("ontology indexes must describe the same unique definitions")
        object.__setattr__(self, "families", MappingProxyType(families))
        object.__setattr__(self, "specifications", MappingProxyType(specifications))

    @classmethod
    def from_definitions(cls, definitions: Iterable[OntologyDefinition]) -> OntologyRegistry:
        families = {}
        specifications = {}
        for definition in definitions:
            if definition.family in families:
                raise ValueError(f"duplicate ontology family: {definition.family}")
            if definition.specification_version in specifications:
                raise ValueError(
                    f"duplicate specification version: {definition.specification_version}"
                )
            families[definition.family] = definition
            specifications[definition.specification_version] = definition
        return cls(MappingProxyType(families), MappingProxyType(specifications))


REGISTRY = OntologyRegistry.from_definitions(
    (
        OntologyDefinition(
            "stateful-interference-v1",
            "stateful-interference-v1",
            runtime_module="nexus.ontology.interference.runtime",
            schema_module="nexus.ontology.interference.schema",
            options_schema=("nexus.ontology.interference.schema", "GenerationOptions"),
            exact_physical_plan=True,
            generator=("nexus.ontology.interference.generation", "generate_episode"),
            qualifier=("nexus.ontology.interference.qualification", "qualify"),
            standalone_contract=True,
        ),
        OntologyDefinition(
            "stateful-coordination-v1",
            "stateful-coordination-v1",
            runtime_module="nexus.ontology.coordination.runtime",
            schema_module="nexus.ontology.coordination.schema",
            options_schema=("nexus.ontology.coordination.schema", "GenerationOptions"),
            exact_physical_plan=True,
            generator=("nexus.ontology.coordination.generation", "generate_episode"),
            qualifier=("nexus.ontology.coordination.qualification", "qualify"),
            standalone_contract=True,
        ),
        OntologyDefinition(
            "stateful-planning-v1",
            "stateful-planning-v1",
            runtime_module="nexus.ontology.planning.runtime",
            schema_module="nexus.ontology.planning.schema",
            exact_physical_plan=True,
            generator=("nexus.ontology.planning.generation", "generate_episode"),
            qualifier=("nexus.ontology.planning.qualification", "qualify"),
            standalone_contract=True,
        ),
        OntologyDefinition(
            "model-revision-v1",
            "model-revision-v1",
            runtime_module="nexus.ontology.revision.runtime",
            schema_module="nexus.ontology.revision.schema",
            options_schema=("nexus.ontology.revision.schema", "GenerationOptions"),
            generator=("nexus.ontology.revision.generation", "generate_episode"),
            qualifier=("nexus.ontology.discovery.qualification", "qualify"),
            diagnostic_budget=True,
            standalone_contract=True,
        ),
        OntologyDefinition(
            "stateful-discovery-v1",
            "stateful-discovery-v1",
            runtime_module="nexus.ontology.stateful.runtime",
            schema_module="nexus.ontology.stateful.schema",
            exact_physical_plan=True,
            generator=("nexus.ontology.stateful.generation", "generate_episode"),
            qualifier=("nexus.ontology.stateful.qualification", "qualify"),
            diagnostic_budget=True,
            standalone_contract=True,
        ),
        OntologyDefinition(
            "coupled-memory-v1",
            "coupled-memory-v1",
            runtime_module="nexus.ontology.coupled_memory.runtime",
            schema_module="nexus.ontology.coupled_memory.schema",
            generator=("nexus.ontology.coupled_memory.generation", "generate_episode"),
            qualifier=("nexus.ontology.discovery.qualification", "qualify"),
            diagnostic_budget=True,
            standalone_contract=True,
        ),
        OntologyDefinition(
            "representation-discovery-v1",
            "representation-discovery-v1",
            runtime_module="nexus.ontology.representation.runtime",
            schema_module="nexus.ontology.representation.schema",
            generator=("nexus.ontology.representation.generation", "generate_episode"),
            qualifier=("nexus.ontology.discovery.qualification", "qualify"),
            diagnostic_budget=True,
            standalone_contract=True,
        ),
        OntologyDefinition(
            "uncertainty-construction-v1",
            "uncertainty-construction-v1",
            runtime_module="nexus.ontology.uncertainty.runtime",
            schema_module="nexus.ontology.uncertainty.schema",
            generator=("nexus.ontology.uncertainty.generation", "generate_episode"),
            qualifier=("nexus.ontology.discovery.qualification", "qualify"),
            diagnostic_budget=True,
            standalone_contract=True,
        ),
        OntologyDefinition(
            "joint-assembly-v1",
            "joint-assembly-v1",
            runtime_module="nexus.ontology.assembly.runtime",
            schema_module="nexus.ontology.assembly.schema",
            exact_physical_plan=True,
            generator=("nexus.ontology.assembly.generation", "generate_assembly"),
            qualifier=("nexus.ontology.assembly.qualification", "qualify_assembly"),
            diagnostic_budget=True,
            standalone_contract=True,
        ),
        OntologyDefinition(
            "staged-repair-v1",
            "staged-repair-v1",
            runtime_module="nexus.ontology.staged.runtime",
            schema_module="nexus.ontology.staged.schema",
            generator=("nexus.ontology.staged.generation", "generate_staged"),
            qualifier=("nexus.ontology.staged.qualification", "qualify_staged"),
            diagnostic_budget=True,
            standalone_contract=True,
        ),
        OntologyDefinition(
            "history-coupled-v1",
            "history-coupled-v1",
            runtime_module="nexus.ontology.history.runtime",
            schema_module="nexus.ontology.history.schema",
            exact_physical_plan=True,
            generator=("nexus.ontology.history.generation", "generate_history"),
            diagnostic_budget=True,
            qualifier=("nexus.ontology.history.qualification", "qualify_history"),
            standalone_contract=True,
        ),
        OntologyDefinition(
            "coupled-transfer-v1",
            "coupled-transfer-v1",
            runtime_module="nexus.ontology.transfer.runtime",
            schema_module="nexus.ontology.transfer.schema",
            generator=("nexus.ontology.transfer.generation", "generate_transfer"),
            diagnostic_budget=True,
            qualifier=("nexus.ontology.transfer.qualification", "qualify_transfer"),
            standalone_contract=True,
        ),
        OntologyDefinition(
            "coupled-evidence-v1",
            "coupled-evidence-v1",
            runtime_module="nexus.ontology.transfer.runtime",
            schema_module="nexus.ontology.transfer.schema",
            generator=("nexus.ontology.transfer.generation", "generate_evidence"),
            diagnostic_budget=True,
            qualifier=("nexus.ontology.transfer.qualification", "qualify_transfer"),
            standalone_contract=True,
        ),
        OntologyDefinition(
            "compositional-repair-v1",
            "compositional-repair-v1",
            runtime_module="nexus.ontology.compositional.runtime",
            schema_module="nexus.ontology.compositional.schema",
            generator=("nexus.ontology.compositional.generation", "generate_compositional"),
            diagnostic_budget=True,
            qualifier=("nexus.ontology.compositional.qualification", "qualify_compositional"),
            standalone_contract=True,
        ),
        OntologyDefinition(
            "coupled-dynamics-v1",
            "coupled-dynamics-v1",
            runtime_module="nexus.ontology.dynamics.runtime",
            schema_module="nexus.ontology.dynamics.schema",
            generator=("nexus.ontology.dynamics.generation", "generate_dynamics"),
            qualifier=("nexus.ontology.dynamics.qualification", "qualify_dynamics"),
            standalone_contract=True,
        ),
        OntologyDefinition(
            "coupled-repair-v1",
            "coupled-repair-v1",
            runtime_module="nexus.ontology.repair.runtime",
            schema_module="nexus.ontology.repair.schema",
            generator=("nexus.ontology.repair.generation", "generate_qualified_repair"),
            qualifier=("nexus.ontology.repair.qualification", "qualify_repair"),
            standalone_contract=True,
        ),
        OntologyDefinition(
            "categorical-chain-poc-v1",
            "categorical-chain-poc-v1",
            runtime_module="nexus.ontology.categorical.runtime",
            schema_module="nexus.ontology.categorical.schema",
            qualifier=("nexus.ontology.categorical.qualification", "qualify_categorical"),
        ),
        OntologyDefinition(
            "shared-response-v1",
            "scientific-v2",
            exact_physical_plan=True,
            generator=("nexus.generator.investigation", "generate_investigation"),
            qualifier=("nexus.generator.investigation_qualify", "qualify_investigation"),
        ),
        OntologyDefinition(
            "coupled-network-v1",
            "coupled-network-v1",
            exact_physical_plan=True,
            generator=("nexus.generator.network", "generate_network"),
            qualifier=("nexus.generator.network_qualify", "qualify_network"),
        ),
        OntologyDefinition(
            "resonant-network-v1",
            "resonant-network-v1",
            exact_physical_plan=True,
            generator=("nexus.generator.resonance", "generate_resonant"),
            qualifier=("nexus.generator.resonance_qualify", "qualify_resonant"),
        ),
        OntologyDefinition(
            "causal-mechanisms-v1",
            "causal-mechanisms-v1",
            runtime_module="nexus.ontology.causal.runtime",
            schema_module="nexus.ontology.causal.schema",
            exact_physical_plan=True,
            generator=("nexus.ontology.causal.generation", "generate_causal"),
            qualifier=("nexus.ontology.causal.qualification", "qualify_causal"),
            standalone_contract=True,
        ),
    )
)
BUILTINS = REGISTRY.families
_BY_SPEC = REGISTRY.specifications


def definition_for(spec) -> OntologyDefinition:
    key = getattr(spec, "ontology", getattr(spec, "version", None))
    if not isinstance(key, str) or key not in _BY_SPEC:
        raise ValueError("unknown scientific specification")
    return _BY_SPEC[key]


def runtime_for(spec):
    return definition_for(spec).runtime()
