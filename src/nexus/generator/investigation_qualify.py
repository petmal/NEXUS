"""Qualification of integrated scientific profiles, including every complete truth."""

from nexus.engine.canonical import canonical_hash
from nexus.engine.investigation import measurement, settings
from nexus.engine.replay import execute_with_trace, replay
from nexus.generator.investigation import (
    base_spec,
    information_certificate,
    make_spec,
    prior,
    reference_plan,
    validate_profile,
)
from nexus.generator.investigation_docs import evidence_files
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PrivateEpisode
from nexus.models.world import TerminalStatus


def qualify_investigation(episode: PrivateEpisode):
    from nexus.generator.qualify import QualificationReport

    checks, errors = {}, []
    spec = episode.public.investigation
    meta = episode.generation_metadata
    try:
        validate_profile(spec.discovery, spec.theory, meta.planning_level, meta.resource_pressure)
        initial = episode.public.initial_state
        p, r = meta.planning_level, meta.resource_pressure
        expected_spec = make_spec(spec.discovery, spec.theory, spec.scale, f"R{p}")
        checks["axis_metadata"] = (
            meta.discovery_level == spec.discovery and meta.theory_level == spec.theory
        )
        checks["public_profile"] = (
            base_spec(expected_spec) == base_spec(spec) and spec.controller_room == f"R{p}"
        )
        checks["topology"] = set(episode.public.rooms) == {
            f"R{i}" for i in range(p + 1)
        } and episode.public.edges == tuple((f"R{i}", f"R{i + 1}") for i in range(p))
        checks["initial_state"] = (
            initial.agent_room == "R0"
            and initial.turn == 0
            and initial.phase == 0
            and initial.terminal_status == TerminalStatus.ACTIVE
            and not initial.artifacts
            and initial.controller_settings is None
            and initial.controller_accepted is None
            and episode.public.phase_modulus == 1
        )
        expected_stocks = {
            (source, q)
            for source in ("reference", "0", "1")
            for q in ((0,) if spec.preparation_required else (0, 1, 2))
        }
        checks["stock_contract"] = (
            len(initial.stocks) == len(expected_stocks)
            and {(stock.source, stock.q) for stock in initial.stocks.values()} == expected_stocks
            and all(
                stock.location == "R0"
                and stock.remaining == (None if r == 0 else 4)
                and stock.id == f"S{stock.source}-{stock.q}"
                for stock in initial.stocks.values()
            )
        )
        expected_machines = {"meter", "prepare", "controller"}
        if spec.known_selector is None:
            expected_machines.add("selector")
        if spec.material_meter:
            expected_machines.add("material")
        checks["apparatus_contract"] = (
            set(initial.machines) == expected_machines
            and all(
                machine.room_id == (f"R{p}" if name == "controller" else "R0" if p == 0 else "R1")
                and machine.uses_remaining == (None if r == 0 else 32)
                for name, machine in initial.machines.items()
            )
            and not episode.rules
            and not episode.machine_rules
        )
        if not all(checks.values()):
            raise ValueError("compiled physical interface does not match the scientific profile")
        worlds, problem = prior(episode)
        truth = episode.investigation_truth
        checks["truth_in_complete_prior"] = truth in worlds
        checks["public_evidence_matches_contract"] = (
            episode.public.evidence_files == evidence_files(episode)
        )
        checks["supplied_measurements_true"] = all(
            measurement(spec, truth, name) == value for name, value in spec.supplied_measurements
        )
        checks["resolved_settings_true"] = (
            spec.resolved_settings is None or spec.resolved_settings == settings(spec, truth)
        )
        expected_evidence = (
            tuple((name, measurement(spec, truth, name)) for name, _ in problem.experiments)
            if spec.discovery == 0
            else ()
        )
        checks["disclosure_contract"] = spec.supplied_measurements == expected_evidence and (
            spec.resolved_settings is not None
        ) == (spec.theory == 0)
        checks["goal_contract"] = episode.public.goal.model_dump() == {
            "kind": "controller_accepted",
            "artifact_id": None,
            "field": None,
            "value": None,
            "children": (),
        }
        if not all(checks.values()):
            raise ValueError(
                "compiled theory, disclosure, truth or goal does not match the profile"
            )
        calculated = information_certificate(base_spec(spec))
        expected_min = problem.minimum_guaranteed_measurements(spec.supplied_measurements)
        checks["measurement_certificate"] = (
            meta.required_probe_count == expected_min
            and meta.investigation_certificate["minimum_measurements"] == expected_min
        )
        checks["family_certificate"] = all(
            meta.investigation_certificate[k] == v
            for k, v in calculated.items()
            if k not in ("minimum_measurements", "fixed_measurements", "adaptive_gap")
        )
        checks["reference_plan_consistent"] = episode.reference_plan == reference_plan(episode)
        plan = [ACTION_ADAPTER.validate_python(a) for a in episode.reference_plan]
        state, trace = execute_with_trace(episode, plan)
        checks["reference_wins"] = state.terminal_status == TerminalStatus.WON and bool(
            trace[-1].victory_code
        )
        checks["replay"] = canonical_hash(replay(episode, trace)) == canonical_hash(state)
        # D0 is intentionally conditioned on supplied evidence, so only consistent truths remain.
        indices = problem.compatible(spec.supplied_measurements)
        bound = 0
        for i in indices:
            candidate = episode.model_copy(update={"investigation_truth": worlds[i]})
            candidate_plan = reference_plan(candidate)
            result, records = execute_with_trace(
                candidate, [ACTION_ADAPTER.validate_python(a) for a in candidate_plan]
            )
            if result.terminal_status != TerminalStatus.WON or not records[-1].victory_code:
                raise ValueError("a public-prior truth lacks a realizable successful policy")
            bound = max(bound, len(candidate_plan))
        checks["all_truths_physically_solvable"] = True
        checks["policy_bound"] = bound == meta.guaranteed_policy_action_count
        budget = episode.public.initial_state.resources.actions_remaining
        checks["budget"] = (
            budget is None
            if meta.resource_pressure == 0
            else budget == bound + (8 if meta.resource_pressure == 1 else 0)
        )
        expected_certificate = dict(calculated)
        if spec.discovery == 0:
            expected_certificate.update(
                minimum_measurements=0,
                fixed_measurements=0,
                adaptive_gap=0,
                target_classes_after_evidence=1,
            )
        expected_certificate.update(
            constructive_policy_action_bound=bound,
            action_budget=budget,
            initial_measurements=len(spec.supplied_measurements),
        )
        checks["complete_certificate"] = meta.investigation_certificate == expected_certificate
        checks["physical_metadata"] = (
            meta.optimal_action_count == p + 2
            and meta.action_budget == (budget or 0)
            and meta.room_count == p + 1
            and meta.machine_count == len(expected_machines)
        )
        checks["compiled_roundtrip"] = (
            PrivateEpisode.model_validate_json(episode.model_dump_json()) == episode
        )
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    errors.extend(name for name, valid in checks.items() if not valid)
    return QualificationReport(
        passed=not errors,
        checks=checks,
        errors=tuple(errors),
        metrics={
            "axis_version": 2,
            "family": "shared-response-v1",
            "prior_worlds": len(worlds) if "worlds" in locals() else 0,
        },
    )
