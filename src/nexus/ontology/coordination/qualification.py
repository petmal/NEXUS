"""Live supported finish and replay, separate from matrix-level independent proof."""

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator.qualify import QualificationReport
from nexus.models.episode import PrivateEpisode
from nexus.ontology.coordination.policy import public_policy
from nexus.protocol.investigation_metrics import AuditedDecisionMissionPerformance
from nexus.protocol.session import Session


def qualify(episode):
    try:
        episode = PrivateEpisode.model_validate_json(episode.model_dump_json())
        session = Session(episode)
        result = public_policy(session, episode.public.evidence_files)
        checks = {
            "compiled_contract": True,
            "public_policy_supported_win": bool(result.victory_code)
            and isinstance(result.performance, AuditedDecisionMissionPerformance)
            and result.performance.decision_diagnostics.escape_classification == "supported_win",
            "exact_reference_actions": result.current_turn
            == episode.generation_metadata.guaranteed_policy_action_count,
            "exact_replay": canonical_hash(replay(episode, session.trace))
            == canonical_hash(session.state),
        }
        return QualificationReport(
            passed=all(checks.values()),
            checks=checks,
            errors=tuple(key for key, value in checks.items() if not value),
            metrics={
                "actions": result.current_turn,
                "scope": "Live public reference and replay; matrix preflight independently proves optimum and interleaving.",
            },
        )
    except (ValueError, RuntimeError, KeyError, TypeError) as exc:
        return QualificationReport(
            passed=False, checks={"compiled_contract": False}, errors=(str(exc),), metrics={}
        )
