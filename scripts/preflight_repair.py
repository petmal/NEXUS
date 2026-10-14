"""Operator-only image check: win and replay both qualified repair profiles."""

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode
from nexus.ontology.repair.policy import public_policy
from nexus.protocol.session import Session


def main():
    for planning in (0, 1):
        episode = generate_episode(
            3943,
            axis_version=2,
            science_family="coupled-repair-v1",
            theory_level=3,
            discovery_level=5,
            planning_level=planning,
            resource_pressure=1,
        )
        session = Session(episode)
        result = public_policy(session)
        if not result.victory_code or result.current_turn != 14 + planning:
            raise RuntimeError(f"P{planning} public policy did not win within its bound")
        if canonical_hash(replay(episode, session.trace)) != canonical_hash(session.state):
            raise RuntimeError(f"P{planning} replay differs from the live terminal state")
        print(f"P{planning}: qualified, won in {result.current_turn} actions, replay verified")


if __name__ == "__main__":
    main()
