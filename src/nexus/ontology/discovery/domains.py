"""Closed code-owned dispatch for shared discovery mechanics."""

from importlib import import_module
from dataclasses import dataclass


@dataclass(frozen=True)
class Adapter:
    package: str
    reader: tuple[int, ...]
    assembler: tuple[int, ...]
    schedule_multiplicity: int = 1


ADAPTERS = {
    "representation-discovery-v1": Adapter("representation", (0,), (0, 0, 0, 0, 0, 1, 1, 1, 0)),
    "uncertainty-construction-v1": Adapter("uncertainty", (0, 0), (0, 0, 0), 40320),
    "coupled-memory-v1": Adapter("coupled_memory", (0,), (0, 0, 0, 0, 1, 1, 0)),
}

PACKAGES = {family: adapter.package for family, adapter in ADAPTERS.items()}


def module(family, role):
    if family not in PACKAGES or role not in ("laws", "schema", "evidence", "inference"):
        raise ValueError("unknown discovery adapter")
    return import_module(f"nexus.ontology.{PACKAGES[family]}.{role}")
