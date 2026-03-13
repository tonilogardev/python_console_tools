import typer
from rich.console import Console

from python_console_tools.cli.app import app  # to reuse typer context

console = Console()


@app.command("menu")
def menu() -> None:
    """Menú interactivo de ejemplo."""

    options = {
        "1": "Login",
        "2": "Signup",
        "3": "Create seam",
        "4": "Download Copernicus data",
    }
    console.print("[cyan]Select option:[/]")
    for key, label in options.items():
        console.print(f"[bold white]{key}[/]: {label}")

    choice = typer.prompt("Your choice")
    if choice in options:
        console.print(f"[bold green]✓[/] Has elegido: [yellow]{options[choice]}[/]")
    else:
        console.print("[bold red]✗[/] Opción no válida", style="bold red")
