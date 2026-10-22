"""Lazy role validation through the single trusted ontology registration."""

from nexus.ontology.catalog import BUILTINS


def schema_for(ontology: str, role: str):
    definition = BUILTINS.get(ontology)
    if definition is None or role not in definition.schemas:
        raise ValueError(f"unsupported ontology payload: {ontology}/{role}")
    return definition.schemas[role]
