from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table


app = typer.Typer(no_args_is_help=True, help="NEXUS procedural LLM reasoning environment")
console = Console()


def _write_json(value: object) -> None:
    sys.stdout.write(json.dumps(value, separators=(",", ":")) + "\n")


def _print_action_reference(*, scientific: bool = False, resonant: bool = False, contract=None) -> None:
    from nexus.models.actions import action_contract

    table = Table(title="NEXUS actions")
    table.add_column("action")
    table.add_column("meaning")
    table.add_column("example")
    for item in (contract or action_contract(scientific=scientific, resonant=resonant))["reference"]:
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


def _print_play_reference(*, scientific: bool = False, resonant: bool = False, contract=None) -> None:
    _print_action_reference(scientific=scientific, resonant=resonant, contract=contract)
    console.print(
        "Human-play meta-command: [bold]evidence <filename>[/bold] reads one of the "
        "public evidence files listed for the episode without consuming an action."
    )


@app.command("help")
def help_command(ctx: typer.Context) -> None:
    """Show top-level command help. Equivalent to nexus --help."""
    parent = ctx.parent
    console.print(parent.get_help() if parent is not None else ctx.get_help())


@app.command("actions")
def actions_command(
    axis_version: int = typer.Option(1, min=1, max=2, envvar="NEXUS_AXIS_VERSION"),
    science_family: str = typer.Option("shared-response-v1", envvar="NEXUS_SCIENCE_FAMILY"),
) -> None:
    """Show the stable player action vocabulary and JSON examples."""
    from nexus.ontology.catalog import BUILTINS

    if science_family not in BUILTINS or BUILTINS[science_family].generator is None:
        raise typer.BadParameter("unknown scientific family", param_hint="science-family")
    if science_family != "shared-response-v1" and axis_version != 2:
        raise typer.BadParameter(f"{science_family} requires axis-version=2")
    _print_action_reference(
        scientific=axis_version == 2, resonant=science_family == "resonant-network-v1",
        contract=BUILTINS[science_family].action_reference(),
    )


@app.command()
def generate(
    output: Path = typer.Argument(..., help="Output directory"),
    seed: int = typer.Option(1, help="Private construction seed"),
    count: int = typer.Option(1, min=1, help="Number of episodes"),
    axis_version: int = typer.Option(1, min=1, max=2, envvar="NEXUS_AXIS_VERSION",
                                    help="1=legacy profiles; 2=scientific investigation semantics."),
    science_family: str = typer.Option("shared-response-v1", envvar="NEXUS_SCIENCE_FAMILY",
        help="Scientific family: shared-response-v1, coupled-network-v1, resonant-network-v1, causal-mechanisms-v1, coupled-repair-v1, coupled-dynamics-v1, compositional-repair-v1, coupled-transfer-v1, coupled-evidence-v1, history-coupled-v1, or staged-repair-v1 (requires axes v2)."),
    budget_profile: str = typer.Option("standard", envvar="NEXUS_BUDGET_PROFILE",
        help="standard or diagnostic-plus6 (supported compositional, transfer, history, or staged profiles; see the family guide)."),
    discovery_level: int = typer.Option(
        0,
        min=0,
        max=5,
        help=(
            "Discovery level 0-5. In v2: supplied evidence, direct measurement, "
            "independent combination, dependent calibration, adaptive selection, construction."
        ),
    ),
    planning_level: int = typer.Option(
        1,
        min=0,
        max=3,
        help="Planning scale 0-3. In v2: P+1 disclosed rooms; P0 is the one-room control.",
    ),
    theory_level: int = typer.Option(
        0, min=0, max=3, envvar="NEXUS_THEORY_LEVEL",
        help="Theory level 0-3; see docs/difficulty.md for legacy v1 and docs/scientific-investigation-design.md for v2 support and semantics.",
    ),
    resource_pressure: int = typer.Option(
        0,
        min=0,
        max=2,
        help="Resource pressure 0-2. Scientific family support and allowances vary; inspect its manifest and profile documentation. Legacy v1 uses finite budgets.",
    ),
) -> None:
    """Generate one or more solver-qualified episodes.

    Writes a player-safe manifest and attachments plus a runner-only private.json.
    """
    from nexus.generator import generate_episode
    from nexus.io import save_episode

    for offset in range(count):
        episode = generate_episode(
            seed + offset,
            axis_version=axis_version,
            science_family=science_family,
            budget_profile=budget_profile,
            discovery_level=discovery_level,
            planning_level=planning_level,
            resource_pressure=resource_pressure,
            theory_level=theory_level,
        )
        target = output if count == 1 else output / f"episode-{offset + 1:03d}"
        save_episode(episode, target)
        metadata = episode.generation_metadata
        policy_summary = f"optimal={metadata.optimal_action_count} probes={metadata.required_probe_count} "
        certificate = metadata.investigation_certificate or {}
        if "reference_reading_bound" in certificate:
            policy_summary = (
                f"physical-optimal={metadata.optimal_action_count} "
                f"reference-readings<={certificate['reference_reading_bound']} "
                f"reference-actions<={certificate['reference_action_bound']} "
            )
        console.print(
            f"[green]generated[/green] {episode.public.episode_id} -> {target} "
            f"(discovery={metadata.discovery_level} planning={metadata.planning_level} "
            f"resource-pressure={metadata.resource_pressure} theory={metadata.theory_level} "
            f"{policy_summary}"
            f"budget={metadata.action_budget} "
            f"recommended-tool-calls={metadata.recommended_tool_call_limit})"
        )


