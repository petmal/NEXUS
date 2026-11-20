"""Playtest regressions: preserve measurements, disclosures and historical presentations."""

import io
import json
from pathlib import Path

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
from nexus.render.commands import parse
from nexus.render.laboratory import item_details, render_theory

ACTIONS = {"configure", "take", "operate", "probe", "move", "finish"}


@pytest.fixture(scope="module", params=(REPAIR, REVISION))
def laboratory(request):
    return generate_episode(
        541 if request.param == REPAIR else 2073, axis_version=2,
        science_family=request.param, theory_level=3, discovery_level=5,
        planning_level=0, resource_pressure=1, verifier_secret="clarity-test",
    )


def act(session, command):
    return session.act(session.state.turn, ACTION_ADAPTER.validate_python(parse(command, ACTIONS)), player_only=True)


@pytest.mark.parametrize("values", ([0, 1, 0], [0] * 8, [0, 11, 2, 7]))
def test_bracketed_and_spaced_settings_produce_identical_actions(values):
    commands = ["configure device " + " ".join(map(str, values)),
                "configure device " + json.dumps(values),
                'configure "device" ' + json.dumps(values, separators=(",", ":"))]
    parsed = [ACTION_ADAPTER.validate_python(parse(command, ACTIONS)) for command in commands]
    assert parsed[0] == parsed[1] == parsed[2]


@pytest.mark.parametrize("settings", ('["1"]', "[true]", "[null]", "[1.0]", "[[1]]", "[]", "[1,]", "[1] 2", "[1,2", "[0,...]"))
def test_bracketed_settings_reject_noninteger_or_malformed_arrays(settings):
    with pytest.raises(ValueError):
        parse("configure stage " + settings, ACTIONS)


def test_invalid_world_settings_are_free_and_atomic(laboratory):
    session = Session(laboratory)
    commands = (["configure stage [2,0,0,0,0,0,0,0]", "configure stage [0,3,0,0,0,0,0,0]",
                 "configure doser [0,0,0]"] if laboratory.public.investigation.ontology == REPAIR else
                ["configure reader [2]", "configure assembler [0,12,0,0]", "configure assembler [0,0,0]"])
    before = canonical_hash(session.state)
    for command in commands:
        reply = act(session, command)
        assert not reply.ok
        assert reply.current_turn == 0 and not session.trace
        assert canonical_hash(session.state) == before


def test_v3_records_keep_prechange_bindings():
    cases = json.loads((Path(__file__).parents[1] / "fixtures/laboratory-presentation-v3.json").read_text())
    for case in cases.values():
        episode = generate_episode(
            case["seed"], axis_version=2, science_family=case["family"],
            theory_level=case["theory"], discovery_level=case["discovery"],
            planning_level=0, resource_pressure=1, ontology_options=case["options"],
            presentation_version="sealed-facility-v3",
        )
        assert canonical_hash(evidence_files(episode.public)) == case["sha256"]


def test_same_clarified_evidence_on_both_transports_and_export(laboratory, tmp_path):
    session = Session(laboratory)
    client = TestClient(create_single_session_app(laboratory))
    save_episode(laboratory, tmp_path)
    before = laboratory.model_dump_json()
    for name in ("theory.json", "apparatus.txt"):
        text = session.evidence(name)
        assert client.get("/evidence/" + name).text == text
        assert _handle(session, {"operation": "evidence", "filename": name}) == {"filename": name, "content": text}
        assert (tmp_path / "attachments" / name).read_text() == text
    assert laboratory.model_dump_json() == before
    assert session.state.turn == 0
    shown = json.loads(session.evidence("theory.json"))
    original = json.loads(laboratory.public.evidence_files["theory.json"])
    for key in ("mission", "graphs", "primitives", "resolved", "archive", "provisional_model", "resolved_construction", "primitive_laws"):
        if key in original:
            assert shown[key] == original[key]
    if laboratory.public.investigation.ontology == REPAIR:
        assert "d=0 removes that offset only" in shown["context"]
        assert "same primitive may be used more than once" in shown["notation"]["choices"]
        assert "not persistent registers" in shown["notation"]["nodes"]
        assert shown["devices"]["stage"]["settings"]["order"] == ["context", "x", "y", "z", "a", "b", "c", "d"]
    else:
        assert "zero-based" in shown["notation"]["link_indices"]
        assert "ordinary nonnegative integers" in shown["notation"]["operators"]
        assert "unverified explanation" in shown["notation"]["records"]


