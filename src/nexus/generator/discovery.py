from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from nexus.engine.rules import apply_effect
from nexus.generator.difficulty import artifact_projection
from nexus.models.rules import Effect
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape


ArtifactKey = tuple[str, str, str, int, str]


@dataclass(frozen=True)
class ExperimentAnalysis:
    """Root-state classification of one legal probe context."""

    machine_id: str
    phase: int
    outcome_count: int
    discriminative: bool
    mission_relevant: bool
    worst_case_remaining_probes: int | None


@dataclass(frozen=True)
class CommitmentAnalysis:
    """Root-state classification of one irreversible operate context."""

    machine_id: str
    phase: int
    outcome_count: int
    guaranteed_safe: bool
    risky: bool
    worst_case_remaining_probes: int | None


@dataclass(frozen=True)
class DiscoveryAnalysis:
    viable_hypothesis_count: int
    minimum_guaranteed_probes: int | None
    experiments: tuple[ExperimentAnalysis, ...] = ()
    commitments: tuple[CommitmentAnalysis, ...] = ()


def _artifact_key(artifact: Artifact) -> ArtifactKey:
    return (
        artifact.shape.value,
        artifact.pattern.value,
        artifact.orientation.value,
        artifact.value,
        artifact.polarity.value,
    )


def _artifact_from_key(key: ArtifactKey) -> Artifact:
    shape, pattern, orientation, value, polarity = key
    return Artifact(
        id="belief-artifact",
        location="@inventory",
        shape=Shape(shape),
        pattern=Pattern(pattern),
        orientation=Orientation(orientation),
        value=value,
        polarity=Polarity(polarity),
    )