@app.command()
def inspect(private: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Show trusted generation/complexity metadata without dumping hidden rules or secrets."""
    from nexus.io import load_private

    episode = load_private(private)
    console.print_json(
        data={
            "episode_id": episode.public.episode_id,
            "generation_metadata": episode.generation_metadata.model_dump(mode="json"),
        }
    )


@app.command()
def qualify(private: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Validate a compiled episode as benchmark-ready.

    Checks information-profile guarantees, solver success, replay, victory receipt generation,
    serialization, metadata consistency, and public/private separation.
    """
    from nexus.generator import qualify_episode
    from nexus.io import load_private

    report = qualify_episode(load_private(private))
    console.print_json(data=report.model_dump(mode="json"))
    if not report.passed:
        raise typer.Exit(code=2)


@app.command("solve")
def solve_episode(
    private: Path = typer.Argument(..., exists=True, readable=True),
    trace_out: Path | None = typer.Option(None, help="Optional JSONL trace output"),
) -> None:
    """Find an optimal physical plan with exhaustive BFS and optionally write its replay trace."""
    from nexus.engine.replay import execute_with_trace
    from nexus.io import load_private, save_trace
    from nexus.solver import solve

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

    Type help, actions, or ? for the action reference. Use evidence <filename> to read a
    public evidence file without consuming an environment action.
    """
    from nexus.io import load_private
    from nexus.models.actions import ACTION_ADAPTER
    from nexus.protocol.session import Session
    from nexus.render.observer import render_observer

    session = Session(load_private(private))
    render_observer(session.episode, session.state, debug_private=debug_private)
    from nexus.presentation import description, evidence_files
    console.print(description(session.episode.public))
    console.print(
        "Evidence files: "
        + ", ".join(sorted(session.episode.public.evidence_files))
    )
    console.print(
        'Enter JSON actions such as {"type":"move","target":"R1"}. '
        "Type [bold]help[/bold] for all actions; use [bold]evidence <filename>[/bold] "
        "to read public evidence; Ctrl-D exits."
    )
    while session.state.terminal_status.value == "active":
        try:
            raw = console.input("[bold cyan]nexus>[/bold cyan] ")
        except EOFError:
            break

        stripped = raw.strip()
        parts = stripped.split(maxsplit=1)
        command = parts[0].lower() if parts else ""

        if command in {"help", "actions", "?"}:
            from nexus.ontology.catalog import runtime_for
            spec = session.episode.public.investigation
            _print_play_reference(
                scientific=spec is not None,
                resonant=getattr(spec, "version", None) == "resonant-network-v1",
                contract=runtime_for(spec).public_contract(spec) if spec is not None else None,
            )
            continue
        if command in {"quit", "exit"}:
            break
        if command == "evidence":
            if len(parts) != 2 or not parts[1].strip():
                console.print("[red]usage:[/red] evidence <filename>")
                continue
            filename = parts[1].strip()
            content = evidence_files(session.episode.public).get(filename)
            if content is None:
                console.print(f"[red]evidence file not found:[/red] {filename}")
                continue
            console.print(content, markup=False, highlight=False, end="")
            if not content.endswith("\n"):
                console.print()
            continue

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
        if session.episode.public.investigation is not None and response.events:
            console.print_json(data=list(response.events))
        if response.victory_code:
            console.print(f"[bold green]{response.victory_code}[/bold green]")


@app.command("replay")
def replay_trace(
    private: Path = typer.Argument(..., exists=True, readable=True),
    trace: Path = typer.Argument(..., exists=True, readable=True),
    observer: bool = typer.Option(False, help="Render final observer state"),
) -> None:
    """Replay a recorded action trace and verify every canonical state hash."""
    from nexus.engine.replay import replay
    from nexus.io import load_private, load_trace
    from nexus.render.observer import render_observer

    episode = load_private(private)
    final = replay(episode, load_trace(trace))
    console.print(f"replay verified: turn={final.turn} status={final.terminal_status.value}")
    if observer:
        render_observer(episode, final)


@app.command()
def stdio(private: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Run the JSONL stdin/stdout machine protocol for an external agent harness."""
    from nexus.io import load_private
    from nexus.protocol.stdio import run_jsonl

    run_jsonl(load_private(private), sys.stdin, sys.stdout)


@app.command()
def serve(
    private: Path = typer.Argument(..., exists=True, readable=True),
    host: str = typer.Option("127.0.0.1"),
    port: int = typer.Option(8000),
) -> None:
    """Run a persistent multi-session HTTP server (requires the server extra)."""
    from nexus.io import load_private

    try:
        import uvicorn
    except ImportError as exc:
        raise typer.BadParameter("install nexus-benchmark[server]") from exc
    from nexus.protocol.http import create_app

    uvicorn.run(create_app(load_private(private)), host=host, port=port)


@app.command("serve-session")
def serve_session(
    private: Path | None = typer.Option(
        None, exists=True, readable=True,
        help="Optional compiled private episode. Mutually exclusive with --seed.",
    ),
    seed: int | None = typer.Option(
        None, envvar="NEXUS_SEED", help="Generate a qualified episode from this seed.",
    ),
    axis_version: int = typer.Option(1, min=1, max=2, envvar="NEXUS_AXIS_VERSION",
                                    help="1=legacy profiles; 2=scientific investigation semantics."),
    science_family: str = typer.Option("shared-response-v1", envvar="NEXUS_SCIENCE_FAMILY",
        help="Scientific family: shared-response-v1, coupled-network-v1, resonant-network-v1, causal-mechanisms-v1, coupled-repair-v1, coupled-dynamics-v1, compositional-repair-v1, coupled-transfer-v1, coupled-evidence-v1, history-coupled-v1, or staged-repair-v1 (requires axes v2)."),
    budget_profile: str = typer.Option("standard", envvar="NEXUS_BUDGET_PROFILE",
        help="standard or diagnostic-plus6 (supported compositional, transfer, history, or staged profiles; see the family guide)."),
    discovery_level: int = typer.Option(
        0,
        min=0,
        max=5,
        envvar="NEXUS_DISCOVERY_LEVEL",
        help="Generated-session causal-discovery difficulty (used with --seed).",
    ),
    planning_level: int = typer.Option(
        1,
        min=0,
        max=3,
        envvar="NEXUS_PLANNING_LEVEL",
        help="Generated-session planning scale (used with --seed).",
    ),
    theory_level: int = typer.Option(
        0, min=0, max=3, envvar="NEXUS_THEORY_LEVEL",
        help="Theory level 0-3; see docs/difficulty.md for legacy v1 and docs/scientific-investigation-design.md for v2 support and semantics.",
    ),
    resource_pressure: int = typer.Option(
        0,
        min=0,
        max=2,
        envvar="NEXUS_RESOURCE_PRESSURE",
        help="Generated-session action-budget pressure (used with --seed).",
    ),
    verifier_secret: str | None = typer.Option(
        None, envvar="NEXUS_VERIFIER_SECRET",
        help="Optional fixed verifier secret when generating from --seed.",
    ),
    extended_diagnostics: bool = typer.Option(
        False, envvar="NEXUS_EXTENDED_DIAGNOSTICS",
        help="Private operator action journal and terminal/shutdown evidence diagnostics.",
    ),
    generation_timing: bool = typer.Option(
        False, envvar="NEXUS_GENERATION_TIMING",
        help="Log generation stage timings to operator stderr; keep service logs private.",
    ),
    host: str = typer.Option("127.0.0.1", envvar="NEXUS_HOST"),
    port: int = typer.Option(8000, envvar="NEXUS_PORT"),
) -> None:
    """Run one non-resettable HTTP session for an external orchestrator."""
    from nexus.generator import generate_episode
    from nexus.io import load_private

    if (private is None) == (seed is None):
        raise typer.BadParameter("provide exactly one of --private or --seed")
    if private is not None and verifier_secret is not None:
        raise typer.BadParameter("--verifier-secret can only be used with --seed")

    if private is not None and budget_profile != "standard":
        raise typer.BadParameter("--budget-profile can only be used with --seed; compiled profiles are immutable")

    if generation_timing or extended_diagnostics:
        import logging

        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
        logging.getLogger("nexus.generation").setLevel(logging.INFO if generation_timing else logging.WARNING)
        logging.getLogger("nexus.operator").setLevel(logging.INFO if extended_diagnostics else logging.WARNING)

    episode = (
        load_private(private)
        if private is not None
        else generate_episode(
            seed,
            axis_version=axis_version,
            science_family=science_family,
            budget_profile=budget_profile,
            discovery_level=discovery_level,
            planning_level=planning_level,
            resource_pressure=resource_pressure,
            theory_level=theory_level,
            verifier_secret=verifier_secret,
        )
    )
    try:
        import uvicorn
    except ImportError as exc:
        raise typer.BadParameter("install nexus-benchmark[server]") from exc
    from nexus.protocol.http import create_single_session_app

    uvicorn.run(create_single_session_app(episode, extended_diagnostics=extended_diagnostics), host=host, port=port)


@app.command("request")
def request_command(
    request_file: Path = typer.Option(..., exists=True, readable=True),
    url: str | None = typer.Option(None, envvar="NEXUS_URL"),
) -> None:
    """Send one player-safe request to a single-session service."""
    from pydantic import ValidationError

    from nexus.protocol.client import (
        SERVICE_REQUEST_ADAPTER,
        ClientError,
        request_service,
    )

    try:
        request = SERVICE_REQUEST_ADAPTER.validate_json(request_file.read_text(encoding="utf-8"))
        response = request_service(request, url=url)
    except (ValidationError, ClientError, OSError) as exc:
        typer.echo(f"request failed: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    _write_json(response)


@app.command("health")
def health_command(
    url: str | None = typer.Option(None, envvar="NEXUS_URL"),
) -> None:
    """Exit successfully when a NEXUS service is healthy."""
    from nexus.protocol.client import ClientError, check_health

    try:
        check_health(url=url)
    except ClientError as exc:
        typer.echo(f"unhealthy: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    sys.stdout.write("ok\n")


@app.command("validate")
def validate_command(
    candidate: str | None = typer.Option(None, help="Submitted victory code."),
    candidate_file: Path | None = typer.Option(
        None, exists=True, readable=True,
        help="Read the submitted victory code from a file.",
    ),
    url: str | None = typer.Option(None, envvar="NEXUS_URL"),
) -> None:
    """Finalize the attempt, validate its victory code, and log terminal diagnostics."""
    from nexus.protocol.client import ClientError, validate_candidate_with_performance

    if (candidate is None) == (candidate_file is None):
        raise typer.BadParameter("provide exactly one of --candidate or --candidate-file")

    supplied = candidate if candidate is not None else candidate_file.read_text(encoding="utf-8")
    try:
        result, performance = validate_candidate_with_performance(supplied, url=url)
    except ClientError as exc:
        typer.echo(f"validation failed: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(
        "NEXUS terminal performance: "
        + json.dumps(performance, sort_keys=True, separators=(",", ":")),
        err=True,
    )
    from nexus.protocol.transport import receipt_classification

    typer.echo("NEXUS receipt classification: " + json.dumps(
        receipt_classification(result.model_dump(mode="json"), performance), sort_keys=True
    ), err=True)
    _write_json(result.model_dump(mode="json"))


if __name__ == "__main__":
    app()
