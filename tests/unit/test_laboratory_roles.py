"""Final playtest regressions: object roles, no-op costs and versioned public help."""

import io
import json
from pathlib import Path

import pytest
from rich.console import Console

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.models.actions import ACTION_ADAPTER
from nexus.presentation import attach, evidence_files
from nexus.presentation.laboratory import REPAIR, REVISION
from nexus.protocol.session import Session
from nexus.render.commands import candidates, log_entry, parse
from nexus.render.player import render_player


@pytest.fixture(scope="module", params=(REPAIR, REVISION))
def laboratory(request):
    return generate_episode(541, axis_version=2, science_family=request.param,
                            theory_level=3, discovery_level=5, planning_level=0,
                            resource_pressure=1)


def act(session, command):
    action = ACTION_ADAPTER.validate_python(parse(command, {"take", "probe", "operate", "configure"}))
    response = session.act(session.state.turn, action, player_only=True)
    assert response.ok
    return action, response


def test_v5_public_records_remain_frozen():
    cases = json.loads((Path(__file__).parents[1] / "fixtures/laboratory-presentation-v5.json").read_text())
    for case in cases.values():
        episode = generate_episode(
            case["seed"], axis_version=2, science_family=case["family"],
            theory_level=case["theory"], discovery_level=case["discovery"],
            planning_level=0, resource_pressure=1, ontology_options=case["options"],
            presentation_version="sealed-facility-v5",
        )
        manifest = Session(episode).manifest()
        assert canonical_hash(evidence_files(episode.public)) == case["sha256"]
        assert manifest.description == case["description"]
        assert canonical_hash(manifest.action_contract) == case["action_contract_sha256"]


def test_facility_task_precedes_glossary_and_help_completes_only_listed_devices(laboratory):
    session = Session(laboratory)
    assert session.evidence("facility.txt").startswith("YOUR TASK\n")
    devices = session.manifest().action_contract["apparatus"]["devices"]
    assert candidates("help ", (), (), session.observe(), devices=devices) == sorted(devices)
    assert candidates("help se", (), (), session.observe(), devices=devices) == (
        ["sensor"] if laboratory.public.investigation.ontology == REPAIR else [])
    assert candidates("help ", (), (), session.observe()) == []


def test_stock_and_workpiece_roles_do_not_imply_reference_or_submission(laboratory):
    family = laboratory.public.investigation.ontology
    session = Session(laboratory)
    stock = "stock" if family == REPAIR else "blank-stock"
    out = io.StringIO()
    console = Console(file=out, width=140)
    render_player(session.observe(), console=console, family=family, roles=True)
    act(session, "take " + stock)
    item = session.observe().carried_artifacts[0]
    assert item.id != stock
    render_player(session.observe(), console=console, family=family, roles=True)
    text = out.getvalue()
    assert "Remaining: unlimited" in text
    if family == REVISION:
        assert "not the reference device" in text
        assert "Blank workpiece; cannot replace carrier at finish" in text
        assert item.payload == {"build": None, "reading": None}
        act(session, "take carrier")
        render_player(session.observe(), console=console, family=family, roles=True)
        assert "Mission carrier" in out.getvalue()
        theory = json.loads(session.evidence("theory.json"))
        assert "q0 + q1 + q2 + q3 = 5" in theory["notation"]["inventory"]
        assert "1 packet if even (including zero), 2 if odd" in theory["notation"]["transfer"]
        assert "Equal displays need not mean equal q0 values" in theory["notation"]["display"]
    else:
        assert "Reusable survey supply" in text and "Reusable survey" in text


def test_measuring_probe_log_is_not_called_a_hypothetical_preview(laboratory):
    session = Session(laboratory)
    family = laboratory.public.investigation.ontology
    act(session, "take " + ("stock" if family == REPAIR else "blank-stock"))
    item = session.observe().carried_artifacts[0]
    machine = "sensor" if family == REPAIR else "reader"
    if family == REVISION:
        act(session, "configure reader [0]")
    before = session.state.artifacts[item.id].model_copy(deep=True)
    action, response = act(session, f"probe {machine} {item.id}")
    logged = log_entry(action, response)
    assert "| Probe:" in logged
    assert "| Preview:" not in logged
    assert session.state.artifacts[item.id] == before
    assert ("Sensor response" if family == REPAIR else "Reference display") in response.message


def test_repair_wrong_material_is_a_paid_noop_with_matching_help(laboratory):
    if laboratory.public.investigation.ontology != REPAIR:
        pytest.skip("Repair has distinct material types")
    session = Session(laboratory)
    act(session, "take seal")
    act(session, "take stock")
    survey = next(item.id for item in session.observe().carried_artifacts if item.id != "seal")
    for machine, target in (("stage", "seal"), ("sensor", "seal"), ("doser", survey)):
        help_text = session.manifest().action_contract["apparatus"]["devices"][machine]["targets"]
        assert "has no effect and still costs an action" in help_text
        for verb in ("probe", "operate"):
            before = session.state.model_copy(deep=True)
            _, response = act(session, f"{verb} {machine} {target}")
            assert session.state.turn == before.turn + 1
            assert session.state.artifacts == before.artifacts
            assert "has no effect on this material" in response.message


def test_v6_does_not_add_example_measurements_or_alter_numeric_records(laboratory):
    old = Session(attach(laboratory, "sealed-facility-v5"))
    new = Session(laboratory)
    before, after = (json.loads(s.evidence("theory.json")) for s in (old, new))
    for name, value in before.items():
        if name not in ("devices", "terms", "notation"):
            assert after[name] == value
    for name, device in before["devices"].items():
        assert after["devices"][name] == {**device, "targets": after["devices"][name]["targets"]}
    assert not new.trace and new.state == old.state
