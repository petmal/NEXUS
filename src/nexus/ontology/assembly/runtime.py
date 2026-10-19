"""Assembly adapter; the generic engine still owns actions, replay and receipts."""

import logging
from dataclasses import dataclass
from typing import cast

from nexus.models.actions import FinishAction, MoveAction, TakeAction, action_contract
from nexus.models.domain import DomainArtifact
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import INVENTORY
from nexus.ontology.assembly.laws import accepted, normalize_query, prepare, reading, target
from nexus.ontology.assembly.laws import submitted as specimen_build
from nexus.ontology.assembly.schema import FAMILY, Reading, Specimen
from nexus.ontology.inference import Measurement

performance_style = "mission"
requires_single_session = True


def validate_episode(episode):
    from nexus.ontology.assembly.evidence import files
    from nexus.ontology.assembly.generation import (
        DESCRIPTION,
        initial_state,
        metadata,
        selection,
        topology,
    )

    spec = episode.public.investigation.data()
    world = episode.investigation_truth.data()
    meta = episode.generation_metadata
    if type(episode.construction_seed) is not int or world != selection(episode.construction_seed):
        raise ValueError("assembly truth contradicts integer seed")
    if spec.resolved is not None and spec.resolved != world:
        raise ValueError("assembly exact disclosure contradicts truth")
    if spec.known_kernel is not None and spec.known_kernel != world.kernel:
        raise ValueError("assembly operator disclosure contradicts truth")
    expected_meta = metadata(spec, meta.resource_pressure, meta.budget_profile)
    rooms, edges = topology(spec)
    if meta != expected_meta:
        raise ValueError("assembly generation metadata contradicts profile")
    public = episode.public
    if (
        public.description != DESCRIPTION
        or public.rooms != rooms
        or public.edges != edges
        or public.phase_modulus != 1
        or public.goal != GoalPredicate(kind=GoalKind.MISSION_ACCEPTED)
        or public.initial_state
        != initial_state(spec, expected_meta.investigation_certificate["action_budget"])
        or public.evidence_files != files(spec)
        or episode.rules
        or episode.machine_rules
    ):
        raise ValueError("assembly public world contradicts compiled contract")


def spawn(stock, artifact_id):
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact_id,
        location=INVENTORY,
        payload=Specimen().model_dump(mode="json"),
    )


def validate_settings(machine, values):
    valid = (
        machine == "reader"
        and len(values) == 3
        and all(v in (0, 1, 2) for v in values)
        or machine == "forge"
        and len(values) == 3
        and values[0] in (0, 1)
        and values[1] in (1, 2)
        and values[2] in (0, 1, 2)
        or machine == "assembler"
        and len(values) == 1
        and values[0] in (0, 1, 2, 3)
    )
    if not valid:
        raise ValueError(
            "reader [channel,x,y] 0..2; forge [slot 0..1,gain 1..2,phase 0..2]; assembler [kernel 0..3]"
        )


def configure(episode, state, action):
    validate_settings(action.machine, action.settings)
    if state.machines[action.machine].room_id != state.agent_room:
        raise ValueError("apparatus is not in the current room")
    state.machines[action.machine].settings = action.settings


def transform(artifact, machine, episode, instrument_settings: tuple[int, ...] | None = None):
    if not instrument_settings:
        raise ValueError("assembly apparatus requires nonempty settings")
    values = instrument_settings
    validate_settings(machine, values)
    sample = artifact.data()
    if machine == "reader":
        ch, x, y = normalize_query(*values)
        result = Specimen(
            b=sample.b,
            c=sample.c,
            kernel=sample.kernel,
            reading=Reading(
                channel=ch,
                x=x,
                y=y,
                value=reading(
                    episode.investigation_truth.data(),
                    (ch, x, y),
                    episode.public.investigation.data().coupled_reader,
                ),
            ),
        )
    elif machine == "forge":
        result = prepare(sample, *values)
    else:
        if sample.b is None or sample.c is None:
            raise ValueError("assembler requires both prepared components")
        result = Specimen(b=sample.b, c=sample.c, kernel=values[0])
    return DomainArtifact(
        ontology=FAMILY,
        id=artifact.id,
        location=artifact.location,
        payload=result.model_dump(mode="json"),
    )


def expected(episode):
    return target(episode.investigation_truth.data())


def submitted(state):
    return specimen_build(state.artifacts["carrier"].data())


def mission_room(spec):
    return "workshop"


def mission_machine(spec):
    return "assembler"


def assess_mission(episode, state):
    state.mission_accepted = (
        state.agent_room == "workshop"
        and state.artifacts["carrier"].location == INVENTORY
        and accepted(episode.investigation_truth.data(), submitted(state))
    )


def physical_plan(episode):
    from nexus.ontology.assembly.policy import omniscient_construction

    spec = episode.public.investigation.data()
    return (
        TakeAction(artifact="carrier"),
        *((MoveAction(target="workshop"),) if spec.stock_room != "workshop" else ()),
        *omniscient_construction(episode.investigation_truth.data()),
        FinishAction(),
    )


