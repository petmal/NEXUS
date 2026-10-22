"""Canonical runtime integration shared by two explicit scientific domains."""

import logging
from dataclasses import dataclass

from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    OperateAction,
    TakeAction,
    action_contract,
)
from nexus.models.domain import DomainArtifact
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import INVENTORY, Room
from nexus.ontology.discovery.domains import ADAPTERS, module
from nexus.ontology.discovery.schema import Reading, Specimen
from nexus.ontology.inference import Measurement

performance_style = "mission"
requires_single_session = True


def validate_episode(episode):
    from nexus.ontology.discovery.generation import DESCRIPTIONS, initial_state, metadata

    public = episode.public
    family = public.investigation.ontology
    laws = module(family, "laws")
    spec = public.investigation.data()
    world = episode.investigation_truth.data()
    if type(episode.construction_seed) is not int or world != laws.selection(
        episode.construction_seed
    ):
        raise ValueError("discovery truth contradicts seed")
    options_factory = getattr(laws, "generation_options", None)
    rebuilt = (
        laws.specification(world, spec.theory, spec.discovery, options_factory(spec))
        if options_factory is not None
        else laws.specification(world, spec.theory, spec.discovery)
    )
    if spec != rebuilt:
        raise ValueError("discovery disclosure contradicts truth")
    meta = metadata(
        family,
        spec,
        episode.generation_metadata.resource_pressure,
        episode.generation_metadata.budget_profile,
    )
    if (
        episode.generation_metadata != meta
        or public.description != DESCRIPTIONS[family]
        or public.rooms != {"workshop": Room(id="workshop", label="Sealed facility workshop")}
        or public.edges
        or public.phase_modulus != 1
        or public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
        or public.initial_state
        != initial_state(family, meta.investigation_certificate["action_budget"])
        or public.evidence_files != module(family, "evidence").files(spec)
        or episode.rules
        or episode.machine_rules
    ):
        raise ValueError("discovery public contract or metadata was altered")


def spawn(stock, artifact_id):
    return DomainArtifact(
        ontology=stock.ontology,
        id=artifact_id,
        location=INVENTORY,
        payload=Specimen().model_dump(mode="json"),
    )


def validate_settings(family, machine, values):
    laws = module(family, "laws")
    if any(type(v) is not int for v in values) or not (
        machine == "reader"
        and laws.valid_query(values)
        or machine == "assembler"
        and laws.validate_build(values)
    ):
        raise ValueError(
            "invalid apparatus settings; follow theory.json's reader and construction grammar"
        )


def configure(episode, state, action):
    validate_settings(episode.public.investigation.ontology, action.machine, action.settings)
    if (
        action.machine not in state.machines
        or state.machines[action.machine].room_id != state.agent_room
    ):
        raise ValueError("apparatus is not in the current room")
    state.machines[action.machine].settings = action.settings


def transform(artifact, machine, episode, instrument_settings=None):
    family = episode.public.investigation.ontology
    if instrument_settings is None:
        raise ValueError("apparatus requires settings")
    values = tuple(instrument_settings)
    validate_settings(family, machine, values)
    old = artifact.data()
    if machine == "reader":
        laws = module(family, "laws")
        query = laws.canonical_query(values)
        world = episode.investigation_truth.data()
        response = laws.read_world(world, query)
        new = Specimen(build=old.build, reading=Reading(query=query, values=response))
    else:
        new = Specimen(build=values)
    return DomainArtifact(
        ontology=family,
        id=artifact.id,
        location=artifact.location,
        payload=new.model_dump(mode="json"),
    )


def expected(episode):
    return module(episode.public.investigation.ontology, "laws").target(
        episode.investigation_truth.data()
    )


def submitted(state):
    return state.artifacts["carrier"].data().build


def mission_room(spec):
    return "workshop"


def mission_machine(spec):
    return "assembler"


def assess_mission(episode, state):
    state.mission_accepted = (
        state.agent_room == "workshop"
        and state.artifacts["carrier"].location == INVENTORY
        and module(episode.public.investigation.ontology, "laws").accepted(
            episode.investigation_truth.data(), submitted(state)
        )
    )


def physical_plan(episode):
    return (
        TakeAction(artifact="carrier"),
        ConfigureAction(machine="assembler", settings=expected(episode)),
        OperateAction(machine="assembler", artifact="carrier"),
        FinishAction(),
    )


