"""Public device guides teach controls without running or recommending experiments."""

import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from pydantic import ValidationError
from rich.console import Console
from typer.testing import CliRunner

from nexus.cli import app
from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.io import save_episode
from nexus.models.actions import ACTION_ADAPTER, ConfigureAction, TakeAction
from nexus.presentation import evidence_files
from nexus.presentation.devices import Device, public_catalog
from nexus.presentation.laboratory import REPAIR, REVISION
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session
from nexus.protocol.stdio import _handle, run_jsonl
from nexus.render.laboratory import render_device, render_theory


def generate(family, seed=541, **kwargs):
    return generate_episode(seed, axis_version=2, science_family=family,
                            theory_level=3, discovery_level=5, planning_level=0,
                            resource_pressure=1, **kwargs)


@pytest.fixture(scope="module", params=(REPAIR, REVISION))
def laboratory(request):
    return generate(request.param)


def act(session, action):
    reply = session.act(session.state.turn, action, player_only=True)
    assert reply.ok
    return reply


def test_v4_records_keep_prechange_bindings():
    cases = json.loads((Path(__file__).parents[1] / "fixtures/laboratory-presentation-v4.json").read_text())
    for case in cases.values():
        episode = generate_episode(
            case["seed"], axis_version=2, science_family=case["family"],
            theory_level=case["theory"], discovery_level=case["discovery"],
            planning_level=0, resource_pressure=1, ontology_options=case["options"],
            presentation_version="sealed-facility-v4",
        )
        assert canonical_hash(evidence_files(episode.public)) == case["sha256"]


def test_same_devices_in_theory_manifest_http_and_stdio(laboratory):
    session = Session(laboratory)
    expected = public_catalog(laboratory.public.investigation.ontology)
    assert json.loads(session.evidence("theory.json"))["devices"] == expected
    for manifest in (session.manifest().model_dump(mode="json"),
                     TestClient(create_single_session_app(laboratory)).get("/manifest").json(),
                     _handle(session, {"operation": "manifest"})):
        assert manifest["action_contract"]["apparatus"]["devices"] == expected
    for record in expected.values():
        assert Device.model_validate(record).model_dump(mode="json", by_alias=True) == record
        assert len(record["examples"]) == 1
        assert set(record["examples"][0]) == {"requires", "action", "effect"}
    altered = session.manifest().action_contract["apparatus"]["devices"]
    next(iter(altered.values()))["examples"][0]["effect"] = "changed by caller"
    assert session.manifest().action_contract["apparatus"]["devices"] == expected


def test_serialized_stdio_preserves_parameter_order(laboratory):
    output = io.StringIO()
    run_jsonl(laboratory, io.StringIO('{"operation":"manifest"}\n'), output)
    manifest = json.loads(output.getvalue().splitlines()[-1])
    family = laboratory.public.investigation.ontology
    for name, record in manifest["action_contract"]["apparatus"]["devices"].items():
        if record["settings"] is None:
            continue
        expected = public_catalog(family)[name]
        assert record["settings"]["order"] == expected["settings"]["order"]
        # Key sorting must not change either the settings table or its bounds.
        rendered = []
        for device in (record, expected):
            out = io.StringIO()
            render_device(name, device, Console(file=out, width=120))
            rendered.append(out.getvalue())
        assert rendered[0] == rendered[1]


def test_reading_help_never_measures_selects_or_solves(laboratory, monkeypatch):
    from nexus.ontology.compositional import inference as repair_inference
    from nexus.ontology.compositional import laws as repair_laws
    from nexus.ontology.compositional import runtime as repair_runtime
    from nexus.ontology.discovery import runtime as discovery_runtime
    from nexus.ontology.revision import laws as revision_laws

    session = Session(laboratory)
    other = Session(generate(laboratory.public.investigation.ontology, seed=942))
    before = canonical_hash(session.state)

    def forbidden(*args, **kwargs):
        pytest.fail("Public help must not query hidden laws, measurements or plans")

    for module, names in (
        (repair_laws, ("world_for_seed", "response", "reading", "accepted")),
        (repair_runtime, ("world_for", "reading", "physical_plan")),
        (repair_inference, ("choose",)),
        (revision_laws, ("selection", "read", "read_world", "accepted", "compiled")),
        (discovery_runtime, ("physical_plan", "measurement", "transform")),
    ):
        for name in names:
            monkeypatch.setattr(module, name, forbidden)
    console = Console(file=io.StringIO(), width=120)
    for current in (session, other):
        shown = json.loads(current.evidence("theory.json"))
        records = current.manifest().action_contract["apparatus"]["devices"]
        assert shown["devices"] == public_catalog(laboratory.public.investigation.ontology)
        for name, record in records.items():
            render_device(name, record, console)
        render_theory(current.evidence("theory.json"), laboratory.public.investigation.ontology, console)
    assert canonical_hash(session.state) == before
    assert not session.trace


