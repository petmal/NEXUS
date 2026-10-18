"""Terminal-only diagnostics for axes-v2; no metric is a player hint during play."""

import logging
from collections import Counter

from pydantic import BaseModel, ConfigDict, Field, model_serializer

from nexus.ontology.catalog import runtime_for
from nexus.ontology.mission import final_acceptance, tracker_for
from nexus.models.domain import DomainInvestigation
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.models.world import WorldState
from nexus.protocol.decision_metrics import DecisionAuditTrail, DecisionDiagnostics

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


class DecisionMissionPerformance(MissionPerformance):
    """Overlapping goals: resolution means a common accepted decision exists."""

    version: str = "mission-performance-v2"
    target_count_meaning: str = "distinct winning-set signatures; not exclusive target classes"
    target_reducing_measurements: int = Field(description="Measurements reducing the number of distinct winning-set signatures; this is not guaranteed-repair progress.")
    measurements_establishing_guaranteed_repair: int
    common_repairs_before_first_submission: int | None
    first_submission_supported_by_evidence: bool | None
    measurements_after_guaranteed_repair: int


class AuditedDecisionMissionPerformance(DecisionMissionPerformance):
    """Add classifications while retaining the parser for existing v2 artifacts."""

    version: str = "mission-performance-v3"
    decision_diagnostics: DecisionDiagnostics


def summarize(
    episode: PrivateEpisode,
    state: WorldState,
    trace: list[TraceRecord],
    *,
    invalid: int,
    duplicates: int,
    conflicts: int,
    extended: bool = False,
) -> InvestigationPerformance | MissionPerformance:
    spec = episode.public.investigation
    certificate = episode.generation_metadata.investigation_certificate
    if spec is None or certificate is None:
        raise ValueError("scientific diagnostics require an investigation and certificate")
    runtime = runtime_for(spec)
    posterior = runtime.belief(spec)
    expected = runtime.expected(episode)
    measurements = informative = target_reducing = submissions = failed = 0
    calibration_count = no_signal_count = after_resolved_count = 0
    established_repair_count = 0
    first_correct = first_classes = None
    first_common = first_supported = None
    decision_semantics = callable(getattr(posterior, "common_decisions", None))
    audited_decisions = (
        decision_semantics
        and callable(getattr(posterior, "accepting_count", None))
        and callable(getattr(runtime, "measurement_features", None))
    )
    decision_audit = DecisionAuditTrail(posterior) if audited_decisions else None
    tracker = tracker_for(runtime, episode)
    for record in trace:
        action = record.action
        tracker.observe(record)
        if action.type == "finish":
            if decision_audit is not None:
                decision_audit.submission(record, posterior, tracker.attempted())
            submissions += 1
            correct = record.terminal_status.value == "won"
            if first_correct is None:
                first_correct = correct
                first_classes = posterior.counts()[1]
                if decision_semantics:
                    first_common = len(posterior.common_decisions())
                    first_supported = posterior.supports(tracker.attempted())
            failed += not correct
            attempted = tracker.attempted()
            if not correct and attempted is not None:
                # Only a physically eligible complete decision is excluded.
                # A wrong room/missing specimen must not falsify its values.
                posterior.exclude_target(attempted)
                if decision_audit is not None:
                    decision_audit.after_evidence(record.turn, posterior)
        measurement = runtime.measurement(record)
        if measurement is None:
            continue
        before, before_targets = posterior.counts()
        calibration_count += measurement.calibration
        no_signal_count += measurement.no_signal
        before_resolved = bool(posterior.common_decisions()) if decision_semantics else before_targets == 1
        after_resolved_count += before_resolved
        posterior.observe(measurement)
        if decision_audit is not None:
            decision_audit.measurement(
                record, posterior, before, runtime.measurement_features(measurement)
            )
        after, after_targets = posterior.counts()
        if decision_semantics:
            established_repair_count += not before_resolved and bool(posterior.common_decisions())
        measurements += 1
        informative += after < before
        target_reducing += after_targets < before_targets
    final_settings = runtime.submitted(state) or ()
    matches = sum(left == right for left, right in zip(final_settings[1:], expected[1:]))
    runtime.log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes)
    terminal_belief_logger = getattr(runtime, "log_terminal_belief", None)
    if terminal_belief_logger is not None:
        terminal_belief_logger(posterior)
    trace_logger = getattr(runtime, "log_terminal_trace", None)
    if trace_logger is not None:
        trace_logger(state, trace, posterior)
    if runtime.performance_style == "mission":
        if not isinstance(spec, DomainInvestigation):
            raise ValueError("mission adapter requires a domain investigation")
        final_correct = final_acceptance(runtime, episode, state)
        if final_correct is None:
            raise ValueError("mission adapter did not provide an acceptance predicate")
        if decision_semantics:
            logging.getLogger("nexus.diagnostics").info(
                "decision_terminal ontology=%s common_repairs_before_first_submission=%s first_submission_supported=%s after_guaranteed_repair=%s",
                spec.ontology, first_common, first_supported, after_resolved_count,
            )
        performance_type = (
            AuditedDecisionMissionPerformance if audited_decisions else
            DecisionMissionPerformance if decision_semantics else MissionPerformance
        )
        decision_fields = {
            "measurements_establishing_guaranteed_repair": established_repair_count,
            "common_repairs_before_first_submission": first_common,
            "first_submission_supported_by_evidence": first_supported,
            "measurements_after_guaranteed_repair": after_resolved_count,
        } if decision_semantics else {}
        if decision_audit is not None:
            decision_fields["decision_diagnostics"] = decision_audit.summary(
                posterior, tracker.attempted(), won=state.terminal_status.value == "won",
                physical_goal=final_correct, extended=extended,
            )
        return performance_type(
            **decision_fields,
            ontology=spec.ontology, experimental=spec.data().experimental,
            terminal_status=state.terminal_status.value,
            termination_reason="victory" if state.terminal_status.value == "won" else
                "action_budget" if state.resources.actions_remaining == 0 else
                "active_at_snapshot" if state.terminal_status.value == "active" else "harness_finalization",
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
            final_submission_correct=final_correct,
            invalid_actions=invalid, duplicate_requests=duplicates, protocol_conflicts=conflicts,
            certificate=certificate,
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
        else "active_at_snapshot"
        if state.terminal_status.value == "active"
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
        certificate=certificate,
    )
