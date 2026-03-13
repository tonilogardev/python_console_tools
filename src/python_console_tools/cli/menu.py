import typer
from rich.console import Console

menu_app = typer.Typer(invoke_without_command=True, help="Menú interactivo de ejemplo")
console = Console()


@menu_app.callback(invoke_without_command=True)
def menu(ctx: typer.Context) -> None:
    """Muestra un menú simple y felicita la elección."""

    options = {
        "1": "Login",
        "2": "Signup",
        "3": "Create seam",
        "4": "Download Copernicus data",
    }

    # Si hubiera subcomandos, no ejecutar el menú principal.
    if ctx.invoked_subcommand:
        return

    console.print("[cyan]Select option:[/]")
    for key, label in options.items():
        console.print(f"[bold white]{key}[/]: {label}")

    choice = typer.prompt("Your choice")
    if choice in options:
        console.print(f"[bold green]✓[/] Has elegido: [yellow]{options[choice]}[/]")
    else:
        console.print("[bold red]✗[/] Opción no válida", style="bold red")
