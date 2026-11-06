from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from nexus.ontology.catalog import BUILTINS

SCIENCE_FAMILY_HELP = "Scientific family: " + ", ".join(
    family for family, definition in BUILTINS.items() if definition.generator is not None
) + " (non-default families require axes v2)."


app = typer.Typer(no_args_is_help=True, help="NEXUS procedural LLM reasoning environment")
console = Console()


def _write_json(value: object) -> None:
    sys.stdout.write(json.dumps(value, separators=(",", ":")) + "\n")


def _ontology_options(raw: str | None) -> dict | None:
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter("ontology-options must be a JSON object") from exc
    if not isinstance(value, dict):
        raise typer.BadParameter("ontology-options must be a JSON object")
    return value


@app.command("ontologies")
def ontologies_command(as_json: bool = typer.Option(False, "--json")) -> None:
    """List trusted adapters without constructing worlds or inference tables."""
    rows = [
        {"family": d.family, "specification_version": d.specification_version,
         "generatable": d.generator is not None, "schema_module": d.schema_module,
         "runtime_module": d.runtime_module, "generation_options": d.options_schema}
        for d in BUILTINS.values()
    ]
    if as_json:
        _write_json(rows)
        return
    table = Table(title="NEXUS ontology adapters (registration is not difficulty admission)")
    for name in ("Family", "Generate", "Payload schemas", "Runtime"):
        table.add_column(name)
    for row in rows:
        table.add_row(row["family"], "yes" if row["generatable"] else "explicit PoC",
                      row["schema_module"] or "legacy models", row["runtime_module"])
    console.print(table)


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
        help=SCIENCE_FAMILY_HELP),
    budget_profile: str = typer.Option("standard", envvar="NEXUS_BUDGET_PROFILE",
        help="standard or diagnostic-plus6 (supported families/profiles only; see the family guide)."),
    ontology_options: str | None = typer.Option(None, envvar="NEXUS_ONTOLOGY_OPTIONS",
        help="JSON object validated by the selected ontology's generation-options schema."),
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
            ontology_options=_ontology_options(ontology_options),
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
    debug_private: bool = typer.Option(False, help="Unscored operator view with hidden rules."),
    audit_dir: Path | None = typer.Option(None, help="New private audit directory; never share with the player."),
) -> None:
    """Play a compiled world. Type help for controls; quit ends the local session."""
    from nexus.io import load_private

    _play(load_private(private), debug_private=debug_private, audit_dir=audit_dir)


