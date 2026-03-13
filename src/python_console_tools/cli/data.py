import typer

from python_console_tools.services.data_service import DataService
from python_console_tools.settings import Settings, get_settings

app = typer.Typer(help="Datos Copernicus")


def _service() -> DataService:
    settings: Settings = get_settings()
    return DataService(settings)


@app.command("download-copernicus")
def download_copernicus(
    region: str = typer.Argument(..., help="Región (ej. bbox id)"),
    from_date: str = typer.Option(..., "--from-date", help="YYYY-MM-DD"),
    to_date: str = typer.Option(..., "--to-date", help="YYYY-MM-DD"),
    product: str = typer.Option(..., "--product", help="Producto Copernicus"),
) -> None:
    """Descarga datos de Copernicus para una región y rango de fechas."""

    _service().download_copernicus(region=region, from_date=from_date, to_date=to_date, product=product)
    typer.echo("Descarga solicitada.")