def test_human_summaries_keep_applied_state_separate_from_pending_settings(laboratory):
    session = Session(laboratory)
    family = laboratory.public.investigation.ontology
    if family == REPAIR:
        act(session, "take seal")
        act(session, "take stock")
        survey = next(a.id for a in session.observe().carried_artifacts if a.id != "seal")
        act(session, "configure stage [1,2,1,0,0,0,0,0]")
        act(session, f"operate stage {survey}")
        preview = act(session, f"probe sensor {survey}")
        assert "context=1, x=2, y=1, z=0" in preview.message
        summaries = {a.id: item_details(family, a) for a in session.observe().carried_artifacts}
        assert "not measured since preparation" in summaries[survey]
        assert "Applied treatment: none" in summaries["seal"]
        assert "settings" not in summaries["seal"] and "reading" not in summaries["seal"]
        act(session, f"operate sensor {survey}")
        act(session, "configure stage [0,0,0,0,0,0,0,0]")
        view = session.observe()
        actual = item_details(family, next(a for a in view.carried_artifacts if a.id == survey))
        pending = item_details(family, next(m for m in view.visible_machines if m.id == "stage"))
        assert "context=1" in actual and "context=0" in pending
        assert "not measured" not in actual
    else:
        act(session, "take carrier")
        act(session, "configure reader [0,1,0]")
        act(session, "operate reader carrier")
        act(session, "configure reader [1]")
        act(session, "configure assembler [0,0,0,0]")
        act(session, "probe assembler carrier")
        view = session.observe()
        actual = item_details(family, view.carried_artifacts[0])
        pending = item_details(family, next(m for m in view.visible_machines if m.id == "reader"))
        assert "Installed cartridge: none" in actual
        assert "word [0, 1, 0]" in actual
        assert "Selected reference word: [1]" in pending
        act(session, "operate assembler carrier")
        actual = item_details(family, session.observe().carried_artifacts[0])
        assert "mode0_first_link=0" in actual and "Stored reference reading: none" in actual


def test_theory_tables_and_installed_console(laboratory, tmp_path):
    session = Session(laboratory)
    family = laboratory.public.investigation.ontology
    content = session.evidence("theory.json")
    out = io.StringIO()
    render_theory(content, family, Console(file=out, width=140))
    text = out.getvalue()
    assert ("Fixed exit checks" if family == REPAIR else "Link indices") in text
    assert ("Possible graphs" if family == REPAIR else "q3") in text
    save_episode(laboratory, tmp_path)
    cmd = "configure stage [0,0,0,0,0,0,0,0]" if family == REPAIR else "configure reader [0,1,0]"
    result = CliRunner().invoke(app, ["play", str(tmp_path / "private.json")],
                               input=f"evidence theory.json\n{cmd}\nlog\nquit\n")
    assert result.exit_code == 0, result.exception
    assert "Invalid action" not in result.stdout
    assert "Turn 1 | Applied: configure" in result.stdout


def test_reference_policy_preserves_actions_state_and_receipt(laboratory):
    from nexus.ontology.compositional.policy import public_policy as repair_policy
    from nexus.ontology.discovery.policy import public_policy as revision_policy

    policy = repair_policy if laboratory.public.investigation.ontology == REPAIR else revision_policy
    sessions = [Session(attach(laboratory, version)) for version in ("sealed-facility-v3", "sealed-facility-v4", "sealed-facility-v5")]
    for session in sessions:
        policy(session, evidence_files(session.episode.public))
        assert session.state.terminal_status.value == "won"
    for session in sessions[1:]:
        assert sessions[0].trace == session.trace
        assert sessions[0].state == session.state
        assert sessions[0].trace[-1].victory_code == session.trace[-1].victory_code
