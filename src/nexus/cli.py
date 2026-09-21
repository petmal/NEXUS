from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console

from nexus.engine.replay import execute_with_trace, replay
from nexus.generator import generate_episode, qualify_episode
from nexus.io import load_private, load_trace, save_episode, save_trace
from nexus.models.actions import ACTION_ADAPTER
from nexus.protocol.session import Session
from nexus.protocol.stdio import run_jsonl
from nexus.render.observer import render_observer
from nexus.solver import solve

app = typer.Typer(no_args_is_help=True, help="NEXUS procedural LLM reasoning environment")
console = Console()


@app.command()
def generate(
    output: Path = typer.Argument(..., help="Output directory"),
    seed: int = typer.Option(1, help="Private construction seed"),
    count: int = typer.Option(1, min=1, help="Number of episodes"),
) -> None:
    """Generate and solver-qualify one or more episodes."""
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
    """Run the benchmark qualification pipeline."""
    report = qualify_episode(load_private(private))
    console.print_json(data=report.model_dump(mode="json"))
    if not report.passed:
        raise typer.Exit(code=2)


@app.command("solve")
def solve_episode(
    private: Path = typer.Argument(..., exists=True, readable=True),
    trace_out: Path | None = typer.Option(None, help="Optional JSONL trace output"),
) -> None:
    """Solve an episode using exhaustive BFS."""
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
    """Play interactively by entering one JSON action per line."""
    session = Session(load_private(private))
    render_observer(session.episode, session.state, debug_private=debug_private)
    console.print(session.episode.public.description)
    console.print("Enter JSON actions such as {\"type\":\"move\",\"target\":\"R1\"}. Ctrl-D exits.")
    while session.state.terminal_status.value == "active":
        try:
            raw = console.input("[bold cyan]nexus>[/bold cyan] ")
        except EOFError:
            break
        try:
            action = ACTION_ADAPTER.validate_python(json.loads(raw))
        except Exception as exc:
            console.print(f"[red]invalid action JSON:[/red] {exc}")
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
    """Replay and validate a JSONL trace."""
    episode = load_private(private)
    final = replay(episode, load_trace(trace))
    console.print(f"replay verified: turn={final.turn} status={final.terminal_status.value}")
    if observer:
        render_observer(episode, final)


@app.command()
def stdio(private: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Run the JSONL stdin/stdout machine protocol."""
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
