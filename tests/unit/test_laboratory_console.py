"""Teach instrument semantics without changing experiments, truth or old sessions."""

import json

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from nexus.cli import app
from nexus.generator import generate_episode
from nexus.io import save_episode
from nexus.models.actions import ACTION_ADAPTER
from nexus.presentation import attach
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session
from nexus.protocol.stdio import _handle
from nexus.render.commands import log_entry, parse

REPAIR = "compositional-repair-v1"
REVISION = "model-revision-v1"
ACTIONS = {"take", "move", "configure", "probe", "operate", "finish"}


@pytest.fixture(scope="module", params=(REPAIR, REVISION))
def laboratory(request):
    family = request.param
    return generate_episode(
        541 if family == REPAIR else 5866, axis_version=2, science_family=family,
        theory_level=3, discovery_level=5, planning_level=int(family == REPAIR),
        resource_pressure=1, verifier_secret="laboratory-console",
    )


def action(command):
    return ACTION_ADAPTER.validate_python(parse(command, ACTIONS))


def artifact(reply, name):
    return next(a["payload"] for a in reply["observation"]["carried_artifacts"] if a["id"] == name)


@pytest.mark.parametrize("transport", ("http", "stdio"))
def test_instrument_readings_and_installation(laboratory, transport):
    session = Session(laboratory)
    client = TestClient(create_single_session_app(laboratory))
    turn = 0

    def send(command):
        nonlocal turn
        request = {"expected_turn": turn, "action": parse(command, ACTIONS)}
        reply = (client.post("/action", json=request).json() if transport == "http" else
                 _handle(session, {"operation": "action", **request}))
        assert reply["ok"], reply
        assert reply["current_turn"] == turn + 1
        turn += 1
        assert "domain-v1" not in json.dumps(reply)
        assert laboratory.public.investigation.ontology not in json.dumps(reply)
        return reply

    if laboratory.public.investigation.ontology == REPAIR:
        send("take seal")
        taken = send("take stock")
        survey = next(a["id"] for a in taken["observation"]["carried_artifacts"] if a["id"] != "seal")
        send("move array")
        settings = [1, 2, 1, 0, 2, 1, 0, 1]
        configured = send("configure stage " + " ".join(map(str, settings)))
        assert "Artifacts unchanged" in configured["message"]
        assert artifact(configured, survey)["settings"] == [0] * 8
        preview = send(f"probe stage {survey}")
        assert "Preparation preview" in preview["message"]
        assert artifact(preview, survey)["settings"] == [0] * 8
        prepared = send(f"operate stage {survey}")
        assert artifact(prepared, survey)["settings"] == settings
        preview = send(f"probe sensor {survey}")
        assert "Sensor response:" in preview["message"]
        assert str(settings) in preview["message"]
        assert artifact(preview, survey)["reading"] is None
        measured = send(f"operate sensor {survey}")
        value = artifact(measured, survey)["reading"]
        assert f"Sensor response: {value}." in preview["message"]
        assert f"Reading stored on {survey}." in measured["message"]
        configured = send("configure stage 0 0 0 0 0 0 0 0")
        assert artifact(configured, survey)["reading"] == value
        assert artifact(configured, survey)["settings"] == settings
        prepared = send(f"operate stage {survey}")
        assert artifact(prepared, survey)["reading"] is None
        assert "Previous sensor reading cleared" in prepared["message"]
        configured = send("configure doser 0 1 2 0")
        assert artifact(configured, "seal")["doses"] is None
        preview = send("probe doser seal")
        assert "Mission not checked" in preview["message"]
        assert artifact(preview, "seal")["doses"] is None
        treated = send("operate doser seal")
        assert artifact(treated, "seal")["doses"] == [0, 1, 2, 0]
        assert "Use finish to check" in treated["message"]
        ineffective = send("operate sensor seal")
        assert "no effect" in ineffective["message"]
        assert artifact(ineffective, "seal") == artifact(treated, "seal")
        ineffective = send(f"operate doser {survey}")
        assert "no effect" in ineffective["message"]
    else:
        send("take carrier")
        configured = send("configure reader 0")
        assert "measure the reference" in configured["message"]
        preview = send("probe reader carrier")
        assert artifact(preview, "carrier")["reading"] is None
        assert "Installed cartridge not tested" in preview["message"]
        measured = send("operate reader carrier")
        cached = artifact(measured, "carrier")["reading"]
        expected = json.loads(session.evidence("theory.json"))["archive"][0]["display"]
        assert cached == {"query": [0], "values": [expected]}
        assert f"Reference display after word [0]: {expected}." in preview["message"]
        configured = send("configure reader 1 0")
        assert artifact(configured, "carrier")["reading"] == cached
        send("configure assembler 0 0 0 0")
        preview = send("probe assembler carrier")
        assert "Cartridge preview" in preview["message"]
        assert artifact(preview, "carrier")["build"] is None
        assert artifact(preview, "carrier")["reading"] == cached
        installed = send("operate assembler carrier")
        assert artifact(installed, "carrier")["build"] == [0] * 4
        assert artifact(installed, "carrier")["reading"] is None
        assert "Mission not checked" in installed["message"]
        send("configure reader 0")
        measured = send("operate reader carrier")
        assert artifact(measured, "carrier")["reading"] == cached
        assert artifact(measured, "carrier")["build"] == [0] * 4


