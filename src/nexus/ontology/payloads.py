"""Trusted schema registration isolated from runtime imports to avoid model cycles."""

from types import MappingProxyType

from nexus.ontology.categorical.schema import SCHEMAS

_SCHEMAS = MappingProxyType(dict(SCHEMAS))


def schema_for(ontology: str, role: str):
    if ontology != "categorical-chain-poc-v1" or role not in _SCHEMAS:
        raise ValueError(f"unsupported ontology payload: {ontology}/{role}")
    return _SCHEMAS[role]
