from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from nexus.engine.engine import step
from nexus.engine.rules import apply_effect
from nexus.generator.difficulty import artifact_projection
from nexus.generator.evidence import candidates_matching_csv, measurement_filename
from nexus.generator.rules import enumerate_transformation_rules
from nexus.models.actions import OperateAction, ProbeAction
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.rules import Effect
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape


ArtifactKey = tuple[str, str, str, int, str]


@dataclass(frozen=True)
class ExperimentAnalysis:
    """Classification of one legal probe context for the current belief state."""

    machine_id: str
    phase: int
    outcome_count: int
    discriminative: bool
    mission_relevant: bool
    worst_case_remaining_probes: int | None


@dataclass(frozen=True)
class CommitmentAnalysis:
    """Classification of one irreversible operate context for the current belief state."""

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


class DiscoveryBelief:
    """Exact causal belief state for the current single-artifact discovery problem.

    The tracker preserves complete rule-combination hypotheses rather than independently narrowing
    each machine. This matters after observations because public-goal viability can correlate
    otherwise independent machine rules.

    It intentionally models only causal information and machine consumption; physical navigation,
    inventory logistics, and action costs remain the responsibility of the concrete solver. Later
    belief-policy milestones can compose those concerns without weakening this exact causal layer.
    """

    def __init__(
        self,
        *,
        candidate_rules_by_machine: dict[str, list[Effect]],
        initial_artifact: Artifact,
        target_artifact: Artifact,
        phase_modulus: int,
    ):
        if phase_modulus < 1:
            raise ValueError("phase_modulus must be at least 1")

        self.machine_ids = tuple(sorted(candidate_rules_by_machine))
        self.phase_modulus = phase_modulus
        self.target_projection = artifact_projection(target_artifact)
        self.artifact_key = _artifact_key(initial_artifact)
        self.remaining = self.machine_ids

        if not self.machine_ids or any(
            not candidate_rules_by_machine[machine_id] for machine_id in self.machine_ids
        ):
            self.hypotheses: tuple[dict[str, Effect], ...] = ()
            self.belief = frozenset()
            self.infinity = 1
            return

        self.hypotheses = tuple(
            dict(zip(self.machine_ids, rules))
            for rules in product(
                *(candidate_rules_by_machine[machine_id] for machine_id in self.machine_ids)
            )
        )
        viable = frozenset(
            index
            for index in range(len(self.hypotheses))
            if self._known_reachable(index, self.artifact_key, self.machine_ids)
        )
        self.belief = viable
        self.infinity = len(viable) + len(self.machine_ids) * phase_modulus + 1

    @lru_cache(maxsize=None)
    def _known_reachable(
        self,
        hypothesis_index: int,
        artifact_key: ArtifactKey,
        remaining: tuple[str, ...],
    ) -> bool:
        artifact = _artifact_from_key(artifact_key)
        if artifact_projection(artifact) == self.target_projection:
            return True
        if not remaining:
            return False

        hypothesis = self.hypotheses[hypothesis_index]
        for machine_id in remaining:
            next_remaining = tuple(item for item in remaining if item != machine_id)
            for phase in range(self.phase_modulus):
                transformed = apply_effect(hypothesis[machine_id], artifact, phase)
                if self._known_reachable(
                    hypothesis_index,
                    _artifact_key(transformed),
                    next_remaining,
                ):
                    return True
        return False

    def _outcome_groups(
        self,
        belief: frozenset[int],
        artifact_key: ArtifactKey,
        machine_id: str,
        phase: int,
    ) -> dict[ArtifactKey, frozenset[int]]:
        artifact = _artifact_from_key(artifact_key)
        groups: dict[ArtifactKey, set[int]] = {}
        for hypothesis_index in belief:
            transformed = apply_effect(
                self.hypotheses[hypothesis_index][machine_id],
                artifact,
                phase,
            )
            groups.setdefault(_artifact_key(transformed), set()).add(hypothesis_index)
        return {key: frozenset(members) for key, members in groups.items()}

    @lru_cache(maxsize=None)
    def _search(
        self,
        belief: frozenset[int],
        artifact_key: ArtifactKey,
        remaining: tuple[str, ...],
    ) -> int:
        if artifact_projection(_artifact_from_key(artifact_key)) == self.target_projection:
            return 0
        if not remaining:
            return self.infinity

        best = self.infinity

        # Irreversible operation costs no probes, but the output is observable and can narrow
        # belief. It is usable in a guaranteed policy only when every possible branch remains
        # winnable after consuming that machine.
        for machine_id in remaining:
            next_remaining = tuple(item for item in remaining if item != machine_id)
            for phase in range(self.phase_modulus):
                groups = self._outcome_groups(belief, artifact_key, machine_id, phase)
                branch_costs: list[int] = []
                feasible = True
                for output_key, members in groups.items():
                    cost = self._search(members, output_key, next_remaining)
                    if cost >= self.infinity:
                        feasible = False
                        break
                    branch_costs.append(cost)
                if feasible:
                    best = min(best, max(branch_costs, default=0))

        # A probe preserves the physical artifact and machine uses while revealing the
        # hypothetical output, so only belief changes.
        for machine_id in remaining:
            for phase in range(self.phase_modulus):
                groups = self._outcome_groups(belief, artifact_key, machine_id, phase)
                if len(groups) <= 1:
                    continue

                branch_costs: list[int] = []
                feasible = True
                for members in groups.values():
                    if members == belief:
                        feasible = False
                        break
                    cost = self._search(members, artifact_key, remaining)
                    if cost >= self.infinity:
                        feasible = False
                        break
                    branch_costs.append(cost)
                if feasible:
                    best = min(best, 1 + max(branch_costs, default=0))

        return best

    def analysis(self) -> DiscoveryAnalysis:
        if not self.belief:
            return DiscoveryAnalysis(
                viable_hypothesis_count=0,
                minimum_guaranteed_probes=None,
            )

        minimum = self._search(self.belief, self.artifact_key, self.remaining)
        minimum_probes = None if minimum >= self.infinity else minimum

        experiments: list[ExperimentAnalysis] = []
        commitments: list[CommitmentAnalysis] = []

        for machine_id in self.remaining:
            next_remaining = tuple(item for item in self.remaining if item != machine_id)
            for phase in range(self.phase_modulus):
                groups = self._outcome_groups(
                    self.belief,
                    self.artifact_key,
                    machine_id,
                    phase,
                )

                probe_costs = [
                    self._search(members, self.artifact_key, self.remaining)
                    for members in groups.values()
                ]
                probe_feasible = all(cost < self.infinity for cost in probe_costs)
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
                    self._search(members, output_key, next_remaining)
                    for output_key, members in groups.items()
                ]
                guaranteed_safe = all(cost < self.infinity for cost in operate_costs)
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
            viable_hypothesis_count=len(self.belief),
            minimum_guaranteed_probes=minimum_probes,
            experiments=tuple(experiments),
            commitments=tuple(commitments),
        )

    def _members_for_observation(
        self,
        *,
        machine_id: str,
        phase: int,
        observed_artifact: Artifact,
    ) -> frozenset[int]:
        if machine_id not in self.remaining:
            raise ValueError(f"machine {machine_id!r} is not available in the causal belief state")
        if not 0 <= phase < self.phase_modulus:
            raise ValueError(f"phase {phase} is outside the configured phase cycle")

        observed_key = _artifact_key(observed_artifact)
        groups = self._outcome_groups(
            self.belief,
            self.artifact_key,
            machine_id,
            phase,
        )
        members = groups.get(observed_key, frozenset())
        if not members:
            raise ValueError("observed outcome is inconsistent with every viable causal hypothesis")
        return members

    def observe_probe(
        self,
        *,
        machine_id: str,
        phase: int,
        observed_artifact: Artifact,
    ) -> None:
        self.belief = self._members_for_observation(
            machine_id=machine_id,
            phase=phase,
            observed_artifact=observed_artifact,
        )

    def observe_operate(
        self,
        *,
        machine_id: str,
        phase: int,
        observed_artifact: Artifact,
    ) -> None:
        self.belief = self._members_for_observation(
            machine_id=machine_id,
            phase=phase,
            observed_artifact=observed_artifact,
        )
        self.artifact_key = _artifact_key(observed_artifact)
        self.remaining = tuple(item for item in self.remaining if item != machine_id)


