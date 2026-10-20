"""Closed code-owned dispatch for shared discovery mechanics."""

from importlib import import_module

PACKAGES = {
    "representation-discovery-v1": "representation",
    "uncertainty-construction-v1": "uncertainty",
}


def module(family, role):
    if family not in PACKAGES or role not in ("laws", "schema", "evidence", "inference"):
        raise ValueError("unknown discovery adapter")
    return import_module(f"nexus.ontology.{PACKAGES[family]}.{role}")
