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


@app.command("search-north-south")
def search_north_south(
    img_east: str = typer.Option(..., "--img-east", "-e", help="Ruta imagen ESTE (R008)"),
    img_west: str = typer.Option(..., "--img-west", "-w", help="Ruta imagen OESTE (R051)"),
    mask: str = typer.Option(..., "--mask", "-m", help="Ruta máscara solape (.shp/.gpkg/.msk)"),
    out_dir: str = typer.Option(..., "--out", "-o", help="Directorio salida"),
    buffer_pixels: int = typer.Option(15, help="Buffer en píxeles para el corredor"),
    block_size: int = typer.Option(4096, help="Tamaño de bloque para procesado"),
) -> None:
    """Ejecuta la búsqueda de costura Norte-Sur con Dijkstra guiado."""

    try:
        ok, mosaic_path = _service().search_north_south_seam(
            img_east=img_east,
            img_west=img_west,
            mask=mask,
            out_dir=out_dir,
            buffer_pixels=buffer_pixels,
            block_size=block_size,
        )
    except Exception as exc:
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(code=1)

    if ok:
        typer.echo(f"[OK] Mosaico generado en {mosaic_path}")
    else:
        typer.echo("[ERROR] Proceso terminado sin generar mosaico")