def _play(episode, *, debug_private=False, audit_dir=None):
    from nexus.models.actions import ACTION_ADAPTER
    from nexus.protocol.audit import AuditRecorder
    from nexus.protocol.session import Session
    from nexus.render.player import render_player

    session = Session(episode)
    recorder = AuditRecorder(session, audit_dir) if audit_dir is not None else None
    try:
        manifest = session.manifest()
        console.print(manifest.description, markup=False)
        console.print("Read the mission and evidence, make a plan, then use finish to claim success.")
        console.print("Evidence files: " + ", ".join(manifest.evidence_files), markup=False)
        console.print("Commands: look, mission, evidence <filename>, help, quit. These are free.\n"
                      'Actions use JSON; for example: {"type":"wait"}. Wait consumes an action.')
        if debug_private:
            console.print("[yellow]Unscored operator mode: private information is visible.[/yellow]")
        while True:
            render_player(session.observe(), console=console)
            if debug_private:
                from nexus.render.observer import render_observer
                render_observer(episode, session.state_snapshot(), console=console, debug_private=True)
            if session.state.terminal_status.value != "active":
                break
            try:
                raw = console.input("[bold cyan]nexus>[/bold cyan] ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            parts = raw.split(maxsplit=1)
            command = parts[0].lower() if parts else ""
            if command in {"quit", "exit"}:
                break
            if command in {"help", "actions", "?"}:
                _print_play_reference(contract=manifest.action_contract)
            elif command in {"look", "status", ""}:
                continue
            elif command == "mission":
                console.print(manifest.description, markup=False)
                console.print_json(data=manifest.goal.model_dump(mode="json"))
                console.print("Evidence files: " + ", ".join(manifest.evidence_files), markup=False)
            elif command == "evidence":
                if len(parts) != 2:
                    console.print("Usage: evidence <filename>")
                    continue
                try:
                    console.print(session.evidence(parts[1]), markup=False, highlight=False)
                except KeyError:
                    console.print("Unknown file. Type mission to list evidence files.")
            else:
                try:
                    action = ACTION_ADAPTER.validate_python(json.loads(raw))
                except (ValueError, TypeError) as exc:
                    console.print(f"Invalid action JSON: {exc}", markup=False)
                    console.print("Type help for valid actions.")
                    continue
                response = session.act(session.state.turn, action)
                console.print(response.message, markup=False)
                if response.events:
                    console.print_json(data=list(response.events))
                if recorder is not None:
                    recorder.checkpoint_safely()
                if response.victory_code:
                    if manifest.presentation_version == "sealed-facility-v2":
                        console.print("Exit clearance granted. Your visit to NEXUS is complete.")
                    console.print("Victory receipt: " + response.victory_code, markup=False)
    finally:
        if recorder is not None:
            recorder.close()


@app.command()
def demo(interactive: bool = typer.Option(False, "--play", help="Play the introductory world yourself.")) -> None:
    """Try NEXUS locally. No model account or API key is needed."""
    from nexus.generator import generate_episode
    from nexus.models.actions import ACTION_ADAPTER
    from nexus.protocol.session import Session
    from nexus.render.player import render_player

    episode = generate_episode(17, discovery_level=0, planning_level=0, resource_pressure=0)
    if interactive:
        _play(episode)
        return
    session = Session(episode)
    manifest = session.manifest()
    console.print("NEXUS guided demonstration — an unscored reference solution.", markup=False)
    console.print(manifest.description, markup=False)
    for name in manifest.evidence_files:
        console.print(f"Evidence: {name}", markup=False)
        console.print(session.evidence(name), markup=False, highlight=False)
    render_player(session.observe(), console=console)
    for raw in episode.reference_plan:
        action = ACTION_ADAPTER.validate_python(raw)
        console.print(action.model_dump_json(), markup=False)
        response = session.act(session.state.turn, action)
        if not response.ok:
            raise RuntimeError("demo reference action failed")
        render_player(response.observation, console=console)
    if not response.victory_code:
        raise RuntimeError("demo did not produce a victory receipt")
    console.print("Success was checked by the engine. Receipt: " + response.victory_code, markup=False)
    console.print("Try it yourself: nexus demo --play")


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
def stdio(
    private: Path = typer.Argument(..., exists=True, readable=True),
    audit_dir: Path | None = typer.Option(None, help="New private audit directory."),
) -> None:
    """Run the JSONL stdin/stdout machine protocol for an external agent harness."""
    from nexus.io import load_private
    from nexus.protocol.stdio import run_jsonl

    run_jsonl(load_private(private), sys.stdin, sys.stdout, audit_directory=audit_dir)


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
        help=SCIENCE_FAMILY_HELP),
    budget_profile: str = typer.Option("standard", envvar="NEXUS_BUDGET_PROFILE",
        help="standard or diagnostic-plus6 (supported families/profiles only; see the family guide)."),
    ontology_options: str | None = typer.Option(None, envvar="NEXUS_ONTOLOGY_OPTIONS",
        help="JSON object validated by the selected ontology generation schema."),
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
    audit_dir: Path | None = typer.Option(
        None, envvar="NEXUS_AUDIT_DIR", help="New private audit directory; keep outside the player sandbox.",
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

    if private is not None and ontology_options is not None:
        raise typer.BadParameter("--ontology-options can only be used with --seed")

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
            ontology_options=_ontology_options(ontology_options),
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

    uvicorn.run(create_single_session_app(episode, extended_diagnostics=extended_diagnostics, audit_directory=audit_dir), host=host, port=port)


@app.command("verify-audit")
def verify_audit(
    directory: Path = typer.Argument(..., exists=True, file_okay=False),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Check a private audit bundle with its matching NEXUS source revision."""
    from nexus.protocol.audit import verify_bundle

    try:
        result = verify_bundle(directory)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        typer.echo(f"Audit verification failed: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    if as_json:
        _write_json(result)
    else:
        console.print_json(data=result)
    if not result["public_capture_complete"]:
        raise typer.Exit(code=2)


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
