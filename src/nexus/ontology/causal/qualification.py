"""Public-family guarantees; no hidden-world pruning or global minimax claim."""

from functools import lru_cache

from nexus.ontology.causal.inference import indices, partitions, policy_bound, target_set
from nexus.ontology.causal.laws import POINTS, WORLDS, targets
from nexus.ontology.causal.schema import Experiment


@lru_cache(maxsize=1)
def untreated_groups():
    # Includes all legal no-treatment sensors and the complete correction value.
    rows = tuple(partitions(Experiment(point=p)) for p in POINTS)
    groups = {}
    for i, world in enumerate(WORLDS):
        signature = tuple(next(y for y, m in enumerate(row) if m >> i & 1) for row in rows) + (
            world.delta,
        )
        groups[signature] = groups.get(signature, 0) | (1 << i)
    return tuple(groups.values())


def certificate(mask: int, planning: int, allow_preparation: bool = True):
    depth, work = policy_bound(mask, allow_preparation)
    raw = tuple(g & mask for g in untreated_groups() if g & mask)
    ambiguous = sum(len(target_set(g)) > 1 for g in raw)
    return {
        "family": "causal-mechanisms-v1",
        "certificate_version": 2,
        "experimental": True,
        "empirical_difficulty_calibrated": False,
        "prior_worlds": mask.bit_count(),
        "target_classes": len(target_set(mask)),
        "reference_reading_bound": depth,
        "reference_action_bound": depth + work + planning + 2,
        "policy_scope": "greedy public-information subset witness; not global minimax",
        "untreated_observation_classes": len(raw),
        "untreated_ambiguous_classes": ambiguous,
        "untreated_readings_insufficient_for_identification": ambiguous > 0,
        "maximum_specimen_pulses": 2,
        "reference_allows_preparation": allow_preparation,
        "adaptive_advantage_proven": False,
        "construction_scope": "identification from untreated readings before the first eligible submission; excludes rejection feedback and makes no eventual-victory requirement",
        "exact_arithmetic": True,
    }


def certificate_matches(recorded, current):
    """Read original certificates without repeating their ambiguous field name."""
    if recorded == current:
        return True
    legacy = dict(current)
    legacy.pop("certificate_version")
    legacy["construction_required_for_guarantee"] = legacy.pop(
        "untreated_readings_insufficient_for_identification"
    )
    legacy["construction_scope"] = "untreated readings cannot guarantee identification; not a per-truth or optimality claim"
    return recorded == legacy


def qualify_causal(episode):
    from nexus.generator.qualify import QualificationReport
    from nexus.models.episode import PrivateEpisode
    from nexus.ontology.causal.inference import initial_mask
    from nexus.ontology.causal.policy import public_policy
    from nexus.protocol.session import Session

    try:
        # Callers may have mutated a previously valid compiled model in memory.
        episode = PrivateEpisode.model_validate_json(episode.model_dump_json())
    except ValueError as exc:
        return QualificationReport(
            passed=False, checks={"compiled_contract": False}, errors=(str(exc),), metrics={}
        )
    from nexus.models.domain import DomainInvestigation

    if not isinstance(episode.public.investigation, DomainInvestigation):
        return QualificationReport(
            passed=False,
            checks={"ontology": False},
            errors=("not a causal domain episode",),
            metrics={},
        )
    spec = episode.public.investigation.data()
    mask = initial_mask(spec)
    proof = certificate(mask, episode.generation_metadata.planning_level, spec.discovery != 2)
    # policy_bound recursively covers every nonempty branch of the admitted prior.
    expected_targets = {targets()[i] for i in indices(mask)}
    result = public_policy(Session(episode), episode.public.evidence_files)
    checks = {
        "nonempty_identifiable_prior": bool(expected_targets),
        "public_policy_wins": result.victory_code is not None,
        "metadata_matches_public_family": certificate_matches(
            episode.generation_metadata.investigation_certificate, proof
        ),
        "D0_resolved": spec.discovery != 0 or len(expected_targets) == 1,
        "D1_single_reading": spec.discovery != 1 or proof["reference_reading_bound"] == 1,
        "D2_combines_measurements": spec.discovery != 2
        or (len(expected_targets) > 3 and not proof["untreated_readings_insufficient_for_identification"]),
        "D5_untreated_identification_insufficient": spec.discovery != 5
        or proof["untreated_readings_insufficient_for_identification"],
    }
    return QualificationReport(
        passed=all(checks.values()),
        checks=checks,
        errors=tuple(k for k, v in checks.items() if not v),
        metrics=proof,
    )