def measurement(record):
    if record.action.type not in ("probe", "operate") or record.action.machine != "reader":
        return None
    payload = next(e.details["result"]["payload"] for e in record.events if "result" in e.details)
    return Measurement("reader", payload["reading"])


def measurement_features(measurement):
    return measurement.sample["channel"], False


def belief(spec):
    from nexus.ontology.assembly.inference import Belief

    return Belief(spec.data())


@dataclass
class Tracker:
    room: str
    location: str
    sample: Specimen

    def observe(self, record):
        action = record.action
        if action.type == "move":
            self.room = action.target
        elif action.type in ("take", "drop") and action.artifact == "carrier":
            self.location = INVENTORY if action.type == "take" else self.room
        elif action.type == "operate" and action.artifact == "carrier":
            self.sample = Specimen.model_validate(
                next(e.details["result"]["payload"] for e in record.events if "result" in e.details)
            )

    def attempted(self):
        return (
            specimen_build(self.sample)
            if self.room == "workshop" and self.location == INVENTORY
            else None
        )


def mission_tracker(public):
    state = public.initial_state
    return Tracker(
        state.agent_room, state.artifacts["carrier"].location, state.artifacts["carrier"].data()
    )


def public_contract(spec):
    result = action_contract(scientific=True)
    # action_contract constructs a tuple of copied ACTION_REFERENCE dictionaries;
    # its legacy return annotation intentionally also permits other object fields.
    reference = cast(tuple[dict[str, object], ...], result["reference"])
    for item in reference:
        if item["type"] == "configure":
            item["description"] = (
                "Reader [channel,x,y]; forge [slot,gain,phase]; assembler [kernel]. Configure stores settings; operate applies them. Read evidence for ranges and cross-slot mounting effects."
            )
            item["example"] = {"type": "configure", "machine": "reader", "settings": [0, 0, 0]}
    result["ontology"] = {
        "family": FAMILY,
        "experimental": True,
        "configuration": {
            "reader": {"arity": 3, "ranges": [[0, 2], [0, 2], [0, 2]]},
            "forge": {"arity": 3, "ranges": [[0, 1], [1, 2], [0, 2]]},
            "assembler": {"arity": 1, "ranges": [[0, 3]]},
        },
        "mission": "Carry the actual carrier in workshop with both correct local gains and an assembled output matching the facility at all nine x,y inputs, then finish.",
        "contract": "Read every evidence file. Local phase validity does not imply global compatibility. Reader measures the isolated reference fixture, not this build. Forge changes the other mounted slot as disclosed. Probe never commits. Failed finishes are binary and recoverable while actions remain.",
    }
    return result


def log_terminal(spec, calibration_count, no_signal_count, after_resolved_count, first_classes):
    logging.getLogger("nexus.diagnostics").info(
        "assembly_terminal T=%s D=%s first_submission_mission_signatures=%s readings_after_supported_build=%s empirical_difficulty_calibrated=false",
        spec.theory,
        spec.discovery,
        first_classes,
        after_resolved_count,
    )


def log_terminal_trace(state, trace, posterior):
    # These are terminal/operator diagnostics, never active-play hints.
    from nexus.ontology.assembly.inference import Belief

    tracker = Tracker(posterior.spec.stock_room, posterior.spec.stock_room, Specimen())
    audit = Belief(posterior.spec)
    first_turn = 0 if audit.common_decisions() else None
    first_kind = "disclosure" if first_turn == 0 else None
    first_reading = None
    count = preparations = repairs = 0
    channels = set()
    for record in trace:
        previous = tracker.sample
        tracker.observe(record)
        action = record.action
        if action.type == "operate" and action.artifact == "carrier" and action.machine == "forge":
            preparations += 1
            repairs += int(previous.kernel is not None)
        observed = measurement(record)
        if observed is not None:
            count += 1
            channels.add(observed.sample["channel"])
            audit.observe(observed)
        elif (
            action.type == "finish"
            and record.terminal_status.value != "won"
            and tracker.attempted() is not None
        ):
            audit.exclude_target(tracker.attempted())
        if first_turn is None and audit.common_decisions():
            first_turn = record.turn
            first_kind = "reading" if observed is not None else "finish_rejection"
            first_reading = count if observed is not None else None
    logging.getLogger("nexus.diagnostics").info(
        "assembly_operations reader_calls=%s channels_observed=%s first_supported_build_turn=%s first_supported_build_source=%s first_supporting_reading_ordinal=%s committed_preparations=%s preparations_after_assembly=%s remaining_worlds=%s remaining_mission_signatures=%s common_builds=%s",
        count,
        sorted(channels),
        first_turn,
        first_kind,
        first_reading,
        preparations,
        repairs,
        *posterior.counts(),
        len(posterior.common_decisions()),
    )
