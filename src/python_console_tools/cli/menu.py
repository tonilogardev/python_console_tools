import typer
from rich.console import Console

from python_console_tools.cli.auth import login as auth_login
from python_console_tools.cli.auth import logout as auth_logout
from python_console_tools.cli.auth import status as auth_status
from python_console_tools.services.auth_service import AuthService
from python_console_tools.settings import get_settings

menu_app = typer.Typer(invoke_without_command=True, help="Menú interactivo")
console = Console()


@menu_app.callback(invoke_without_command=True)
def menu(ctx: typer.Context) -> None:
    """Muestra menú principal."""

    service = AuthService(get_settings())
    status_text = service.status()
    logged_in = status_text != "Not logged in"

    options: dict[str, tuple[str, callable | None]] = {}
    if not logged_in:
        options["1"] = ("Login / Signup (Auth0)", auth_login)
    else:
        options["1"] = (f"Status ({status_text})", auth_status)
        options["2"] = ("Logout", auth_logout)
        options["3"] = ("Create seam", None)
        options["4"] = ("Download Copernicus data", None)

    # Si hubiera subcomandos, no ejecutar el menú principal.
    if ctx.invoked_subcommand:
        return

    console.print("[cyan]Select option:[/]")
    for key, (label, _) in options.items():
        console.print(f"[bold white]{key}[/]: {label}")

    choice = typer.prompt("Your choice")
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
