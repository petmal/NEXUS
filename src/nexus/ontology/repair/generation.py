"""Instantiate the fixed proved structure cheaply; search is an offline operation."""

import secrets

from nexus.models.domain import DomainArtifact, DomainInvestigation, DomainStock, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.repair.evidence import files
from nexus.ontology.repair.laws import world_at
from nexus.ontology.repair.schema import FAMILY, Investigation, Specimen

DESCRIPTION = "Open the exit seal by applying a joint treatment to the unique seal specimen, carrying it into the array, and finishing with all four latent residuals zero."


def initial_state(stock_room, mission_room):
    return WorldState(
        agent_room=stock_room,
        artifacts={
            "seal": DomainArtifact(
                ontology=FAMILY,
                id="seal",
                location=stock_room,
                payload=Specimen(material="seal").model_dump(mode="json"),
            )
        },
        stocks={
            "stock": DomainStock(
                ontology=FAMILY,
                id="stock",
                location=stock_room,
                payload={"material": "survey"},
                remaining=None,
            )
        },
        machines={
            name: Machine(id=name, room_id=mission_room, uses_remaining=None, settings=None)
            for name in ("reference", "stage", "coupler", "reader", "doser")
        },
        resources=Resources(actions_remaining=17 + int(stock_room != mission_room)),
    )


def generate_repair(
    seed,
    *,
    discovery_level=5,
    theory_level=3,
    planning_level=1,
    resource_pressure=1,
    verifier_secret=None,
):
    from nexus.ontology.repair.qualification import certificate, release_matches

    if (discovery_level, theory_level, resource_pressure) != (5, 3, 1) or planning_level not in (
        0,
        1,
    ):
        raise ValueError(
            "coupled-repair-v1 supports only T3/D5/P0-or-P1/R1; other cells are not qualified"
        )
    if type(seed) is not int:
        raise ValueError("construction seed must be an integer")
    if verifier_secret == "":
        raise ValueError("verifier_secret must not be empty")
    spec = Investigation(
        stock_room="stores" if planning_level else "array",
        mission_room="array",
        experimental=not release_matches(),
    )
    truth = world_at(seed)
    state = initial_state(spec.stock_room, spec.mission_room)
    budget = 17 + planning_level
    # Independent fresh public identity avoids encoding the selected truth index.
    # A saved compiled episode, not regeneration of its identifier, is the replay unit.
    public = PublicEpisode(
        episode_id=secrets.token_hex(16),
        description=DESCRIPTION,
        rooms={
            room: Room(id=room, label="Sealed array" if room == "array" else "Material stores")
            for room in {spec.stock_room, spec.mission_room}
        },
        edges=() if planning_level == 0 else ((spec.stock_room, spec.mission_room),),
        phase_modulus=1,
        initial_state=state,
        goal=GoalPredicate(kind=GoalKind.MISSION_ACCEPTED),
        evidence_files=files(spec),
        investigation=DomainInvestigation(ontology=FAMILY, payload=spec.model_dump(mode="json")),
    )
    return PrivateEpisode(
        public=public,
        rules={},
        machine_rules={},
        verifier_secret=verifier_secret or secrets.token_hex(32),
        construction_seed=seed,
        investigation_truth=DomainTruth(ontology=FAMILY, payload=truth.model_dump(mode="json")),
        generation_metadata=GenerationMetadata(
            theory_level=3,
            discovery_level=5,
            planning_level=planning_level,
            resource_pressure=1,
            room_count=1 + planning_level,
            machine_count=5,
            action_budget=budget,
            guaranteed_policy_action_count=14 + planning_level,
            resource_allowance=3,
            recommended_tool_call_limit=80,
            investigation_certificate=certificate(planning_level),
        ),
    )


def generate_qualified_repair(seed, **kwargs):
    """General-factory entry point; incomplete or changed proof scope fails closed."""
    from nexus.ontology.repair.qualification import require_release

    require_release()
    return generate_repair(seed, **kwargs)
