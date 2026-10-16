"""Full-prior generation: matrix selection never filters the game sampler."""

import secrets

from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainStock, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.compositional.evidence import files
from nexus.ontology.compositional.inference import Belief, reading_bound
from nexus.ontology.compositional.laws import REPAIRS, population, world_for_seed
from nexus.ontology.compositional.schema import FAMILY, Investigation, Specimen

APPARATUS = ("stage", "sensor", "doser")
DESCRIPTION = "Infer the shared counterphase mechanisms and apply a common seal treatment that nulls all four public excitations across both contexts; carry it into array and finish."


def certificate(spec, planning):
    belief = Belief(spec)
    readings = reading_bound(belief.mask)
    bound = 4 + planning if spec.resolved is not None else 5 + planning + 3 * readings
    return {
        "family": FAMILY,
        "status": "experimental-reference-qualified",
        "empirical_difficulty_calibrated": False,
        "prior_worlds": belief.mask.bit_count(),
        "winning_set_signatures": belief.counts()[1],
        "reference_reading_upper": readings,
        "reference_action_upper": bound,
        "scope": "complete disclosed solvable grammar; common accepted repair witness; no cognitive-depth, round or model-failure claim; targeted fixtures are not a uniform sample",
    }


def initial_state(spec, budget):
    return WorldState(
        agent_room=spec.stock_room,
        artifacts={
            "seal": DomainArtifact(
                ontology=FAMILY,
                id="seal",
                location=spec.stock_room,
                payload=Specimen(material="seal").model_dump(mode="json"),
            )
        },
        stocks={
            "stock": DomainStock(
                ontology=FAMILY, id="stock", location=spec.stock_room, remaining=None, payload={}
            )
        },
        machines={
            name: Machine(id=name, room_id=spec.mission_room, uses_remaining=None, settings=None)
            for name in APPARATUS
        },
        resources=Resources(actions_remaining=budget),
    )


def generate_compositional(
    seed,
    *,
    discovery_level=5,
    theory_level=3,
    planning_level=1,
    resource_pressure=1,
    verifier_secret=None,
):
    if (
        any(
            type(v) is not int
            for v in (seed, theory_level, discovery_level, planning_level, resource_pressure)
        )
        or planning_level not in (0, 1)
        or resource_pressure != 1
    ):
        raise ValueError("compositional repair requires integer seed and P0/P1,R1")
    if verifier_secret == "":
        raise ValueError("verifier secret must not be empty")
    index = seed % len(population())
    spec = Investigation.model_validate(
        {
            "theory": theory_level,
            "discovery": discovery_level,
            "stock_room": "stores" if planning_level else "array",
            "resolved": REPAIRS[next(i for i in range(81) if population()[index][1] >> i & 1)]
            if theory_level == 0
            else None,
        }
    )
    proof = certificate(spec, planning_level)
    bound = proof["reference_action_upper"]
    rooms = {spec.stock_room, spec.mission_room}
    return PrivateEpisode(
        public=PublicEpisode(
            episode_id=secrets.token_hex(16),
            description=DESCRIPTION,
            rooms={
                room: Room(id=room, label="Coupled array" if room == "array" else "Material stores")
                for room in rooms
            },
            edges=() if len(rooms) == 1 else ((spec.stock_room, spec.mission_room),),
            phase_modulus=1,
            initial_state=initial_state(spec, bound + 3),
            goal=GoalPredicate(kind=GoalKind.MISSION_ACCEPTED),
            evidence_files=files(spec),
            investigation=DomainInvestigation(
                ontology=FAMILY, payload=spec.model_dump(mode="json")
            ),
        ),
        rules={},
        machine_rules={},
        verifier_secret=verifier_secret or secrets.token_hex(32),
        construction_seed=seed,
        investigation_truth=DomainTruth(ontology=FAMILY, payload=world_for_seed(seed)._asdict()),
        generation_metadata=GenerationMetadata(
            theory_level=theory_level,
            discovery_level=discovery_level,
            planning_level=planning_level,
            resource_pressure=1,
            scenario_family_id=FAMILY,
            room_count=len(rooms),
            machine_count=len(APPARATUS),
            action_budget=bound + 3,
            guaranteed_policy_action_count=bound,
            resource_allowance=3,
            recommended_tool_call_limit=bound + 32,
            investigation_certificate=proof,
        ),
    )
