from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from nexus.engine.rules import apply_effect
from nexus.generator.difficulty import artifact_projection
from nexus.models.rules import Effect
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape


@dataclass(frozen=True)
class DiscoveryAnalysis:
    viable_hypothesis_count: int
    minimum_guaranteed_probes: int | None


def _artifact_key(artifact: Artifact) -> tuple[str, str, str, int, str]:
    return (
        artifact.shape.value,
        artifact.pattern.value,
        artifact.orientation.value,
        artifact.value,
        artifact.polarity.value,
    )


def _artifact_from_key(key: tuple[str, str, str, int, str]) -> Artifact:
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
    """Find the exact probe count for a guaranteed causal strategy.

    The analysis treats every rule combination consistent with public evidence as a possible
    world, then discards combinations that cannot reach the public target at all because NEXUS
    publicly guarantees solver-qualified episodes. A policy may choose phases, probe any
    remaining machine, or irreversibly operate a machine. Both probe and operate outcomes are
    observations, so an operation can reduce uncertainty even though it consumes that machine.

    The returned count is the minimum worst-case number of probes needed to guarantee the target
    across the remaining viable hypotheses. It is an epistemic guarantee, not an engine gate:
    an agent may always guess and can get lucky.
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
        artifact_key: tuple[str, str, str, int, str],
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

    @lru_cache(maxsize=None)
    def search(
        belief: frozenset[int],
        artifact_key: tuple[str, str, str, int, str],
        remaining: tuple[str, ...],
    ) -> int:
        artifact = _artifact_from_key(artifact_key)
        if artifact_projection(artifact) == target_projection:
            return 0
        if not remaining:
            return infinity

        best = infinity

        # Irreversible operation costs no probes, but its observed output can partition belief.
        for machine_id in remaining:
            next_remaining = tuple(item for item in remaining if item != machine_id)
            for phase in range(phase_modulus):
                groups: dict[tuple[str, str, str, int, str], set[int]] = {}
                for hypothesis_index in belief:
                    transformed = apply_effect(
                        hypotheses[hypothesis_index][machine_id],
                        artifact,
                        phase,
                    )
                    groups.setdefault(_artifact_key(transformed), set()).add(hypothesis_index)

                branch_costs: list[int] = []
                feasible = True
                for output_key, members in groups.items():
                    cost = search(frozenset(members), output_key, next_remaining)
                    if cost >= infinity:
                        feasible = False
                        break
                    branch_costs.append(cost)
                if feasible:
                    best = min(best, max(branch_costs, default=0))

        # A probe leaves the real artifact and machine uses unchanged, but narrows the belief.
        for machine_id in remaining:
            for phase in range(phase_modulus):
                groups: dict[tuple[str, str, str, int, str], set[int]] = {}
                for hypothesis_index in belief:
                    transformed = apply_effect(
                        hypotheses[hypothesis_index][machine_id],
                        artifact,
                        phase,
                    )
                    groups.setdefault(_artifact_key(transformed), set()).add(hypothesis_index)

                if len(groups) <= 1:
                    continue

                branch_costs = []
                feasible = True
                for members in groups.values():
                    narrowed = frozenset(members)
                    if narrowed == belief:
                        feasible = False
                        break
                    cost = search(narrowed, artifact_key, remaining)
                    if cost >= infinity:
                        feasible = False
                        break
                    branch_costs.append(cost)
                if feasible:
                    best = min(best, 1 + max(branch_costs, default=0))

        return best

    minimum = search(viable, initial_key, machine_ids)
    return DiscoveryAnalysis(
        viable_hypothesis_count=len(viable),
        minimum_guaranteed_probes=None if minimum >= infinity else minimum,
    )
