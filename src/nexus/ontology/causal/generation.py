"""Opt-in causal ontology generation; existing family defaults and seeds are unchanged."""

import hashlib
import hmac
import logging
import secrets
from time import perf_counter

from nexus.generator.randomness import rng_for
from nexus.models.domain import DomainInvestigation, DomainStock, DomainTruth
from nexus.models.episode import PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.causal.evidence import files
from nexus.ontology.causal.inference import evidence_for, initial_mask
from nexus.ontology.causal.laws import WORLDS, targets
from nexus.ontology.causal.qualification import certificate, research_metadata
from nexus.ontology.causal.schema import FAMILY, LAW_FIELDS, STRUCTURE_FIELDS, Investigation


def generate_causal(
    seed: int,
    *,
    discovery_level=5,
    theory_level=3,
    planning_level=1,
    resource_pressure=1,
    verifier_secret=None,
):
    start = perf_counter()
    if planning_level not in (0, 1) or resource_pressure not in (0, 1, 2):
        raise ValueError("causal-mechanisms-v1 supports P0/P1 and R0/R1/R2")
    if verifier_secret == "":
        raise ValueError("verifier_secret must not be empty")
    secret = verifier_secret or secrets.token_hex(32)
    index = rng_for(seed, FAMILY, "mechanism").randrange(len(WORLDS))
    world = WORLDS[index]
    if (theory_level, discovery_level) == (2, 2):
        world = world._replace(response=rng_for(seed, FAMILY, "combination-response").randrange(2))
        index = WORLDS.index(world)
    fields = LAW_FIELDS if theory_level == 1 else STRUCTURE_FIELDS if theory_level == 2 else ()
    lab, stock = "lab", "lab" if planning_level == 0 else "stocks"
    spec = Investigation.model_validate(
        {
            "theory": theory_level,
            "discovery": discovery_level,
            "mission_room": lab,
            "stock_room": stock,
            "known": {k: getattr(world, k) for k in fields},
            "resolved": targets()[index] if theory_level == 0 else None,
        }
    )
    if discovery_level == 0 and theory_level != 0:
        spec = Investigation.model_validate(
            spec.model_dump() | {"supplied": evidence_for(spec, index)}
        )
    proof = certificate(initial_mask(spec), planning_level, discovery_level != 2)
    if discovery_level == 5 and not proof["untreated_readings_insufficient_for_identification"]:
        raise ValueError("family does not qualify for construction difficulty")
    if discovery_level == 1 and proof["reference_reading_bound"] != 1:
        raise ValueError("family does not qualify for direct measurement difficulty")
    if discovery_level == 2 and proof["target_classes"] <= 3:
        raise ValueError("family does not qualify for combined measurement difficulty")
    bound = proof["reference_action_bound"]
    budget = None if resource_pressure == 0 else bound + (8 if resource_pressure == 1 else 0)
    state = WorldState(
        agent_room=stock,
        artifacts={},
        machines={
            name: Machine(
                id=name,
                room_id=lab,
                uses_remaining=None if resource_pressure == 0 else bound,
                settings=(0, 0, 0) if name == "stage" else None,
            )
            for name in ("stage", "pulse", "sensor", "reference", "board")
        },
        stocks={
            "stock": DomainStock(
                ontology=FAMILY,
                id="stock",
                location=stock,
                remaining=None if resource_pressure == 0 else bound,
                payload={},
            )
        },
        resources=Resources(actions_remaining=budget),
    )
    identity = (
        f"{FAMILY}|{seed}|{discovery_level}|{theory_level}|{planning_level}|{resource_pressure}"
    )
    episode = PrivateEpisode(
        public=PublicEpisode(
            episode_id=hmac.new(secret.encode(), identity.encode(), hashlib.sha256).hexdigest()[
                :24
            ],
            description="Discover the artificial mechanism and preparation-state effects; configure six physical mission responses and finish.",
            rooms={
                room: Room(id=room, label="Causal laboratory" if room == lab else "Specimen stocks")
                for room in {lab, stock}
            },
            edges=() if stock == lab else ((stock, lab),),
            phase_modulus=1,
            initial_state=state,
            goal=GoalPredicate(kind=GoalKind.MISSION_ACCEPTED),
            evidence_files=files(spec),
            investigation=DomainInvestigation(
                ontology=FAMILY, payload=spec.model_dump(mode="json")
            ),
        ),
        rules={},
        machine_rules={},
        verifier_secret=secret,
        construction_seed=seed,
        investigation_truth=DomainTruth(ontology=FAMILY, payload=world._asdict()),
        generation_metadata=research_metadata(
            proof, state, len({lab, stock}), planning_level, spec, resource_pressure,
        ),
    )
    logging.getLogger("nexus.generation").info(
        "causal_generated T=%s D=%s P=%s R=%s worlds=%s targets=%s reference_readings=%s reference_actions=%s seconds=%.6f",
        theory_level,
        discovery_level,
        planning_level,
        resource_pressure,
        proof["prior_worlds"],
        proof["target_classes"],
        proof["reference_reading_bound"],
        bound,
        perf_counter() - start,
    )
    return episode