def measurement(record):
    if record.action.type not in ("probe", "operate") or record.action.machine != "reader":
        return None
    result = next(e.details["result"] for e in record.events if "result" in e.details)
    reading = result["payload"]["reading"]
    return Measurement(
        "reader",
        reading,
        calibration=(
            result["ontology"] == "uncertainty-construction-v1" and reading["query"][0] == 1
        ),
    )


def belief(spec):
    return module(spec.ontology, "inference").Belief(spec.data())


@dataclass
class Tracker:
    room: str
    location: str
    build: tuple[int, ...] | None

    def observe(self, record):
        action = record.action
        if action.type == "move":
            self.room = action.target
        elif action.type in ("take", "drop") and action.artifact == "carrier":
            self.location = INVENTORY if action.type == "take" else self.room
        elif action.type == "operate" and action.artifact == "carrier":
            payload = next(
                e.details["result"]["payload"] for e in record.events if "result" in e.details
            )
            self.build = Specimen.model_validate(payload).build

    def attempted(self):
        return self.build if self.room == "workshop" and self.location == INVENTORY else None


def mission_tracker(public):
    state = public.initial_state
    return Tracker(state.agent_room, state.artifacts["carrier"].location, submitted(state))


def contract(family, spec):
    result = action_contract(scientific=True)
    for item in result["reference"]:
        if item["type"] == "configure":
            item["description"] = (
                "Store reader or assembler settings using the complete grammar in theory.json. Operate commits; probe previews without committing or testing the mission."
            )
            item["example"] = {
                "type": "configure",
                "machine": "reader",
                "settings": list(ADAPTERS[family].reader),
            }
    result["ontology"] = {
        "family": family,
        "experimental": True,
        "mission": "Carry the actual carrier in workshop with an installed device satisfying every operating condition in theory.json; finish successfully.",
        "contract": "Read all evidence. Reader interrogates the facility reference, never your build's correctness. Repeated fixtures are persistent. Failed eligible finishes are binary and recoverable while actions remain. No reset or live correctness preview.",
    }
    return result


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    logging.getLogger("nexus.diagnostics").info(
        "discovery_terminal family=%s T=%s D=%s readings_after_supported_build=%s first_submission_mission_classes=%s empirical_difficulty_calibrated=false",
        spec.ontology,
        spec.theory,
        spec.discovery,
        after_resolved_count,
        first_classes,
    )


def log_terminal_trace(state, trace, posterior):
    from time import perf_counter

    start = perf_counter()
    audit = type(posterior)(posterior.spec)
    tracker = Tracker("workshop", "workshop", None)
    first = 0 if audit.common_decisions() else None
    first_reading_ordinal = 0 if first == 0 else None
    first_source = "public_disclosure" if first == 0 else None
    seen = set()
    repeated = constructs = repairs = observations = 0
    for record in trace:
        previous = tracker.build
        tracker.observe(record)
        if (
            record.action.type == "operate"
            and record.action.artifact == "carrier"
            and record.action.machine == "assembler"
        ):
            constructs += 1
            repairs += previous is not None
        observed = measurement(record)
        if observed:
            observations += 1
            query = tuple(observed.sample["query"])
            repeated += query in seen
            seen.add(query)
            audit.observe(observed)
        elif (
            record.action.type == "finish"
            and record.terminal_status.value != "won"
            and tracker.attempted() is not None
        ):
            audit.exclude_target(tracker.attempted())
        if first is None and audit.common_decisions():
            first = record.turn
            first_reading_ordinal = observations
            first_source = "reader" if observed else "finish_feedback"
    logging.getLogger("nexus.diagnostics").info(
        "discovery_operations readings=%s repeated_queries=%s first_supported_build_turn=%s committed_builds=%s replacements=%s %s=%s remaining_mission_classes=%s common_builds=%s audit_seconds=%.6f",
        observations,
        repeated,
        first,
        constructs,
        repairs,
        ADAPTERS[state.artifacts["carrier"].ontology].prior_count_key.replace(
            "prior_", "remaining_", 1
        ),
        *posterior.counts(),
        len(posterior.common_decisions()),
        perf_counter() - start,
    )
    logging.getLogger("nexus.diagnostics").info(
        "discovery_support first_supported_reading_ordinal=%s first_support_source=%s support_is_behavioral_not_parameter_identity=true",
        first_reading_ordinal,
        first_source,
    )
    if state.artifacts["carrier"].ontology == "uncertainty-construction-v1":
        logging.getLogger("nexus.diagnostics").info(
            "uncertainty_schedule_posterior compatible_complete_assignments=%s distinct_joint_fixtures=%s",
            posterior.compatible_schedules,
            len(posterior.fixtures),
        )
