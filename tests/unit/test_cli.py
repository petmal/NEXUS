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
