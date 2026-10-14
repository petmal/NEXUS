"""Opt-in conformance PoC; not a calibrated production difficulty family."""

import hashlib
import hmac
import secrets

from nexus.generator.randomness import rng_for
from nexus.models.actions import ConfigureAction, FinishAction, ProbeAction, TakeAction
from nexus.models.domain import DomainInvestigation, DomainStock, DomainTruth
from nexus.models.episode import GenerationMetadata, PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalKind, GoalPredicate
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.categorical.laws import PERMUTATIONS, prefix, target
from nexus.ontology.categorical.runtime import FAMILY
from nexus.ontology.categorical.schema import SYMBOLS
from nexus.presentation import CURRENT, PresentationVersion


def generate_categorical(seed: int, *, depth: int = 3, verifier_secret: str | None = None,
                         presentation_version: PresentationVersion | None = CURRENT):
    if depth not in (2, 3):
        raise ValueError("categorical PoC supports depth 2 or 3")
    if verifier_secret == "":
        raise ValueError("verifier_secret must not be empty")
    secret = verifier_secret or secrets.token_hex(32)
    rng = rng_for(seed, FAMILY, depth)
    laws = tuple(rng.choice(PERMUTATIONS) for _ in range(depth))
    manual = f"""EXPERIMENTAL ONTOLOGY CONFORMANCE PoC — not a calibrated D profile.
There are {depth} unknown bijections pi0..pi{depth - 1} on the invented symbols
ka, tu, ve. Every permutation is allowed, independently at each stage.
Integer selectors 0,1,2 denote ka,tu,ve in that order.
Stocks S0,S1,S2 create specimens of these respective symbols using take.
Instrument0 reports pi0(x) directly. For instrument i>0, configure one selector z;
it reports pi_i(x) only when z = pi_(i-1)(...pi0(x)). Otherwise it reports
signal=false and reading=null. Both outcomes are evidence. Configure gives no
correctness feedback. Probe previews; operate writes the reading. Symbols persist.
The board requires three selectors: the composition pi{depth - 1}(...pi0(x)) for
x=ka,tu,ve, in that order. Configure board then finish. No port is required.
All stocks, instruments and the board are in lab. Stocks and uses are unlimited;
actions advance turns without a resource cap. No staged unlocks apply.
"""
    state = WorldState(
        agent_room="lab",
        artifacts={},
        machines={
            name: Machine(
                id=name,
                room_id="lab",
                uses_remaining=None,
                settings=(0,) if name.startswith("instrument") else None,
            )
            for name in ("board", *(f"instrument{i}" for i in range(depth)))
        },
        stocks={
            f"S{i}": DomainStock(
                ontology=FAMILY, id=f"S{i}", location="lab", payload={"symbol": symbol}
            )
            for i, symbol in enumerate(SYMBOLS)
        },
        resources=Resources(actions_remaining=None),
    )
    return PrivateEpisode(
        public=PublicEpisode(
            presentation_version=presentation_version,
            episode_id=hmac.new(
                secret.encode(), f"{FAMILY}|{seed}|{depth}".encode(), hashlib.sha256
            ).hexdigest()[:16],
            description="Infer the categorical laws, compose them, configure the prediction board, and finish.",
            rooms={"lab": Room(id="lab", label="Categorical laboratory")},
            edges=(),
            phase_modulus=1,
            initial_state=state,
            goal=GoalPredicate(kind=GoalKind.MISSION_ACCEPTED),
            evidence_files={"manual.txt": manual},
            investigation=DomainInvestigation(
                ontology=FAMILY, payload={"depth": depth, "mission_room": "lab"}
            ),
        ),
        rules={},
        machine_rules={},
        verifier_secret=secret,
        construction_seed=seed,
        investigation_truth=DomainTruth(
            ontology=FAMILY, payload={"laws": [list(law) for law in laws]}
        ),
        generation_metadata=GenerationMetadata(
            theory_level=3,
            discovery_level=0,
            planning_level=0,
            resource_pressure=0,
            room_count=1,
            machine_count=depth + 1,
            investigation_certificate={
                "experimental": True,
                "calibrated_axes": False,
                "dependency_depth": depth,
                "world_count": 6**depth,
                "reading_upper_bound": 2 * depth,
                "exact_global_minimum": False,
            },
        ),
    )


def public_policy(session):
    """Reference agent uses only manifest/evidence, observations and action responses.

    It deliberately does not inspect session.episode or hidden truth. The manifest
    declares depth via the listed instruments in the ordinary observation.
    """
    observation = session.observe()
    depth = sum(m.id.startswith("instrument") for m in observation.visible_machines)

    def act(action):
        response = session.act(action=action, expected_turn=session.status().turn)
        if not response.ok:
            raise AssertionError(response.message)
        return response

    specimens = []
    for x in (0, 1):
        response = act(TakeAction(artifact=f"S{x}"))
        specimens.append(
            next(e["details"]["artifact"] for e in response.events if e["type"] == "take")
        )
    learned = []
    for stage in range(depth):
        values = []
        for x, artifact in enumerate(specimens):
            if stage:
                act(
                    ConfigureAction(
                        machine=f"instrument{stage}", settings=(prefix(tuple(learned), stage, x),)
                    )
                )
            response = act(ProbeAction(machine=f"instrument{stage}", artifact=artifact))
            result = next(
                e["details"]["result"]["payload"]
                for e in response.events
                if "result" in e["details"]
            )
            values.append(SYMBOLS.index(result["reading"]))
        learned.append(next(law for law in PERMUTATIONS if law[:2] == tuple(values)))
    act(ConfigureAction(machine="board", settings=target(tuple(learned))))
    return act(FinishAction())
