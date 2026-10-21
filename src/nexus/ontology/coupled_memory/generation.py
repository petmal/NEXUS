"""Opt-in family; no change to previous discovery ontologies."""

from nexus.ontology.discovery.generation import generate
from nexus.ontology.coupled_memory.schema import FAMILY


def generate_episode(seed, **kwargs):
    return generate(FAMILY, seed, **kwargs)
