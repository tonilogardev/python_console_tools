from typer.testing import CliRunner

from python_console_tools.cli.app import app


runner = CliRunner()


def test_auth_commands_exist() -> None:
    result = runner.invoke(app, ["auth", "--help"])
    assert result.exit_code == 0
    assert "login" in result.stdout
    assert "signup" in result.stdout
