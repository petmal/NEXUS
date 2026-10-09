"""Terminal-only diagnostics for axes-v2; no metric is a player hint during play."""

from collections import Counter

from pydantic import BaseModel, ConfigDict, Field, model_serializer

from nexus.engine.investigation import settings
from nexus.generator.investigation import prior
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


def summarize(
    episode: PrivateEpisode,
    state: WorldState,
    trace: list[TraceRecord],
    *,
    invalid: int,
    duplicates: int,
    conflicts: int,
) -> InvestigationPerformance:
    spec = episode.public.investigation
    worlds, problem = prior(episode)
    belief = set(problem.compatible(spec.supplied_measurements))
    expected = settings(spec, episode.investigation_truth)
    predictions = tuple(settings(spec, world) for world in worlds)
    if spec.resolved_settings is not None:
        belief = {i for i in belief if predictions[i] == spec.resolved_settings}
    measurements = informative = target_reducing = submissions = failed = 0
    first_correct = first_classes = None
    current_settings = None
    room = episode.public.initial_state.agent_room
    rows = dict(problem.experiments)
    for record in trace:
        action = record.action
        if action.type == "move":
            room = action.target
        elif action.type == "configure":
            current_settings = action.settings
        elif action.type == "finish":
            submissions += 1
            correct = current_settings == expected and room == spec.controller_room
            if first_correct is None:
                first_correct = correct
                first_classes = len({predictions[i] for i in belief})
            failed += not correct
            # An unsuccessful submission in the correct room rules out that complete vector.
            # It is evidence, but never counted as a scientific measurement.
            if not correct and room == spec.controller_room:
                belief = {i for i in belief if predictions[i] != current_settings}
        if action.type not in ("probe", "operate") or action.machine not in (
            "meter",
            "selector",
            "material",
        ):
            continue
        result = record.events[-1].details.get("result")
        # Budget exhaustion can append a second event; locate the actual result explicitly.
        result = next(
            (event.details["result"] for event in record.events if "result" in event.details),
            result,
        )
        if result is None:
            continue
        sample = result["sample"]
        name = (f"{sample['x']}:{sample['y']}" if "x" in sample else
            "selector"
            if action.machine == "selector"
            else f"{sample['source']}:property"
            if action.machine == "material"
            else f"{sample['source']}:{sample['q']}"
        )
        if name not in rows:
            raise RuntimeError("runtime produced a measurement missing from the certified prior")
        before = len(belief)
        before_targets = len({predictions[i] for i in belief})
        belief = {i for i in belief if rows[name][i] == sample["reading"]}
        measurements += 1
        informative += len(belief) < before
        target_reducing += len({predictions[i] for i in belief}) < before_targets
    final_settings = state.controller_settings or ()
    matches = sum(left == right for left, right in zip(final_settings[1:], expected[1:]))
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