def analyze_discovery(
    *,
    candidate_rules_by_machine: dict[str, list[Effect]],
    initial_artifact: Artifact,
    target_artifact: Artifact,
    phase_modulus: int,
) -> DiscoveryAnalysis:
    """Analyze guaranteed causal discovery and root experiment quality.

    Every rule combination consistent with public evidence is a possible causal world. Worlds
    that cannot reach the public target at all are discarded because generated NEXUS episodes
    separately guarantee physical winnability. The search then computes the minimum worst-case
    number of probes required by a policy that guarantees the target across the remaining worlds.

    Probe/operate observations both partition belief. An irreversible operation is therefore not
    treated as hidden information, but it is safe only when every possible observed branch still
    admits a guaranteed winning continuation.

    Root probe contexts are additionally classified:
    - discriminative: surviving hypotheses predict more than one observable outcome;
    - mission-relevant: taking the probe can strictly reduce the worst-case number of additional
      probes required by an optimal guaranteed policy;
    - otherwise it may reveal the hidden law while being irrelevant to completing this mission.

    These are epistemic guarantees, not engine gates. An agent may always guess and get lucky.
    """
    machine_ids = tuple(sorted(candidate_rules_by_machine))
    if not machine_ids:
        return DiscoveryAnalysis(
            viable_hypothesis_count=0,
            minimum_guaranteed_probes=None,
        )
    if any(not candidate_rules_by_machine[machine_id] for machine_id in machine_ids):
        return DiscoveryAnalysis(
            viable_hypothesis_count=0,
            minimum_guaranteed_probes=None,
        )

    hypotheses = tuple(
        dict(zip(machine_ids, rules))
        for rules in product(*(candidate_rules_by_machine[machine_id] for machine_id in machine_ids))
    )
    target_projection = artifact_projection(target_artifact)

    @lru_cache(maxsize=None)
    def known_reachable(
        hypothesis_index: int,
        artifact_key: ArtifactKey,
        remaining: tuple[str, ...],
    ) -> bool:
        artifact = _artifact_from_key(artifact_key)
        if artifact_projection(artifact) == target_projection:
            return True
        if not remaining:
            return False

        hypothesis = hypotheses[hypothesis_index]
        for machine_id in remaining:
            next_remaining = tuple(item for item in remaining if item != machine_id)
            for phase in range(phase_modulus):
                transformed = apply_effect(hypothesis[machine_id], artifact, phase)
                if known_reachable(
                    hypothesis_index,
                    _artifact_key(transformed),
                    next_remaining,
                ):
                    return True
        return False

    initial_key = _artifact_key(initial_artifact)
    viable = frozenset(
        index
        for index in range(len(hypotheses))
        if known_reachable(index, initial_key, machine_ids)
    )
    if not viable:
        return DiscoveryAnalysis(
            viable_hypothesis_count=0,
            minimum_guaranteed_probes=None,
        )

    infinity = len(viable) + len(machine_ids) * phase_modulus + 1

    def outcome_groups(
        belief: frozenset[int],
        artifact_key: ArtifactKey,
        machine_id: str,
        phase: int,
    ) -> dict[ArtifactKey, frozenset[int]]:
        artifact = _artifact_from_key(artifact_key)
        groups: dict[ArtifactKey, set[int]] = {}
        for hypothesis_index in belief:
            transformed = apply_effect(
                hypotheses[hypothesis_index][machine_id],
                artifact,
                phase,
            )
            groups.setdefault(_artifact_key(transformed), set()).add(hypothesis_index)
        return {key: frozenset(members) for key, members in groups.items()}

    @lru_cache(maxsize=None)
    def search(
        belief: frozenset[int],
        artifact_key: ArtifactKey,
        remaining: tuple[str, ...],
    ) -> int:
        if artifact_projection(_artifact_from_key(artifact_key)) == target_projection:
            return 0
        if not remaining:
            return infinity

        best = infinity

        # Irreversible operation costs no probes, but its observed output can partition belief.
        for machine_id in remaining:
            next_remaining = tuple(item for item in remaining if item != machine_id)
            for phase in range(phase_modulus):
                groups = outcome_groups(belief, artifact_key, machine_id, phase)

                branch_costs: list[int] = []
                feasible = True
                for output_key, members in groups.items():
                    cost = search(members, output_key, next_remaining)
                    if cost >= infinity:
                        feasible = False
                        break
                    branch_costs.append(cost)
                if feasible:
                    best = min(best, max(branch_costs, default=0))

        # A probe leaves the real artifact and machine uses unchanged, but narrows belief.
        for machine_id in remaining:
            for phase in range(phase_modulus):
                groups = outcome_groups(belief, artifact_key, machine_id, phase)
                if len(groups) <= 1:
                    continue

                branch_costs: list[int] = []
                feasible = True
                for members in groups.values():
                    if members == belief:
                        feasible = False
                        break
                    cost = search(members, artifact_key, remaining)
                    if cost >= infinity:
                        feasible = False
                        break
                    branch_costs.append(cost)
                if feasible:
                    best = min(best, 1 + max(branch_costs, default=0))

        return best

    minimum = search(viable, initial_key, machine_ids)
    minimum_probes = None if minimum >= infinity else minimum

    experiments: list[ExperimentAnalysis] = []
    commitments: list[CommitmentAnalysis] = []

    for machine_id in machine_ids:
        next_remaining = tuple(item for item in machine_ids if item != machine_id)
        for phase in range(phase_modulus):
            groups = outcome_groups(viable, initial_key, machine_id, phase)

            probe_costs = [
                search(members, initial_key, machine_ids)
                for members in groups.values()
            ]
            probe_feasible = all(cost < infinity for cost in probe_costs)
            worst_probe_cost = max(probe_costs, default=0) if probe_feasible else None
            discriminative = len(groups) > 1
            mission_relevant = (
                discriminative
                and minimum_probes is not None
                and worst_probe_cost is not None
                and worst_probe_cost < minimum_probes
            )
            experiments.append(
                ExperimentAnalysis(
                    machine_id=machine_id,
                    phase=phase,
                    outcome_count=len(groups),
                    discriminative=discriminative,
                    mission_relevant=mission_relevant,
                    worst_case_remaining_probes=worst_probe_cost,
                )
            )

            operate_costs = [
                search(members, output_key, next_remaining)
                for output_key, members in groups.items()
            ]
            guaranteed_safe = all(cost < infinity for cost in operate_costs)
            worst_operate_cost = (
                max(operate_costs, default=0) if guaranteed_safe else None
            )
            commitments.append(
                CommitmentAnalysis(
                    machine_id=machine_id,
                    phase=phase,
                    outcome_count=len(groups),
                    guaranteed_safe=guaranteed_safe,
                    risky=not guaranteed_safe,
                    worst_case_remaining_probes=worst_operate_cost,
                )
            )

    return DiscoveryAnalysis(
        viable_hypothesis_count=len(viable),
        minimum_guaranteed_probes=minimum_probes,
        experiments=tuple(experiments),
        commitments=tuple(commitments),
    )