def analyze_discovery(
    *,
    candidate_rules_by_machine: dict[str, list[Effect]],
    initial_artifact: Artifact,
    target_artifact: Artifact,
    phase_modulus: int,
) -> DiscoveryAnalysis:
    """Analyze guaranteed causal discovery and current experiment quality.

    This convenience entry point returns the initial-state analysis. Use :class:`DiscoveryBelief`
    when observations must be incorporated sequentially while preserving correlations among
    evidence-consistent machine-rule combinations.
    """
    return DiscoveryBelief(
        candidate_rules_by_machine=candidate_rules_by_machine,
        initial_artifact=initial_artifact,
        target_artifact=target_artifact,
        phase_modulus=phase_modulus,
    ).analysis()



@dataclass(frozen=True)
class CausalDecisionTrace:
    """Epistemic classification of a probe/operate at the moment the agent took it."""

    turn_before: int
    action_type: str
    machine_id: str
    artifact_id: str
    phase: int
    viable_hypotheses_before: int
    minimum_guaranteed_probes_before: int | None
    discriminative: bool | None = None
    mission_relevant: bool | None = None
    guaranteed_safe: bool | None = None
    risky: bool | None = None


def _target_artifact_from_public_goal(episode: PrivateEpisode, artifact_id: str) -> Artifact:
    """Recover the public target projection without consulting latent rules or reference plans."""
    source = episode.public.initial_state.artifacts[artifact_id].model_copy(
        update={"location": "@inventory"}
    )
    updates: dict[str, object] = {}

    def visit(predicate: GoalPredicate) -> None:
        if (
            predicate.kind == GoalKind.ARTIFACT_FIELD
            and predicate.artifact_id == artifact_id
            and predicate.field is not None
        ):
            updates[predicate.field] = predicate.value
        for child in predicate.children:
            visit(child)

    visit(episode.public.goal)
    return Artifact.model_validate(source.model_copy(update=updates).model_dump())


