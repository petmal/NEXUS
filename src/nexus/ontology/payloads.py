"""Trusted schema registration isolated from runtime imports to avoid model cycles."""

from types import MappingProxyType

from nexus.ontology.categorical.schema import SCHEMAS as CATEGORICAL
from nexus.ontology.causal.schema import SCHEMAS as CAUSAL
from nexus.ontology.dynamics.schema import SCHEMAS as DYNAMICS
from nexus.ontology.repair.schema import SCHEMAS as REPAIR

_SCHEMAS = MappingProxyType(
    {
        "categorical-chain-poc-v1": MappingProxyType(dict(CATEGORICAL)),
        "causal-mechanisms-v1": MappingProxyType(dict(CAUSAL)),
        "coupled-repair-v1": MappingProxyType(dict(REPAIR)),
        "coupled-dynamics-v1": MappingProxyType(dict(DYNAMICS)),
    }
)


def schema_for(ontology: str, role: str):
    if ontology not in _SCHEMAS or role not in _SCHEMAS[ontology]:
        raise ValueError(f"unsupported ontology payload: {ontology}/{role}")
    return _SCHEMAS[ontology][role]
