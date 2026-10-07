"""Compile theory-relative evidence and policy metadata for a fixed physical world."""

from itertools import islice, product

from nexus.engine.canonical import canonical_hash
from nexus.engine.rules import apply_effect
from nexus.generator.difficulty import (
    GENERATION_SOLVER_BUDGET, recommended_tool_call_limit, required_probe_count, resource_allowance,
)
from nexus.generator.discovery import analyze_discovery
from nexus.generator.evidence import (
    EvidencePlanningError, candidates_matching_csv, evidence_csv, measurement_filename,
)
from nexus.generator.rules import enumerate_transformation_rules
from nexus.generator.theory import SPEC, theory_universe
from nexus.models.episode import PrivateEpisode
from nexus.solver.belief import solve_guaranteed_policy


def compile_theory(episode: PrivateEpisode) -> PrivateEpisode:
    """Preserve laws/topology/goals; fail closed when the paired D profile is not certified."""
    universe = theory_universe()
    metadata = episode.generation_metadata
    machine_ids = tuple(sorted(episode.machine_rules))
    evidence_level = min(metadata.discovery_level, 2)
    ceiling = 12 if len(machine_ids) == 2 else 32
    initial = episode.public.initial_state.artifacts["A1"]
    current = initial
    options = []
    for machine_id in machine_ids:
        rule = episode.rules[episode.machine_rules[machine_id]]
        phase = metadata.transformation_phases[machine_id]
        preserve = tuple(candidates_matching_csv(
            episode.public.evidence_files[measurement_filename(machine_id)],
            enumerate_transformation_rules(),
        )) if evidence_level == 2 else ()
        plans = list(islice(universe.evidence_options(
            rule, current, phase, evidence_level, ceiling=ceiling, preserve=preserve,
        ), 24))
        options.append([(plan, evidence_csv(rule, plan.experiments)) for plan in plans])
        current = apply_effect(rule, current, phase)

    selected = None
    for combination in product(*options):
        candidates = {
            machine: universe.candidates(text, ceiling=ceiling)
            for machine, (_, text) in zip(machine_ids, combination)
        }
        analysis = analyze_discovery(
            candidate_rules_by_machine=candidates, initial_artifact=initial,
            target_artifact=current, phase_modulus=episode.public.phase_modulus,
        )
        if analysis.minimum_guaranteed_probes == required_probe_count(metadata.discovery_level):
            selected = combination, candidates, analysis
            break
    if selected is None:
        raise EvidencePlanningError(
            f"paired T1/D{metadata.discovery_level} evidence search could not certify this seed; "
            "choose another seed (no hidden-law reroll or weaker D guarantee was applied)"
        )
    combination, candidates, analysis = selected
    episode.public.evidence_files = {
        "facility_manual.txt": SPEC.manual(), "theory.json": SPEC.public_json(),
        **{measurement_filename(machine): text
           for machine, (_, text) in zip(machine_ids, combination)},
    }
    episode.public.episode_id = canonical_hash([episode.public.episode_id, "theory", 1])[:16]
    metadata.theory_level = 1
    metadata.candidate_rules_before_evidence = len(universe.behaviors)
    metadata.evidence_candidate_counts = {
        machine: plan.candidate_count for machine, (plan, _) in zip(machine_ids, combination)
    }
    metadata.evidence_rows_by_machine = {
        machine: len(plan.experiments) for machine, (plan, _) in zip(machine_ids, combination)
    }
    metadata.mission_relevant_prediction_counts = {
        machine: plan.prediction_count for machine, (plan, _) in zip(machine_ids, combination)
    }
    metadata.candidate_rules_after_evidence = metadata.evidence_candidate_counts["M1"]
    metadata.evidence_rows = metadata.evidence_rows_by_machine["M1"]
    metadata.direct_target_example = any(plan.direct_target_example for plan, _ in combination)
    metadata.viable_causal_hypotheses = analysis.viable_hypothesis_count
    episode.public.initial_state.resources.actions_remaining = GENERATION_SOLVER_BUDGET
    policy = solve_guaranteed_policy(
        episode, candidate_rules_by_machine=candidates,
        max_actions=GENERATION_SOLVER_BUDGET, include_action_values=False,
    )
    if not policy.solvable or policy.optimal_worst_case_actions is None or policy.witness is None:
        raise EvidencePlanningError("T1 evidence has no certified exact action policy")
    metadata.guaranteed_policy_action_count = policy.optimal_worst_case_actions
    metadata.guaranteed_policy_witness = policy.witness.model_dump(mode="json")
    metadata.resource_allowance = resource_allowance(len(episode.public.rooms), 0)
    metadata.action_budget = policy.optimal_worst_case_actions + metadata.resource_allowance
    metadata.recommended_tool_call_limit = recommended_tool_call_limit(
        metadata.action_budget, len(episode.public.evidence_files),
    )
    episode.public.initial_state.resources.actions_remaining = metadata.action_budget
    return episode
