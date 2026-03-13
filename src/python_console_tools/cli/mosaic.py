import typer

from python_console_tools.services.mosaic_service import MosaicService
from python_console_tools.settings import Settings, get_settings

app = typer.Typer(help="Mosaicos")


def _service() -> MosaicService:
    settings: Settings = get_settings()
    return MosaicService(settings)


@app.command("create-catalonia")
def create_catalonia() -> None:
    """Crea mosaico de Cataluña a partir de datos descargados."""

    _service().create_catalonia()
    typer.echo("Mosaico de Cataluña creado.")
