"""Full-prior physical replay and tamper checks for the coupled-network family."""

from __future__ import annotations

from nexus.diagnostics import timed_stage
from nexus.engine.canonical import canonical_hash
from nexus.engine.network import measurement, settings
from nexus.engine.replay import execute_with_trace, replay
from nexus.generator.network import compile_network, generate_network, reference_plan
from nexus.generator.network_docs import evidence_files
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PrivateEpisode
from nexus.models.world import TerminalStatus


def qualify_network(episode: PrivateEpisode):
    from nexus.generator.qualify import QualificationReport

    checks, errors = {}, []
    replayed = 0
    try:
        checks["roundtrip"] = (
            PrivateEpisode.model_validate_json(episode.model_dump_json()) == episode
        )
        spec, meta, truth = (
            episode.public.investigation,
            episode.generation_metadata,
            episode.investigation_truth,
        )
        worlds, problem = compile_network()
        checks["complete_prior_truth"] = truth in worlds
        if not checks["complete_prior_truth"] or not checks["roundtrip"]:
            raise ValueError("invalid compiled network truth")
        expected = generate_network(
            0,
            discovery_level=spec.discovery,
            theory_level=spec.theory,
            planning_level=meta.planning_level,
            resource_pressure=meta.resource_pressure,
            verifier_secret=episode.verifier_secret,
        )
        expected.public.episode_id = episode.public.episode_id
        supplied = (
            tuple((name, measurement(truth, name)) for name, _ in problem.experiments)
            if spec.discovery == 0
            else ()
        )
        expected.public.investigation = expected.public.investigation.model_copy(
            update={
                "supplied_measurements": supplied,
                "resolved_settings": settings(truth) if spec.theory == 0 else None,
            }
        )
        expected.investigation_truth = truth
        expected.public.evidence_files = evidence_files(expected)
        from nexus.presentation import attach
        expected = attach(expected, episode.public.presentation_version)
        checks["compiled_public_contract"] = episode.public == expected.public
        checks["compiled_metadata"] = meta == expected.generation_metadata
        checks["no_undeclared_rules"] = not episode.rules and not episode.machine_rules
        checks["reference_consistency"] = episode.reference_plan == reference_plan(expected)
        if not all(checks.values()):
            raise ValueError("network compilation does not match its qualified public contract")
        state, records = execute_with_trace(
            episode, [ACTION_ADAPTER.validate_python(a) for a in episode.reference_plan]
        )
        checks["actual_truth_wins"] = state.terminal_status == TerminalStatus.WON and bool(
            records[-1].victory_code
        )
        checks["trace_replay"] = canonical_hash(replay(episode, records)) == canonical_hash(state)
        bound = 0
        with timed_stage("network.full_prior_replay"):
            for i in problem.compatible(spec.supplied_measurements):
                candidate = episode.model_copy(update={"investigation_truth": worlds[i]})
                plan = reference_plan(candidate)
                result, trace = execute_with_trace(
                    candidate, [ACTION_ADAPTER.validate_python(a) for a in plan]
                )
                if result.terminal_status != TerminalStatus.WON or not trace[-1].victory_code:
                    raise ValueError("network admitted a physically unsolvable prior world")
                replayed += 1
                bound = max(bound, len(plan))
        checks["all_prior_worlds_win"] = True
        checks["physical_bound"] = bound == meta.guaranteed_policy_action_count
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        errors.append(str(exc))
    errors.extend(k for k, v in checks.items() if not v)
    return QualificationReport(
        passed=not errors,
        checks=checks,
        errors=tuple(errors),
        metrics={"axis_version": 2, "family": "coupled-network-v1", "worlds_replayed": replayed},
    )
