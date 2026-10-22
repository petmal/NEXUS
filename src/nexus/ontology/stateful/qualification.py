"""Live reference qualification; deep trajectory admission is a separate matrix gate."""

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator.qualify import QualificationReport
from nexus.models.episode import PrivateEpisode
from nexus.ontology.stateful.policy import public_policy
from nexus.protocol.session import Session


def qualify(episode):
    try:
        episode = PrivateEpisode.model_validate_json(episode.model_dump_json())
        session = Session(episode)
        result = public_policy(session, episode.public.evidence_files)
        checks = {
            "compiled_contract": True,
            "public_policy_supported_win": bool(result.victory_code)
            and result.performance.decision_diagnostics.escape_classification == "supported_win",
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
                "scope": "Reference qualification only; use the stateful matrix preflight for bounded difficulty admission.",
            },
        )
    except (ValueError, RuntimeError, KeyError, TypeError) as exc:
        return QualificationReport(
            passed=False, checks={"compiled_contract": False}, errors=(str(exc),), metrics={}
        )
