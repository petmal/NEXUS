"""Live reference, source-bound preflight and replay remain distinct from depth."""

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator.qualify import QualificationReport
from nexus.models.episode import PrivateEpisode
from nexus.ontology.staged.policy import public_policy
from nexus.protocol.session import Session


def qualify_staged(episode):
    try:
        validated = PrivateEpisode.model_validate_json(episode.model_dump_json())
        session = Session(validated)
        result = public_policy(session, validated.public.evidence_files)
        checks = {
            "compiled_contract": True,
            "public_policy_wins": bool(result.victory_code),
            "supported_win": result.performance.decision_diagnostics.escape_classification
            == "supported_win",
            "within_reference_bound": result.current_turn
            <= validated.generation_metadata.guaranteed_policy_action_count,
            "exact_replay": canonical_hash(replay(validated, session.trace))
            == canonical_hash(session.state),
        }
        return QualificationReport(
            passed=all(checks.values()),
            checks=checks,
            errors=tuple(k for k, v in checks.items() if not v),
            metrics={
                "actions": result.current_turn,
                "difficulty_scope": "bounded mission information and adaptive-vs-fixed reading advantage; no deep cognition/model failure claim",
            },
        )
    except (ValueError, RuntimeError, KeyError, TypeError) as exc:
        return QualificationReport(
            passed=False, checks={"compiled_contract": False}, errors=(str(exc),), metrics={}
        )
