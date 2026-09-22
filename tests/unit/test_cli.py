from typer.testing import CliRunner

from nexus.cli import app


runner = CliRunner()


def test_help_alias_and_actions_command():
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 0
    assert "generate" in result.stdout
    assert "qualify" in result.stdout
    assert "actions" in result.stdout

    actions = runner.invoke(app, ["actions"])
    assert actions.exit_code == 0
    assert "take" in actions.stdout
    assert "operate" in actions.stdout
    assert "probe" in actions.stdout
    assert "finish" in actions.stdout
