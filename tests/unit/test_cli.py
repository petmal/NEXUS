import json

import pytest

from typer.testing import CliRunner

from nexus.cli import app
from nexus.generator import generate_episode
from nexus.io import save_episode


runner = CliRunner()


def test_help_alias_and_actions_command():
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 0
    assert "generate" in result.stdout
    assert "qualify" in result.stdout
    assert "inspect" in result.stdout
    assert "actions" in result.stdout
    assert "serve-session" in result.stdout
    assert "request" in result.stdout
    assert "health" in result.stdout
    assert "validate" in result.stdout

    actions = runner.invoke(app, ["actions"])
    assert actions.exit_code == 0
    assert "take" in actions.stdout
    assert "operate" in actions.stdout
    assert "probe" in actions.stdout
    assert "finish" in actions.stdout


def test_generate_exposes_generic_difficulty_knobs_and_operator_summary(tmp_path):
    output = tmp_path / "episode"
    result = runner.invoke(
        app,
        [
            "generate",
            str(output),
            "--seed",
            "1202",
            "--discovery-level",
            "2",
            "--planning-level",
            "0",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "discovery=2" in result.stdout
    assert "planning=0" in result.stdout
    assert "optimal=" in result.stdout
    assert "probes=1" in result.stdout
    assert "budget=" in result.stdout
    assert "recommended-tool-calls=" in result.stdout

    inspected = runner.invoke(app, ["inspect", str(output / "private.json")])
    assert inspected.exit_code == 0
    assert '"discovery_level": 2' in inspected.stdout
    assert '"planning_level": 0' in inspected.stdout
    assert '"optimal_action_count":' in inspected.stdout
    assert '"recommended_tool_call_limit":' in inspected.stdout


def test_play_evidence_meta_command_matches_player_evidence_access(tmp_path):
    episode = generate_episode(2210, discovery_level=0, planning_level=0)
    save_episode(episode, tmp_path)

    result = runner.invoke(
        app,
        ["play", str(tmp_path / "private.json")],
        input="evidence measurements.csv\nquit\n",
    )

    assert result.exit_code == 0, result.stdout
    assert "Evidence files:" in result.stdout
    assert "facility_manual.txt" in result.stdout
    assert "measurements.csv" in result.stdout
    assert "phase,shape,input_value,input_polarity,input_orientation" in result.stdout
    assert "invalid action JSON" not in result.stdout


def test_story_ending_requires_a_real_successful_finish(tmp_path):
    episode = generate_episode(2210, discovery_level=0, planning_level=0)
    save_episode(episode, tmp_path)
    failed = runner.invoke(
        app, ["play", str(tmp_path / "private.json")],
        input='{"type":"finish"}\nquit\n',
    )
    assert failed.exit_code == 0
    assert "Exit clearance granted." not in failed.stdout
    won = runner.invoke(
        app, ["play", str(tmp_path / "private.json")],
        input="\n".join(json.dumps(action) for action in episode.reference_plan) + "\n",
    )
    assert won.exit_code == 0, won.stdout
    assert "Exit clearance granted." in won.stdout
    assert "Victory receipt: NX-" in won.stdout


@pytest.mark.slow
def test_generate_supports_selective_discovery_level_four(tmp_path):
    result = runner.invoke(
        app,
        [
            "generate",
            str(tmp_path / "episode-d4"),
            "--seed",
            "17",
            "--discovery-level",
            "4",
            "--planning-level",
            "0",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "discovery=4" in result.stdout


@pytest.mark.slow
def test_generate_supports_constructed_discovery_level_five(tmp_path):
    result = runner.invoke(
        app,
        [
            "generate",
            str(tmp_path / "episode-d5"),
            "--seed",
            "17",
            "--discovery-level",
            "5",
            "--planning-level",
            "0",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "discovery=5" in result.stdout


def test_generate_rejects_out_of_range_difficulty_levels(tmp_path):
    result = runner.invoke(
        app,
        ["generate", str(tmp_path / "episode"), "--discovery-level", "6"],
    )
    assert result.exit_code != 0



@pytest.mark.slow
def test_generate_supports_dependency_planning_and_resource_pressure(tmp_path):
    result = runner.invoke(
        app,
        [
            "generate",
            str(tmp_path / "episode-p3-r2"),
            "--seed",
            "17",
            "--discovery-level",
            "2",
            "--planning-level",
            "3",
            "--resource-pressure",
            "2",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "planning=3" in result.stdout
    assert "resource-pressure=2" in result.stdout


def test_generate_rejects_out_of_range_planning_and_resource_pressure(tmp_path):
    planning = runner.invoke(
        app,
        ["generate", str(tmp_path / "bad-p"), "--planning-level", "4"],
    )
    pressure = runner.invoke(
        app,
        ["generate", str(tmp_path / "bad-r"), "--resource-pressure", "3"],
    )
    assert planning.exit_code != 0
    assert pressure.exit_code != 0


def test_cli_uses_current_family_action_contract(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["actions", "--axis-version", "2"],
        env={"NEXUS_SCIENCE_FAMILY": "resonant-network-v1", "COLUMNS": "200"},
    )
    assert result.exit_code == 0, result.output
    assert "Configure meter" in result.output
    assert "resonance law" in result.output
    e = generate_episode(
        7, axis_version=2, science_family="resonant-network-v1", discovery_level=0,
        theory_level=0, planning_level=0, resource_pressure=0,
    )
    save_episode(e, tmp_path)
    result = runner.invoke(
        app, ["play", str(tmp_path / "private.json")], input="help\n", env={"COLUMNS": "200"}
    )
    assert result.exit_code == 0, result.output
    assert "Configure meter" in result.output
    invalid = runner.invoke(app, ["actions", "--science-family", "unknown"])
    assert invalid.exit_code != 0
    invalid = runner.invoke(app, ["actions", "--science-family", "resonant-network-v1"])
    assert invalid.exit_code != 0
