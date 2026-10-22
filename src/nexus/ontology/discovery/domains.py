"""Closed code-owned dispatch for shared discovery mechanics."""

from dataclasses import dataclass
from importlib import import_module


@dataclass(frozen=True)
class Adapter:
    package: str
    reader: tuple[int, ...]
    assembler: tuple[int, ...]
    schedule_multiplicity: int = 1
    description: str = ""
    reference_action_upper: int = 16
    prior_count_key: str = "prior_mechanism_programs"


ADAPTERS = {
    "representation-discovery-v1": Adapter("representation", (0,), (0, 0, 0, 0, 0, 1, 1, 1, 0)),
    "uncertainty-construction-v1": Adapter("uncertainty", (0, 0), (0, 0, 0), 40320),
    "coupled-memory-v1": Adapter("coupled_memory", (0,), (0, 0, 0, 0, 1, 1, 0)),
    "model-revision-v1": Adapter(
        "revision",
        (0,),
        (0, 0, 0, 0),
        description="Reconstruct a conservative routing cartridge to reopen the sealed facility.",
        reference_action_upper=18,
        prior_count_key="prior_behavior_classes",
    ),
}

PACKAGES = {family: adapter.package for family, adapter in ADAPTERS.items()}


def module(family, role):
    if family not in PACKAGES or role not in ("laws", "schema", "evidence", "inference"):
        raise ValueError("unknown discovery adapter")
    return import_module(f"nexus.ontology.{PACKAGES[family]}.{role}")
