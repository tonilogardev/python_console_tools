import pathlib
import typer

from python_console_tools.services.auth_service import AuthService
from python_console_tools.settings import Settings, get_settings

app = typer.Typer(help="Autenticación")


def _service() -> AuthService:
    settings: Settings = get_settings()
    return AuthService(settings)


@app.command()
def login(username: str = typer.Argument(...), password: str = typer.Option(..., prompt=True, hide_input=True)) -> None:
    """Inicia sesión y guarda token local."""

    token = _service().login(username=username, password=password)
    typer.echo("Login OK, token guardado.")


@app.command()
def signup(username: str = typer.Argument(...), password: str = typer.Option(..., prompt=True, hide_input=True)) -> None:
    """Crea usuario y guarda token."""

    token = _service().signup(username=username, password=password)
    typer.echo("Signup OK, token guardado.")


@app.command()
def status() -> None:
    """Muestra estado de autenticación."""

    state = _service().status()
    typer.echo(state)
