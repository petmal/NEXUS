"""Teach instrument semantics without changing experiments, truth or old sessions."""

import io
import json

import pytest
from fastapi.testclient import TestClient
from rich.console import Console
from typer.testing import CliRunner

from nexus.cli import app
from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.io import save_episode
from nexus.models.actions import ACTION_ADAPTER
from nexus.presentation import attach, evidence_files
from nexus.presentation.laboratory import REPAIR, REVISION
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session
from nexus.protocol.stdio import _handle
from nexus.render.commands import log_entry, parse
from nexus.render.laboratory import item_details, render_theory
from nexus.render.player import render_player

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


def clarity_act(session, command):
    return session.act(session.state.turn, ACTION_ADAPTER.validate_python(parse(command, ACTIONS)), player_only=True)


def test_invalid_world_settings_are_free_and_atomic(clarity_laboratory):
    session = Session(clarity_laboratory)
    commands = (["configure stage [2,0,0,0,0,0,0,0]", "configure stage [0,3,0,0,0,0,0,0]",
                 "configure doser [0,0,0]"] if clarity_laboratory.public.investigation.ontology == REPAIR else
                ["configure reader [2]", "configure assembler [0,12,0,0]", "configure assembler [0,0,0]"])
    before = canonical_hash(session.state)
    for command in commands:
        reply = clarity_act(session, command)
        assert not reply.ok
        assert reply.current_turn == 0 and not session.trace
        assert canonical_hash(session.state) == before


def test_same_clarified_evidence_on_both_transports_and_export(clarity_laboratory, tmp_path):
    session = Session(clarity_laboratory)
    client = TestClient(create_single_session_app(clarity_laboratory))
    save_episode(clarity_laboratory, tmp_path)
    before = clarity_laboratory.model_dump_json()
    for name in ("theory.json", "apparatus.txt"):
        text = session.evidence(name)
        assert client.get("/evidence/" + name).text == text
        assert _handle(session, {"operation": "evidence", "filename": name}) == {"filename": name, "content": text}
        assert (tmp_path / "attachments" / name).read_text() == text
    assert clarity_laboratory.model_dump_json() == before
    assert session.state.turn == 0
    shown = json.loads(session.evidence("theory.json"))
    original = json.loads(clarity_laboratory.public.evidence_files["theory.json"])
    for key in ("mission", "graphs", "primitives", "resolved", "archive", "provisional_model", "resolved_construction", "primitive_laws"):
        if key in original:
            assert shown[key] == original[key]
    if clarity_laboratory.public.investigation.ontology == REPAIR:
        assert "d=0 removes that offset only" in shown["context"]
        assert "same primitive may be used more than once" in shown["notation"]["choices"]
        assert "not persistent registers" in shown["notation"]["nodes"]
        assert shown["devices"]["stage"]["settings"]["order"] == ["context", "x", "y", "z", "a", "b", "c", "d"]
    else:
        assert "zero-based" in shown["notation"]["link_indices"]
        assert "ordinary nonnegative integers" in shown["notation"]["operators"]
        assert "unverified explanation" in shown["notation"]["records"]


def test_human_summaries_keep_applied_state_separate_from_pending_settings(clarity_laboratory):
    session = Session(clarity_laboratory)
    family = clarity_laboratory.public.investigation.ontology
    if family == REPAIR:
        clarity_act(session, "take seal")
        clarity_act(session, "take stock")
        survey = next(a.id for a in session.observe().carried_artifacts if a.id != "seal")
        clarity_act(session, "configure stage [1,2,1,0,0,0,0,0]")
        clarity_act(session, f"operate stage {survey}")
        preview = clarity_act(session, f"probe sensor {survey}")
        assert "context=1, x=2, y=1, z=0" in preview.message
        summaries = {a.id: item_details(family, a) for a in session.observe().carried_artifacts}
        assert "not measured since preparation" in summaries[survey]
        assert "Applied treatment: none" in summaries["seal"]
        assert "settings" not in summaries["seal"] and "reading" not in summaries["seal"]
        clarity_act(session, f"operate sensor {survey}")
        clarity_act(session, "configure stage [0,0,0,0,0,0,0,0]")
        view = session.observe()
        actual = item_details(family, next(a for a in view.carried_artifacts if a.id == survey))
        pending = item_details(family, next(m for m in view.visible_machines if m.id == "stage"))
        assert "context=1" in actual and "context=0" in pending
        assert "not measured" not in actual
    else:
        clarity_act(session, "take carrier")
        clarity_act(session, "configure reader [0,1,0]")
        clarity_act(session, "operate reader carrier")
        clarity_act(session, "configure reader [1]")
        clarity_act(session, "configure assembler [0,0,0,0]")
        clarity_act(session, "probe assembler carrier")
        view = session.observe()
        actual = item_details(family, view.carried_artifacts[0])
        pending = item_details(family, next(m for m in view.visible_machines if m.id == "reader"))
        assert "Installed cartridge: none" in actual
        assert "word [0, 1, 0]" in actual
        assert "Selected reference word: [1]" in pending
        clarity_act(session, "operate assembler carrier")
        actual = item_details(family, session.observe().carried_artifacts[0])
        assert "mode0_first_link=0" in actual and "Stored reference reading: none" in actual


