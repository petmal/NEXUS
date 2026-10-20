"""Versioned representation generator entry point."""

from nexus.ontology.discovery.generation import generate
from nexus.ontology.representation.schema import FAMILY


def generate_episode(seed, **kwargs):
    return generate(FAMILY, seed, **kwargs)
