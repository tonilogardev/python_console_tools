from typer.testing import CliRunner

from python_console_tools.cli import app


runner = CliRunner()


def test_greet() -> None:
    result = runner.invoke(app, ["greet", "Codex"])
    assert result.exit_code == 0
    assert "Codex" in result.stdout
