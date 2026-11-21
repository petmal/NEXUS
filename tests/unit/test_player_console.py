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
from nexus.render.commands import candidates, parse

MOVES = ("take seal", "move array", "probe vek seal", "operate sul seal",
         "probe vek seal", "operate sul seal", "probe vek seal")
READINGS = [2, 0, 0, 0, 4]


@pytest.fixture(scope="module")
def episode():
    return generate_episode(229, axis_version=2, science_family="stateful-discovery-v1",
                            theory_level=3, discovery_level=5, planning_level=1, resource_pressure=1,
                            verifier_secret="console-test")


@pytest.mark.parametrize("transport", ("http", "stdio"))
def test_real_player_sequence(episode, transport):
    session = Session(episode)
    client = TestClient(create_single_session_app(episode))
    actions = {r["type"] for r in session.manifest().action_contract["reference"]}
    for turn, command in enumerate(MOVES):
        payload = {"expected_turn": turn, "action": parse(command, actions)}
        reply = (client.post("/action", json=payload).json() if transport == "http" else
                 _handle(session, {"operation": "action", **payload}))
        assert reply["ok"]
        assert "domain-v1" not in json.dumps(reply)
        assert "stateful-discovery-v1" not in json.dumps(reply)
        if turn >= 2:
            reading = READINGS[turn - 2]
            operation, machine, _ = command.split()
            expected = (f"Mode {machine} preview: seal display would read {reading}. Seal unchanged."
                        if operation == "probe" else f"Mode {machine} applied. Seal display reads {reading}.")
            assert reply["message"] == expected
            assert reply["events"][0]["details"]["result"]["payload"]["reading"] == reading
            assert reply["observation"]["carried_artifacts"][0]["payload"]["reading"] == 0
            assert reply["observation"]["actions_remaining"] == 64 - turn - 1
        if turn == 2:
            duplicate = (client.post("/action", json=payload).json() if transport == "http" else
                         _handle(session, {"operation": "action", **payload}))
            assert duplicate["duplicate"] and duplicate["message"] == reply["message"]


def test_console_history_and_evidence(episode, tmp_path):
    save_episode(episode, tmp_path)
    output = CliRunner().invoke(app, ["play", str(tmp_path / "private.json")],
                                input="\n".join(("evidence theory.json", *MOVES, "log", "quit", "")))
    assert output.exit_code == 0, output.exception
    assert '  "instrument":' in output.stdout
    assert "Turn 7 | Probe: probe vek seal" in output.stdout
    assert "Turn 6 | Applied: operate sul seal" in output.stdout
    assert "turn 8" not in output.stdout
    assert "stateful-discovery-v1" not in output.stdout


def test_public_completion_and_historical_versions(episode):
    session = Session(episode)
    actions = {row["type"] for row in session.manifest().action_contract["reference"]}
    view = session.observe()
    assert candidates("take ", actions, (), view) == ["seal"]
    assert candidates("probe ", actions, (), view) == []
    for cmd in MOVES[:2]:
        session.act(session.status().turn, ACTION_ADAPTER.validate_python(parse(cmd, actions)))
    assert candidates("probe s", actions, (), session.observe()) == ["sul"]
    assert candidates("probe sul ", actions, (), session.observe()) == ["seal"]
    assert candidates("evidence th", actions, ["theory.json"], view) == ["theory.json"]
    for version in ("sealed-facility-v1", "sealed-facility-v2"):
        old = Session(attach(episode, version))
        assert "T0 discloses" in old.evidence("theory.json")
        assert old.observe().visible_artifacts[0].ontology == "stateful-discovery-v1"
    current = json.loads(session.evidence("theory.json"))
    assert current["specification"]["target"] == [1, 2, 1, 2]
    assert current["specification"]["resolved"] is None
    assert not {"theory", "discovery", "experimental"} & current["specification"].keys()



def test_terminal_editing_history_and_tab(monkeypatch, episode):
    import sys
    from functools import partial

    import prompt_toolkit
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    from nexus.render.commands import reader

    session = Session(episode)
    actions = {row["type"] for row in session.manifest().action_contract["reference"]}
    for cmd in MOVES[:2]:
        session.act(session.status().turn, ACTION_ADAPTER.validate_python(parse(cmd, actions)))
    view = session.observe()
    with create_pipe_input() as keys:
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        monkeypatch.setattr(prompt_toolkit, "PromptSession",
                            partial(prompt_toolkit.PromptSession, input=keys, output=DummyOutput()))
        read = reader(None, actions, ())
        keys.send_text("probe su\t seal\r")
        assert read(view) == "probe sul seal"
        # Recall, move left four characters, and insert in the middle of the line.
        keys.send_text("\x1b[A" + "\x1b[D" * 4 + "test-" + "\r")
        assert read(view) == "probe sul test-seal"


def test_historical_replay_and_terminal_receipt_survive_presentation_change(episode):
    from nexus.ontology.stateful.runtime import physical_plan
    from nexus.engine.replay import replay

    original = Session(attach(episode, "sealed-facility-v2"))
    current = Session(episode)
    for step in physical_plan(episode):
        turn = current.status().turn
        old = original.act(turn, step, player_only=True)
        new = current.act(turn, step, player_only=True)
        assert new.ok == old.ok and new.current_turn == old.current_turn
    assert new.victory_code and new.victory_code == old.victory_code
    assert new.performance is None and old.performance is not None
    assert current.act(turn, step, player_only=True).performance is None
    assert current.trace == original.trace
    assert replay(episode, original.trace) == current.state
    assert current.finalize_attempt()[1].terminal_status == "won"