def analyze_causal_trace(
    episode: PrivateEpisode,
    trace: tuple[TraceRecord, ...] | list[TraceRecord],
    *,
    artifact_id: str = "A1",
) -> tuple[CausalDecisionTrace, ...]:
    """Label causal decisions using only information available before each decision.

    The trusted private episode is used to replay accepted state transitions because compact trace
    records store hashes/events rather than complete state snapshots. Causal classification never
    consults the selected hidden rule directly: its hypothesis set comes from public evidence and
    its target comes from the public goal. Each observed probe/operate result then narrows that
    hypothesis set exactly as it would for the player.
    """
    catalog = enumerate_transformation_rules()
    candidate_rules_by_machine: dict[str, list[Effect]] = {}
    for machine_id in sorted(episode.public.initial_state.machines):
        filename = measurement_filename(machine_id)
        evidence = episode.public.evidence_files.get(filename)
        if evidence is None:
            raise ValueError(f"missing public evidence for machine {machine_id}")
        candidate_rules_by_machine[machine_id] = candidates_matching_csv(evidence, catalog)

    belief = DiscoveryBelief(
        candidate_rules_by_machine=candidate_rules_by_machine,
        initial_artifact=episode.public.initial_state.artifacts[artifact_id],
        target_artifact=_target_artifact_from_public_goal(episode, artifact_id),
        phase_modulus=episode.public.phase_modulus,
    )
    state = episode.public.initial_state.model_copy(deep=True)
    decisions: list[CausalDecisionTrace] = []

    for record in trace:
        action = record.action
        before_phase = state.phase
        before_turn = state.turn

        if isinstance(action, ProbeAction):
            analysis = belief.analysis()
            experiment = next(
                (
                    item
                    for item in analysis.experiments
                    if item.machine_id == action.machine and item.phase == before_phase
                ),
                None,
            )
            if experiment is None:
                raise ValueError("trace probe is unavailable in the causal belief state")
            decisions.append(
                CausalDecisionTrace(
                    turn_before=before_turn,
                    action_type="probe",
                    machine_id=action.machine,
                    artifact_id=action.artifact,
                    phase=before_phase,
                    viable_hypotheses_before=analysis.viable_hypothesis_count,
                    minimum_guaranteed_probes_before=analysis.minimum_guaranteed_probes,
                    discriminative=experiment.discriminative,
                    mission_relevant=experiment.mission_relevant,
                )
            )

        elif isinstance(action, OperateAction):
            analysis = belief.analysis()
            commitment = next(
                (
                    item
                    for item in analysis.commitments
                    if item.machine_id == action.machine and item.phase == before_phase
                ),
                None,
            )
            if commitment is None:
                raise ValueError("trace operation is unavailable in the causal belief state")
            decisions.append(
                CausalDecisionTrace(
                    turn_before=before_turn,
                    action_type="operate",
                    machine_id=action.machine,
                    artifact_id=action.artifact,
                    phase=before_phase,
                    viable_hypotheses_before=analysis.viable_hypothesis_count,
                    minimum_guaranteed_probes_before=analysis.minimum_guaranteed_probes,
                    guaranteed_safe=commitment.guaranteed_safe,
                    risky=commitment.risky,
                )
            )

        result = step(state, action, episode)
        if not result.ok:
            raise ValueError(f"trace contains invalid accepted action at turn {record.turn}")

        if isinstance(action, ProbeAction):
            probe_event = next((event for event in result.events if event.type == "probe"), None)
            if probe_event is None:
                raise ValueError("probe trace step did not emit a probe result")
            observed = Artifact.model_validate(probe_event.details["result"])
            belief.observe_probe(
                machine_id=action.machine,
                phase=before_phase,
                observed_artifact=observed,
            )
        elif isinstance(action, OperateAction):
            observed = result.state.artifacts[action.artifact]
            belief.observe_operate(
                machine_id=action.machine,
                phase=before_phase,
                observed_artifact=observed,
            )

        state = result.state

    return tuple(decisions)
