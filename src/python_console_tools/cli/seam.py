import typer

from python_console_tools.services.seam_service import SeamService
from python_console_tools.settings import Settings, get_settings

app = typer.Typer(help="Operaciones seam")


def _service() -> SeamService:
    settings: Settings = get_settings()
    return SeamService(settings)


@app.command("create")
def create_seam(name: str = typer.Argument(..., help="Nombre del seam")) -> None:
    """Crea un seam."""

    _service().create(name=name)
    typer.echo(f"Seam '{name}' creado.")
