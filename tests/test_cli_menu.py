from typer.testing import CliRunner

from python_console_tools.cli.app import app


runner = CliRunner()


def test_menu_runs() -> None:
    result = runner.invoke(app, ["menu"], input="1\n")
    assert result.exit_code == 0
    assert "Has elegido" in result.stdout
