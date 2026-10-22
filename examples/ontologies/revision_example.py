"""Trusted operator example: generation, public policy, exact replay; no model calls."""

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode
from nexus.ontology.discovery.policy import public_policy
from nexus.protocol.session import Session


def main():
    episode = generate_episode(
        5866,
        axis_version=2,
        science_family="model-revision-v1",
        theory_level=3,
        discovery_level=5,
        planning_level=0,
        resource_pressure=1,
        ontology_options={"guidance": "principles"},
    )
    session = Session(episode)
    response = public_policy(session, episode.public.evidence_files)
    if not response.victory_code:
        raise RuntimeError("public policy did not win")
    if canonical_hash(replay(episode, session.trace)) != canonical_hash(session.state):
        raise RuntimeError("replay mismatch")
    print(f"Supported win and replay in {response.current_turn} actions")


if __name__ == "__main__":
    main()
