from __future__ import annotations

from collections import defaultdict

from rich.console import Console
from rich.table import Table

from nexus.models.episode import PrivateEpisode
from nexus.models.world import WorldState


def _room_exits(episode: PrivateEpisode) -> dict[str, tuple[str, ...]]:
    exits: dict[str, list[str]] = defaultdict(list)
    for left, right in episode.public.edges:
        exits[left].append(right)
        exits[right].append(left)
    return {
        room_id: tuple(sorted(exits.get(room_id, [])))
        for room_id in sorted(episode.public.rooms)
    }


def render_observer(
    episode: PrivateEpisode,
    state: WorldState,
    *,
    console: Console | None = None,
    debug_private: bool = False,
) -> None:
    console = console or Console()
    console.rule(f"NEXUS {episode.public.episode_id} · turn {state.turn}")
    console.print(
        f"Agent: [bold]{state.agent_room}[/bold]  Phase: {state.phase}  "
        f"Actions: {state.resources.actions_remaining}  Status: {state.terminal_status.value}"
    )

    map_table = Table(title="Facility map")
    map_table.add_column("here")
    map_table.add_column("room")
    map_table.add_column("label")
    map_table.add_column("exits")
    for room_id, exits in _room_exits(episode).items():
        room = episode.public.rooms[room_id]
        map_table.add_row(
            "●" if room_id == state.agent_room else "",
            room_id,
            room.label,
            ", ".join(exits) or "—",
        )
    console.print(map_table)

    table = Table(title="Artifacts")
    for column in ("id", "location", "shape", "pattern", "orientation", "value", "polarity"):
        table.add_column(column)
    for artifact in sorted(state.artifacts.values(), key=lambda a: a.id):
        table.add_row(
            artifact.id,
            artifact.location,
            artifact.shape.value,
            artifact.pattern.value,
            artifact.orientation.value,
            str(artifact.value),
            artifact.polarity.value,
        )
    console.print(table)

    if state.stocks:
        stocks = Table(title="Specimen stocks")
        for column in ("id", "room", "source", "initial q", "remaining"):
            stocks.add_column(column)
        for stock in state.stocks.values():
            stocks.add_row(stock.id, stock.location, stock.source, str(stock.q),
                           "unlimited" if stock.remaining is None else str(stock.remaining))
        console.print(stocks)
        specimens = Table(title="Prepared specimens")
        for column in ("id", "source", "q", "reading"):
            specimens.add_column(column)
        for artifact in state.artifacts.values():
            if artifact.sample is not None:
                specimens.add_row(artifact.id, artifact.sample.source, str(artifact.sample.q),
                                  str(artifact.sample.reading))
        console.print(specimens)
        if state.controller_settings is not None:
            console.print("Controller settings:", state.controller_settings)

    machines = Table(title="Machines")
    for column in ("id", "room", "uses"):
        machines.add_column(column)
    for machine in sorted(state.machines.values(), key=lambda m: m.id):
        machines.add_row(machine.id, machine.room_id, str(machine.uses_remaining))
    console.print(machines)

    if debug_private:
        if episode.investigation_truth is not None:
            console.print("[bold yellow]Private scientific truth[/bold yellow]")
            console.print_json(data=episode.investigation_truth.model_dump(mode="json"))
        console.print("[bold yellow]Private rule AST[/bold yellow]")
        console.print_json(data={k: v.model_dump(mode="json") for k, v in episode.rules.items()})
        console.print("[bold yellow]Reference plan[/bold yellow]")
        console.print_json(data=list(episode.reference_plan))
