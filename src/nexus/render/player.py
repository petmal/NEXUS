"""Human rendering of the same observation available to an evaluated player."""

from rich.console import Console
from rich.table import Table

from nexus.models.observation import Observation


def render_player(observation: Observation, *, console: Console | None = None) -> None:
    console = console or Console()
    console.rule(f"NEXUS · turn {observation.turn} · {observation.terminal_status.value}")
    remaining = observation.actions_remaining
    console.print(f"{observation.room}: {observation.room_label}", markup=False)
    console.print(
        f"Exits: {', '.join(observation.exits) or 'none'} | Phase: {observation.phase} | "
        f"Actions left: {'unlimited' if remaining is None else remaining}",
        markup=False,
    )
    for title, items in (
        ("Here", observation.visible_artifacts),
        ("Carrying", observation.carried_artifacts),
        ("Machines here", observation.visible_machines),
        ("Stocks here", observation.visible_stocks),
    ):
        if not items:
            continue
        table = Table(title=title)
        table.add_column("ID")
        table.add_column("Public state")
        for item in items:
            import json
            from rich.text import Text

            values = item.model_dump(mode="json")
            values.pop("id", None)
            table.add_row(Text(item.id), Text(json.dumps(values, ensure_ascii=False)))
        console.print(table)
    if observation.controller_settings is not None:
        console.print("Controller settings:", observation.controller_settings)
