from __future__ import annotations

from rich.console import Console
from rich.table import Table

from nexus.models.episode import PrivateEpisode
from nexus.models.world import WorldState


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

    machines = Table(title="Machines")
    for column in ("id", "room", "uses"):
        machines.add_column(column)
    for machine in sorted(state.machines.values(), key=lambda m: m.id):
        machines.add_row(machine.id, machine.room_id, str(machine.uses_remaining))
    console.print(machines)

    if debug_private:
        console.print("[bold yellow]Private rule AST[/bold yellow]")
        console.print_json(data={k: v.model_dump(mode="json") for k, v in episode.rules.items()})
        console.print("[bold yellow]Reference plan[/bold yellow]")
        console.print_json(data=list(episode.reference_plan))