def test_laboratory_evidence_and_console_log(laboratory, tmp_path):
    session = Session(laboratory)
    family = laboratory.public.investigation.ontology
    guide = session.evidence("apparatus.txt")
    old = Session(attach(laboratory, "sealed-facility-v2"))
    assert old.evidence("apparatus.txt") == laboratory.public.evidence_files["apparatus.txt"]
    assert guide != old.evidence("apparatus.txt")
    assert ("Separate queries do not continue one another" if family == REVISION else
            "Context is a stage setting, separate from the facility phase") in guide
    # Reading and recording a public response never consumes another action.
    commands = (["take seal", "move array", "configure doser 0 0 0 0", "probe doser seal"]
                if family == REPAIR else
                ["take carrier", "configure reader 0", "probe reader carrier"])
    for command in commands:
        step = action(command)
        response = session.act(session.state.turn, step, player_only=True)
        old_response = old.act(old.state.turn, step, player_only=True)
        assert response.ok and old_response.ok
        assert session.state == old.state and session.trace == old.trace
    turn = session.state.turn
    text = log_entry(step, response)
    assert response.message in text
    assert ("Reference display" if family == REVISION else "Treatment preview") in text
    retry = session.act(turn - 1, step, player_only=True)
    assert retry.duplicate and retry.message == response.message
    assert session.state.turn == turn
    save_episode(laboratory, tmp_path)
    result = CliRunner().invoke(app, ["play", str(tmp_path / "private.json")],
                               input="\n".join(("evidence apparatus.txt", *commands, "log", "quit", "")))
    assert result.exit_code == 0, result.exception
    assert " ".join(text.split()) in " ".join(result.stdout.split())


@pytest.mark.parametrize("policy", ("recoverable", "single"))
def test_revision_guide_retains_finish_policy(policy):
    from nexus.ontology.revision.schema import GenerationOptions

    options = GenerationOptions(finish_policy=policy).model_dump(mode="json")
    episode = generate_episode(5866, axis_version=2, science_family=REVISION,
                               theory_level=0, discovery_level=0, planning_level=0,
                               resource_pressure=1, ontology_options=options)
    session = Session(episode)
    guide = session.evidence("apparatus.txt")
    assert ("ends the attempt" in guide) == (policy == "single")
    assert ("can be retried" in guide) == (policy == "recoverable")
    assert json.loads(session.evidence("theory.json"))["resolved_construction"] is not None
