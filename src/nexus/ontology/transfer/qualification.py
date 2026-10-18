"""Public policy and replay gate; separate matrix audits establish lower bounds."""

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator.qualify import QualificationReport
from nexus.models.episode import PrivateEpisode
from nexus.ontology.transfer.policy import public_policy
from nexus.protocol.session import Session


def qualify_transfer(episode):
    try:
        episode = PrivateEpisode.model_validate_json(episode.model_dump_json())
        session = Session(episode)
        result = public_policy(session, episode.public.evidence_files)
        checks = {
            "compiled_contract": True,
            "public_policy_wins": bool(result.victory_code),
            "within_reference_bound": result.current_turn
            <= episode.generation_metadata.guaranteed_policy_action_count,
            "exact_replay": canonical_hash(replay(episode, session.trace))
            == canonical_hash(session.state),
        }
        return QualificationReport(
            passed=all(checks.values()),
            checks=checks,
            errors=tuple(k for k, v in checks.items() if not v),
            metrics={
                "actions": result.current_turn,
                "difficulty_scope": "constructive upper only; see independent proof and matrix",
            },
        )
    except (ValueError, RuntimeError, KeyError, TypeError) as exc:
        return QualificationReport(
            passed=False, checks={"compiled_contract": False}, errors=(str(exc),), metrics={}
        )
