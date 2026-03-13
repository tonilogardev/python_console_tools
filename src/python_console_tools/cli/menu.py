import typer
from rich.console import Console

from python_console_tools.cli.auth import logout as auth_logout
from python_console_tools.cli.auth import status as auth_status

menu_app = typer.Typer(invoke_without_command=True, help="Menú interactivo")
console = Console()


@menu_app.callback(invoke_without_command=True)
def menu(ctx: typer.Context) -> None:
    """Muestra menú principal."""

    options: dict[str, tuple[str, callable | None]] = {
        "1": ("Search north south seam", _menu_search_north_south),
        "2": ("Search clouds seam", None),
        "3": ("Create Mosaic", None),
        "9": ("Status", auth_status),
        "0": ("Logout", auth_logout),
    }

    # Si hubiera subcomandos, no ejecutar el menú principal.
    if ctx.invoked_subcommand:
        return

    console.print("[bold red]Type exit to leave the app[/]")
    console.print("[cyan]Select app:[/]")
    for key, (label, _) in options.items():
        console.print(f"[bold white]{key}[/]: {label}")

    choice = typer.prompt("Your choice")
    if choice.lower() == "exit":
        raise typer.Exit()

    if choice in options:
        label, action = options[choice]
        console.print(f"[bold green]✓[/] Has elegido: [yellow]{label}[/]")
        if action:
            action()
    else:
        console.print("[bold red]✗[/] Opción no válida", style="bold red")


def run_menu() -> None:
    """Invoca el menú interactivo directamente (uso desde __main__)."""

    ctx = typer.Context(menu_app)
    menu(ctx)


def _menu_search_north_south() -> None:
    from python_console_tools.services.seam_service import SeamService
    from python_console_tools.settings import get_settings

    img_east = typer.prompt("Ruta imagen ESTE (R008)")
    img_west = typer.prompt("Ruta imagen OESTE (R051)")
    mask = typer.prompt("Ruta máscara solape (.shp/.gpkg/.msk)")
    out_dir = typer.prompt("Directorio de salida")
    buffer_pixels = typer.prompt("Buffer en píxeles", default="15")
    block_size = typer.prompt("Tamaño de bloque", default="4096")

    service = SeamService(get_settings())
    try:
        ok, mosaic = service.search_north_south_seam(
            img_east=img_east,
            img_west=img_west,
            mask=mask,
            out_dir=out_dir,
            buffer_pixels=int(buffer_pixels),
            block_size=int(block_size),
        )
    except Exception as exc:
        console.print(f"[bold red]✗[/] {exc}")
        return

    if ok:
        console.print(f"[bold green]✓[/] Mosaico generado: {mosaic}")
    else:
        console.print("[bold red]✗[/] Proceso terminado sin mosaico")
