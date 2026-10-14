"""Terminal-only diagnostics for axes-v2; no metric is a player hint during play."""

from collections import Counter

from pydantic import BaseModel, ConfigDict, Field, model_serializer

from nexus.ontology.catalog import runtime_for
from nexus.ontology.mission import final_acceptance, tracker_for
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.models.world import WorldState

SCIENCE_SCHEMA_URL = (
    "https://raw.githubusercontent.com/petmal/NEXUS/"
    "dd6564d848183d9f70eca474a6ef02c5ab84a58e/schemas/performance-scientific-v1.schema.json"
)


class InvestigationPerformance(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, populate_by_name=True, serialize_by_alias=True
    )
    schema_url: str = Field(default=SCIENCE_SCHEMA_URL, alias="$schema")
    axis_version: int = 2
    theory_level: int
    discovery_level: int
    planning_level: int
    resource_pressure: int
    terminal_status: str
    termination_reason: str
    actions_used: int
    initial_action_budget: int | None
    budget_remaining: int | None
    action_counts: dict[str, int]
    measurements_used: int
    informative_measurements: int
    target_reducing_measurements: int
    redundant_measurements: int
    target_classes_before_first_submission: int | None
    first_submission_correct: bool | None
    controller_submissions: int
    failed_finishes: int
    final_correct_field_values: int
    field_value_count: int
    final_port_correct: bool
    invalid_actions: int
    duplicate_requests: int
    protocol_conflicts: int
    certificate: dict[str, object]

    @model_serializer(mode="wrap")
    def preserve_semantic_nulls(self, handler):
        result = handler(self)
        for name, field in type(self).model_fields.items():
            if getattr(self, name) is None:
                result[field.alias or name] = None
        return result


class MissionPerformance(BaseModel):
    """Ontology-neutral terminal projection; no legacy controller/port assumptions."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: str = "mission-performance-v1"
    ontology: str
    experimental: bool
    terminal_status: str
    termination_reason: str
    actions_used: int
    initial_action_budget: int | None
    budget_remaining: int | None
    action_counts: dict[str, int]
    measurements_used: int
    informative_measurements: int
    target_reducing_measurements: int
    redundant_measurements: int
    target_classes_before_first_submission: int | None
    first_submission_correct: bool | None
    mission_submissions: int
    failed_finishes: int
    final_submission_correct: bool
    invalid_actions: int
    duplicate_requests: int
    protocol_conflicts: int
    certificate: dict[str, object]

    @model_serializer(mode="wrap")
    def preserve_semantic_nulls(self, handler):
        result = handler(self)
        for name in type(self).model_fields:
            if getattr(self, name) is None:
                result[name] = None
        return result


def summarize(
    episode: PrivateEpisode,
    state: WorldState,
    trace: list[TraceRecord],
    *,
    invalid: int,
    duplicates: int,
    conflicts: int,
) -> InvestigationPerformance | MissionPerformance:
    spec = episode.public.investigation
    runtime = runtime_for(spec)
    posterior = runtime.belief(spec)
    expected = runtime.expected(episode)
    measurements = informative = target_reducing = submissions = failed = 0
    calibration_count = no_signal_count = after_resolved_count = 0
    first_correct = first_classes = None
    tracker = tracker_for(runtime, episode)
    for record in trace:
        action = record.action
        tracker.observe(record)
        if action.type == "finish":
            submissions += 1
            correct = record.terminal_status.value == "won"
            if first_correct is None:
                first_correct = correct
                first_classes = posterior.counts()[1]
            failed += not correct
            attempted = tracker.attempted()
            if not correct and attempted is not None:
                # Only a physically eligible complete decision is excluded.
                # A wrong room/missing specimen must not falsify its values.
                posterior.exclude_target(attempted)
        measurement = runtime.measurement(record)
        if measurement is None:
            continue
        before, before_targets = posterior.counts()
        calibration_count += measurement.calibration
        no_signal_count += measurement.no_signal
        after_resolved_count += before_targets == 1
        posterior.observe(measurement)
        after, after_targets = posterior.counts()
        measurements += 1
        informative += after < before
        target_reducing += after_targets < before_targets
    final_settings = runtime.submitted(state) or ()
    matches = sum(left == right for left, right in zip(final_settings[1:], expected[1:]))
    runtime.log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes)
    if runtime.performance_style == "mission":
        return MissionPerformance(
            ontology=spec.ontology, experimental=spec.data().experimental,
            terminal_status=state.terminal_status.value,
            termination_reason="victory" if state.terminal_status.value == "won" else
                "action_budget" if state.resources.actions_remaining == 0 else "harness_finalization",
            actions_used=state.turn,
            initial_action_budget=episode.public.initial_state.resources.actions_remaining,
            budget_remaining=state.resources.actions_remaining,
            action_counts=dict(Counter(record.action.type for record in trace)),
            measurements_used=measurements, informative_measurements=informative,
            target_reducing_measurements=target_reducing,
            redundant_measurements=measurements-informative,
            target_classes_before_first_submission=first_classes,
            first_submission_correct=first_correct, mission_submissions=submissions,
            failed_finishes=failed,
            final_submission_correct=final_acceptance(runtime, episode, state),
            invalid_actions=invalid, duplicate_requests=duplicates, protocol_conflicts=conflicts,
            certificate=episode.generation_metadata.investigation_certificate,
        )
    return InvestigationPerformance(
        theory_level=spec.theory,
        discovery_level=spec.discovery,
        planning_level=episode.generation_metadata.planning_level,
        resource_pressure=episode.generation_metadata.resource_pressure,
        terminal_status=state.terminal_status.value,
        termination_reason="victory"
        if state.terminal_status.value == "won"
        else "action_budget"
        if state.resources.actions_remaining == 0
        else "harness_finalization",
        actions_used=state.turn,
        initial_action_budget=episode.public.initial_state.resources.actions_remaining,
        budget_remaining=state.resources.actions_remaining,
        action_counts=dict(Counter(record.action.type for record in trace)),
        measurements_used=measurements,
        informative_measurements=informative,
        target_reducing_measurements=target_reducing,
        redundant_measurements=measurements - informative,
        target_classes_before_first_submission=first_classes,
        first_submission_correct=first_correct,
        controller_submissions=submissions,
        failed_finishes=failed,
        final_correct_field_values=matches,
        field_value_count=len(expected) - 1,
        final_port_correct=bool(final_settings) and final_settings[0] == expected[0],
        invalid_actions=invalid,
        duplicate_requests=duplicates,
        protocol_conflicts=conflicts,
        certificate=episode.generation_metadata.investigation_certificate,
    )
