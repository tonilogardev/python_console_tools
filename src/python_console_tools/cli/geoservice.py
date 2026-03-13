import typer

from python_console_tools.services.geoservice import GeoService
from python_console_tools.settings import Settings, get_settings

app = typer.Typer(help="Geoservicio")


def _service() -> GeoService:
    settings: Settings = get_settings()
    return GeoService(settings)


@app.command("add-month")
def add_month(month: str = typer.Argument(..., help="Mes en formato YYYY-MM")) -> None:
    """Añade un mes al geoservicio."""

    _service().add_month(month=month)
    typer.echo(f"Mes {month} añadido al geoservicio.")
