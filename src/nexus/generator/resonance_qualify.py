"""Qualification by independent factor witnesses and their explicit composition contract."""

from nexus.diagnostics import timed_stage
from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import execute_with_trace, replay
from nexus.engine.resonance import resonance, settings
from nexus.generator.network import compile_network
from nexus.generator.resonance import calibration_prior, generate_resonant, reference_plan
from nexus.generator.resonance_docs import evidence_files
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PrivateEpisode
from nexus.models.network import NetworkSpec, NetworkTruth


def qualify_resonant(episode: PrivateEpisode):
    from nexus.generator.qualify import QualificationReport

    checks, errors = {}, []
    replayed = 0
    try:
        checks["roundtrip"] = (
            PrivateEpisode.model_validate_json(episode.model_dump_json()) == episode
        )
        spec, truth, meta = (
            episode.public.investigation,
            episode.investigation_truth,
            episode.generation_metadata,
        )
        hs, _ = calibration_prior()
        if (
            not isinstance(spec, NetworkSpec)
            or not isinstance(truth, NetworkTruth)
            or truth.resonance is None
        ):
            raise ValueError("qualification requires resonant specification and truth")
        gs, _ = compile_network()
        checks["complete_factor_prior"] = (
            truth.resonance in hs and truth.model_copy(update={"resonance": None}) in gs
        )
        if not all(checks.values()):
            raise ValueError("invalid resonance prior or serialized episode")
        expected = generate_resonant(
            0,
            discovery_level=spec.discovery,
            theory_level=spec.theory,
            planning_level=meta.planning_level,
            resource_pressure=meta.resource_pressure,
            verifier_secret=episode.verifier_secret,
        )
        expected.public.episode_id = episode.public.episode_id
        expected.investigation_truth = truth
        supplied = tuple(
            (name, resonance(truth.resonance, *map(int, name.split(":")[1:])))
            if name.startswith("cal:")
            else (name, value)
            for name, value in expected.public.investigation.supplied_measurements
        )
        if spec.discovery == 0:
            from nexus.engine.network import response

            supplied = tuple(
                (name, response(truth, *map(int, name.split(":")[1:])))
                if name.startswith("response:")
                else (name, value)
                for name, value in supplied
            )
        expected.public.investigation = expected.public.investigation.model_copy(
            update={
                "supplied_measurements": supplied,
                "resolved_settings": settings(truth) if spec.theory == 0 else None,
            }
        )
        expected.public.evidence_files = evidence_files(expected)
        expected.reference_plan = reference_plan(expected)
        checks["compiled_public_contract"] = episode.public == expected.public
        checks["compiled_metadata"] = meta == expected.generation_metadata
        checks["no_undeclared_rules"] = not episode.rules and not episode.machine_rules
        checks["reference_consistency"] = episode.reference_plan == expected.reference_plan
        if not all(checks.values()):
            raise ValueError("resonant compilation does not match its public contract")

        def witness(candidate):
            nonlocal replayed
            plan = reference_plan(candidate)
            state, trace = execute_with_trace(
                candidate, [ACTION_ADAPTER.validate_python(a) for a in plan]
            )
            if state.terminal_status != "won" or not trace[-1].victory_code:
                raise ValueError("composed scientific witness did not win")
            if len(plan) > meta.guaranteed_policy_action_count:
                raise ValueError("composed witness exceeded its bound")
            replayed += 1
            return state, trace

        state, trace = witness(episode)
        checks["trace_replay"] = canonical_hash(replay(episode, trace)) == canonical_hash(state)
        # D0 already fixes the field prediction from supplied evidence. For D4/D5,
        # stage decisions depend only on their factor's observations. H only changes
        # the configured numbers during stage2, never its route or action count.
        if spec.discovery:
            with timed_stage("resonance.factor_witness_replay"):
                for g in gs:
                    witness(
                        episode.model_copy(
                            update={
                                "investigation_truth": g.model_copy(update={"resonance": hs[0]})
                            }
                        )
                    )
                for h in hs:
                    witness(
                        episode.model_copy(
                            update={
                                "investigation_truth": gs[0].model_copy(update={"resonance": h})
                            }
                        )
                    )
        checks["factor_witnesses_compose"] = True
        checks["moderate_sweep_excluded"] = (
            not (spec.discovery and meta.planning_level == 1 and meta.resource_pressure == 1)
            or meta.action_budget < 92
        )
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        errors.append(str(exc))
    errors.extend(key for key, value in checks.items() if not value)
    return QualificationReport(
        passed=not errors,
        checks=checks,
        errors=tuple(errors),
        metrics={
            "family": "resonant-network-v1",
            "factor_witnesses_replayed": replayed,
            "joint_prior_worlds": 59049,
            "scope": "factor witness replay plus separable stage composition; not full product replay",
        },
    )