def test_theory_tables_and_installed_console(clarity_laboratory, tmp_path):
    session = Session(clarity_laboratory)
    family = clarity_laboratory.public.investigation.ontology
    content = session.evidence("theory.json")
    out = io.StringIO()
    render_theory(content, family, Console(file=out, width=140))
    text = out.getvalue()
    assert ("Fixed exit checks" if family == REPAIR else "Link indices") in text
    assert ("Possible graphs" if family == REPAIR else "q3") in text
    save_episode(clarity_laboratory, tmp_path)
    cmd = "configure stage [0,0,0,0,0,0,0,0]" if family == REPAIR else "configure reader [0,1,0]"
    result = CliRunner().invoke(app, ["play", str(tmp_path / "private.json")],
                               input=f"evidence theory.json\n{cmd}\nlog\nquit\n")
    assert result.exit_code == 0, result.exception
    assert "Invalid action" not in result.stdout
    assert "Turn 1 | Applied: configure" in result.stdout


def test_reference_policy_preserves_actions_state_and_receipt(clarity_laboratory):
    from nexus.ontology.compositional.policy import public_policy as repair_policy
    from nexus.ontology.discovery.policy import public_policy as revision_policy

    policy = repair_policy if clarity_laboratory.public.investigation.ontology == REPAIR else revision_policy
    sessions = [Session(attach(clarity_laboratory, version)) for version in ("sealed-facility-v3", "sealed-facility-v4", "sealed-facility-v5", "sealed-facility-v6")]
    for session in sessions:
        policy(session, evidence_files(session.episode.public))
        assert session.state.terminal_status.value == "won"
    for session in sessions[1:]:
        assert sessions[0].trace == session.trace
        assert sessions[0].state == session.state
        assert sessions[0].trace[-1].victory_code == session.trace[-1].victory_code


def role_act(session, command):
    action = ACTION_ADAPTER.validate_python(parse(command, {"take", "probe", "operate", "configure"}))
    response = session.act(session.state.turn, action, player_only=True)
    assert response.ok
    return action, response


def test_stock_and_workpiece_roles_do_not_imply_reference_or_submission(role_laboratory):
    family = role_laboratory.public.investigation.ontology
    session = Session(role_laboratory)
    stock = "stock" if family == REPAIR else "blank-stock"
    out = io.StringIO()
    console = Console(file=out, width=140)
    render_player(session.observe(), console=console, family=family, roles=True)
    role_act(session, "take " + stock)
    item = session.observe().carried_artifacts[0]
    assert item.id != stock
    render_player(session.observe(), console=console, family=family, roles=True)
    text = out.getvalue()
    assert "Remaining: unlimited" in text
    if family == REVISION:
        assert "not the reference device" in text
        assert "Blank workpiece; cannot replace carrier at finish" in text
        assert item.payload == {"build": None, "reading": None}
        role_act(session, "take carrier")
        render_player(session.observe(), console=console, family=family, roles=True)
        assert "Mission carrier" in out.getvalue()
        theory = json.loads(session.evidence("theory.json"))
        assert "q0 + q1 + q2 + q3 = 5" in theory["notation"]["inventory"]
        assert "1 packet if even (including zero), 2 if odd" in theory["notation"]["transfer"]
        assert "Equal displays need not mean equal q0 values" in theory["notation"]["display"]
    else:
        assert "Reusable survey supply" in text and "Reusable survey" in text


def test_measuring_probe_log_is_not_called_a_hypothetical_preview(role_laboratory):
    session = Session(role_laboratory)
    family = role_laboratory.public.investigation.ontology
    role_act(session, "take " + ("stock" if family == REPAIR else "blank-stock"))
    item = session.observe().carried_artifacts[0]
    machine = "sensor" if family == REPAIR else "reader"
    if family == REVISION:
        role_act(session, "configure reader [0]")
    before = session.state.artifacts[item.id].model_copy(deep=True)
    action, response = role_act(session, f"probe {machine} {item.id}")
    logged = log_entry(action, response)
    assert "| Probe:" in logged
    assert "| Preview:" not in logged
    assert session.state.artifacts[item.id] == before
    assert ("Sensor response" if family == REPAIR else "Reference display") in response.message


@pytest.mark.parametrize("role_laboratory", [REPAIR], indirect=True)
def test_repair_wrong_material_is_a_paid_noop_with_matching_help(role_laboratory):
    session = Session(role_laboratory)
    role_act(session, "take seal")
    role_act(session, "take stock")
    survey = next(item.id for item in session.observe().carried_artifacts if item.id != "seal")
    for machine, target in (("stage", "seal"), ("sensor", "seal"), ("doser", survey)):
        help_text = session.manifest().action_contract["apparatus"]["devices"][machine]["targets"]
        assert "has no effect and still costs an action" in help_text
        for verb in ("probe", "operate"):
            before = session.state.model_copy(deep=True)
            _, response = role_act(session, f"{verb} {machine} {target}")
            assert session.state.turn == before.turn + 1
            assert session.state.artifacts == before.artifacts
            assert "has no effect on this material" in response.message


@pytest.mark.parametrize("seed", [541, 586], ids=["F05", "F08"])
def test_disclosed_repair_needs_only_the_seal(seed):
    episode = generate_episode(seed, axis_version=2, science_family=REPAIR, theory_level=0,
                               discovery_level=0, planning_level=1, resource_pressure=1)
    session = Session(episode)
    assert "To run a survey, take stock." in session.evidence("apparatus.txt")
    assert "Take seal and take stock." in Session(attach(episode, "sealed-facility-v6")).evidence("apparatus.txt")
    dose = json.loads(session.evidence("theory.json"))["resolved"]
    for command in ("take seal", "move array", "configure doser " + " ".join(map(str, dose)),
                    "operate doser seal", "finish"):
        reply = session.act(session.state.turn, action(command), player_only=True)
        assert reply.ok
    assert reply.victory_code and session.state.turn == 5
