"""Opt-in revision family over the persistent scientific construction adapter."""

from nexus.ontology.discovery.generation import generate
from nexus.ontology.revision.schema import FAMILY


def generate_episode(seed, **kwargs):
    return generate(FAMILY, seed, **kwargs)
