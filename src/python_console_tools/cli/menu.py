import typer
from rich.console import Console

from python_console_tools.cli.auth import login as auth_login
from python_console_tools.cli.auth import logout as auth_logout
from python_console_tools.cli.auth import signup as auth_signup
from python_console_tools.cli.auth import status as auth_status

menu_app = typer.Typer(invoke_without_command=True, help="Menú interactivo de ejemplo")
console = Console()


@menu_app.callback(invoke_without_command=True)
def menu(ctx: typer.Context) -> None:
    """Muestra un menú simple y permite login/signup."""

    options = {
        "1": ("Login", auth_login),
        "2": ("Signup", auth_signup),
        "3": ("Status", auth_status),
        "4": ("Logout", auth_logout),
        "5": ("Create seam", None),
        "6": ("Download Copernicus data", None),
    }

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
