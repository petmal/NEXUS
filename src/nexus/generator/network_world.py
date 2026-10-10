"""Fresh topology construction and physical witness bookkeeping for network worlds.

This layer neither selects hidden laws nor computes information certificates. A
family can construct its own episode directly without compiling another family.
"""

from __future__ import annotations

from collections import deque
from functools import lru_cache

from nexus.engine.network import prepare
from nexus.models.episode import PrivateEpisode, PublicEpisode
from nexus.models.goals import GoalPredicate
from nexus.models.network import NetworkSpec, NetworkStock, NetworkTruth
from nexus.models.world import Machine, Resources, Room, WorldState
from nexus.ontology.network import Point, network_apparatus


def build_network_world(
    *,
    spec: NetworkSpec,
    truth: NetworkTruth,
    planning: int,
    pressure: int,
    seed: int,
    secret: str,
    episode_id: str,
    description: str,
) -> PrivateEpisode:
    """Allocate fresh mutable state; the caller adds its evidence and certificate."""
    apparatus = network_apparatus(spec.version)
    bench_room = "R0" if planning == 0 else "R1"
    tuning = dict(apparatus.initial_settings)
    return PrivateEpisode(
        public=PublicEpisode(
            protocol_version="nexus-0.3",
            episode_id=episode_id,
            description=description,
            rooms={
                f"R{i}": Room(
                    id=f"R{i}",
                    label="Laboratory"
                    if i == 0 and planning == 0
                    else "Specimen stocks"
                    if i == 0
                    else "Laboratory"
                    if i == 1
                    else "Controller"
                    if i == planning
                    else "Transit",
                )
                for i in range(planning + 1)
            },
            edges=tuple((f"R{i}", f"R{i + 1}") for i in range(planning)),
            phase_modulus=1,
            initial_state=WorldState(
                agent_room="R0",
                artifacts={},
                stocks={
                    f"S{x}-{y}": NetworkStock(
                        id=f"S{x}-{y}",
                        location="R0",
                        x=x,
                        y=y,
                        remaining=None if pressure == 0 else 16,
                    )
                    for x, y in (((0, 0),) if spec.discovery == 5 else apparatus.bench)
                },
                machines={
                    name: Machine(
                        id=name,
                        room_id=spec.controller_room if name == "controller" else bench_room,
                        uses_remaining=None if pressure == 0 else 128,
                        settings=tuning.get(name),
                    )
                    for name in apparatus.machines
                },
                resources=Resources(actions_remaining=None),
            ),
            goal=GoalPredicate(kind="controller_accepted"),
            investigation=spec,
        ),
        rules={},
        machine_rules={},
        verifier_secret=secret,
        construction_seed=seed,
        investigation_truth=truth,
    )


@lru_cache(maxsize=49 * 49)
def preparation_route(start: Point, target: Point) -> tuple[str, ...]:
    queue: deque[tuple[Point, tuple[str, ...]]] = deque(((start, ()),))
    seen = {start}
    while queue:
        point, path = queue.popleft()
        if point == target:
            return path
        for machine in ("shift", "shear"):
            other = prepare(point, machine)
            if other not in seen:
                seen.add(other)
                queue.append((other, path + (machine,)))
    raise ValueError("unreachable network preparation")


class NetworkWitness:
    """Physical plan on the qualified chain layout, starting at R0 with no specimen.

    Each stage may have a turn offset. Returning a stage to R0 and taking a fresh
    specimen permits composition without leaking the preceding specimen state.
    Experiment selection and readings are owned by the calling scientific policy.
    """

    def __init__(self, episode: PrivateEpisode, *, offset: int = 0):
        spec = episode.public.investigation
        if not isinstance(spec, NetworkSpec):
            raise TypeError("network witness requires a network specification")
        self.discovery = spec.discovery
        self.lab = episode.public.initial_state.machines["meter"].room_id
        self.offset = offset
        self.actions: list[dict] = []
        self.room = "R0"
        self.point: Point = (0, 0)
        self.specimen: str | None = None

    def move(self, destination: str) -> None:
        while self.room != destination:
            here, there = int(self.room[1:]), int(destination[1:])
            self.room = f"R{here + (1 if here < there else -1)}"
            self.actions.append({"type": "move", "target": self.room})

    def take(self, stock: str) -> str:
        self.move("R0")
        self.actions.append({"type": "take", "artifact": stock})
        return f"{stock}.{self.offset + len(self.actions)}"

    def prepare(self, target: Point) -> str:
        if self.discovery == 5:
            if self.specimen is None:
                self.specimen = self.take("S0-0")
            self.move(self.lab)
            for machine in preparation_route(self.point, target):
                self.actions.append(
                    {"type": "operate", "machine": machine, "artifact": self.specimen}
                )
            self.point = target
        else:
            self.specimen = self.take(f"S{target[0]}-{target[1]}")
            self.move(self.lab)
        return self.specimen
