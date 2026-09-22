from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from nexus.engine.replay import execute_with_trace, replay
from nexus.generator import generate_episode, qualify_episode
from nexus.io import load_private, load_trace, save_episode, save_trace
from nexus.models.actions import ACTION_ADAPTER, ACTION_REFERENCE
from nexus.protocol.session import Session
from nexus.protocol.stdio import run_jsonl
from nexus.render.observer import render_observer
from nexus.solver import solve

app = typer.Typer(no_args_is_help=True, help="NEXUS procedural LLM reasoning environment")
console = Console()


def _print_action_reference() -> None:
    table = Table(title="NEXUS actions")
    table.add_column("action")
    table.add_column("meaning")
    table.add_column("example")
    for item in ACTION_REFERENCE:
        table.add_row(
            str(item["type"]),
            str(item["description"]),
            json.dumps(item["example"], separators=(",", ":")),
        )
    console.print(table)
    console.print(
        "Carried artifacts move with you. A machine can only operate/probe a carried artifact "
        "while you are in the machine's room."
    )


@app.command("help")
def help_command(ctx: typer.Context) -> None:
    """Show top-level command help. Equivalent to nexus --help."""
    parent = ctx.parent
    console.print(parent.get_help() if parent is not None else ctx.get_help())


@app.command("actions")
def actions_command() -> None:
    """Show the stable player action vocabulary and JSON examples."""
    _print_action_reference()


@app.command()
def generate(
    output: Path = typer.Argument(..., help="Output directory"),
    seed: int = typer.Option(1, help="Private construction seed"),
    count: int = typer.Option(1, min=1, help="Number of episodes"),
) -> None:
    """Generate one or more solver-qualified episodes.

    Writes a player-safe manifest and attachments plus a runner-only private.json.
    """
    for offset in range(count):
        episode = generate_episode(seed + offset)
        target = output if count == 1 else output / f"episode-{offset + 1:03d}"
        save_episode(episode, target)
        report = qualify_episode(episode)
        if not report.passed:
            raise typer.Exit(code=2)
        console.print(
            f"[green]generated[/green] {episode.public.episode_id} -> {target} "
            f"(optimal={report.metrics['optimal_action_count']})"
        )


@app.command()
def qualify(private: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Validate a compiled episode as benchmark-ready.

    Checks evidence sufficiency, compositional-rule complexity, solver success,
    optimal-plan bounds, exact replay, victory receipt generation, serialization,
    and public/private separation.
    """
    report = qualify_episode(load_private(private))
    console.print_json(data=report.model_dump(mode="json"))
    if not report.passed:
        raise typer.Exit(code=2)


@app.command("solve")
def solve_episode(
    private: Path = typer.Argument(..., exists=True, readable=True),
    trace_out: Path | None = typer.Option(None, help="Optional JSONL trace output"),
) -> None:
    """Find an optimal plan with exhaustive BFS and optionally write its replay trace."""
    episode = load_private(private)
    result = solve(episode)
    console.print_json(data=result.model_dump(mode="json"))
    if result.solvable and trace_out is not None:
        _, trace = execute_with_trace(episode, list(result.plan))
        save_trace(trace, trace_out)


@app.command()
def play(
    private: Path = typer.Argument(..., exists=True, readable=True),
    debug_private: bool = typer.Option(False, help="Show hidden rule/reference plan"),
) -> None:
    """Play interactively by entering one JSON action per line.

    Type help, actions, or ? inside the game for the action reference.
    """
    session = Session(load_private(private))
    render_observer(session.episode, session.state, debug_private=debug_private)
    console.print(session.episode.public.description)
    console.print(
        'Enter JSON actions such as {"type":"move","target":"R1"}. '
        "Type [bold]help[/bold] for all actions; Ctrl-D exits."
    )
    while session.state.terminal_status.value == "active":
        try:
            raw = console.input("[bold cyan]nexus>[/bold cyan] ")
        except EOFError:
            break

        command = raw.strip().lower()
        if command in {"help", "actions", "?"}:
            _print_action_reference()
            continue
        if command in {"quit", "exit"}:
            break

        try:
            action = ACTION_ADAPTER.validate_python(json.loads(raw))
        except Exception as exc:
            console.print(f"[red]invalid action JSON:[/red] {exc}")
            console.print("Type [bold]help[/bold] to see valid actions.")
            continue
        response = session.act(session.state.turn, action)
        if not response.ok:
            console.print(f"[red]{response.message}[/red]")
            continue
        render_observer(session.episode, session.state, debug_private=debug_private)
        if response.victory_code:
            console.print(f"[bold green]{response.victory_code}[/bold green]")


@app.command("replay")
def replay_trace(
    private: Path = typer.Argument(..., exists=True, readable=True),
    trace: Path = typer.Argument(..., exists=True, readable=True),
    observer: bool = typer.Option(False, help="Render final observer state"),
) -> None:
    """Replay a recorded action trace and verify every canonical state hash."""
    episode = load_private(private)
    final = replay(episode, load_trace(trace))
    console.print(f"replay verified: turn={final.turn} status={final.terminal_status.value}")
    if observer:
        render_observer(episode, final)


@app.command()
def stdio(private: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Run the JSONL stdin/stdout machine protocol for an external agent harness."""
    run_jsonl(load_private(private), sys.stdin, sys.stdout)


@app.command()
def serve(
    private: Path = typer.Argument(..., exists=True, readable=True),
    host: str = typer.Option("127.0.0.1"),
    port: int = typer.Option(8000),
) -> None:
    """Run a persistent HTTP session server (requires the server extra)."""
    try:
        import uvicorn
    except ImportError as exc:
        raise typer.BadParameter("install nexus-benchmark[server]") from exc
    from nexus.protocol.http import create_app

    uvicorn.run(create_app(load_private(private)), host=host, port=port)


if __name__ == "__main__":
    app()