def test_standalone_examples_match_actual_effect_and_cost(laboratory):
    for record in public_catalog(laboratory.public.investigation.ontology).values():
        # Fresh session per example: none relies on a previous example or result.
        session = Session(laboratory)
        action = dict(record["examples"][0]["action"])
        if action["type"] == "probe":
            target = "stock" if action["artifact"] == "<survey-id>" else "carrier"
            act(session, TakeAction(artifact=target))
            action["artifact"] = session.observe().carried_artifacts[0].id
            if target == "carrier":
                act(session, ConfigureAction(machine="reader", settings=(1,)))
        before = session.state.model_copy(deep=True)
        reply = act(session, ACTION_ADAPTER.validate_python(action))
        assert session.state.turn == before.turn + record["actions"][action["type"]]["action_cost"]
        assert session.state.artifacts == before.artifacts
        if action["type"] == "configure":
            assert session.state.machines[action["machine"]].settings == tuple(action["settings"])
        else:
            assert session.state.machines == before.machines
            result = reply.events[0]["details"]["result"]["payload"]["reading"]
            value = result["values"][0] if isinstance(result, dict) else result
            assert value in (0, 1, 2)  # Output range only: help supplies no actual reading.


def test_published_settings_bounds_match_engine(laboratory):
    for name, record in public_catalog(laboratory.public.investigation.ontology).items():
        if record["settings"] is None:
            assert "configure" not in record["actions"]
            continue
        schema = record["settings"]["schema"]
        validator = Draft202012Validator(schema)
        validator.check_schema(schema)
        constraints = schema.get("prefixItems", [schema.get("items")] * schema["minItems"])
        low = [item["minimum"] for item in constraints]
        high = [item["maximum"] for item in constraints]
        cases = [low, high, low[:-1], high + [0]]
        if name == "reader":
            cases += [[1] * 8, [1] * 9]
        for i, constraint in enumerate(constraints):
            for value in (constraint["minimum"] - 1, constraint["maximum"] + 1):
                invalid = list(low)
                invalid[i] = value
                cases.append(invalid)
        for values in cases:
            session = Session(laboratory)
            try:
                action = ConfigureAction(machine=name, settings=values)
            except ValidationError:
                accepted = False
            else:
                accepted = session.act(0, action, player_only=True).ok
            assert accepted == validator.is_valid(values), (name, values)
            assert session.state.turn == int(accepted)


@pytest.mark.parametrize("policy", ("single", "recoverable"))
def test_consolidation_preserves_finish_and_assistance_contract(policy):
    episode = generate(REVISION, ontology_options={"finish_policy": policy, "consistency_check": "readings"})
    shown = json.loads(Session(episode).evidence("theory.json"))
    assert "reader" not in shown and "assembler" not in shown
    original = json.loads(episode.public.evidence_files["theory.json"])
    assert shown["consistency_assistance"] == original["consistency_assistance"]
    rejection = shown["submission"]["on_rejection"]
    if policy == "single":
        assert rejection == original["finish_policy"]["contract"]
    else:
        assert "recoverable while actions remain" in rejection


def test_local_help_is_free_and_task_precedes_terminology(laboratory, tmp_path):
    family = laboratory.public.investigation.ontology
    out = io.StringIO()
    render_theory(Session(laboratory).evidence("theory.json"), family, Console(file=out, width=120))
    text = out.getvalue()
    assert text.index("YOUR TASK") < text.index("Terms used in this task") < text.index("DETAILED RULES")
    save_episode(laboratory, tmp_path)
    name = "sensor" if family == REPAIR else "reader"
    result = CliRunner().invoke(app, ["play", str(tmp_path / "private.json")],
                               input=f"mission\nhelp {name}\nhelp unknown\nlog\nquit\n")
    assert result.exit_code == 0, result.exception
    assert "Standalone usage example" in result.stdout
    assert "No example" in result.stdout
    assert "Unknown device" in result.stdout
    assert "No actions yet." in result.stdout
