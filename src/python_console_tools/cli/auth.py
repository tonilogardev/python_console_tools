import typer
from rich.console import Console

from python_console_tools.services.auth_service import AuthError, AuthService
from python_console_tools.settings import Settings, get_settings

app = typer.Typer(help="Autenticación")
console = Console()


def _service() -> AuthService:
    settings: Settings = get_settings()
    return AuthService(settings)


@app.command()
def signup(
    email: str = typer.Argument(..., help="Email de usuario"),
    password: str = typer.Option(..., "--password", "-p", prompt=True, hide_input=True, confirmation_prompt=True),
) -> None:
    """Registra un usuario en Auth0 (DB Connection) sin guardar contraseña."""

    try:
        _service().signup(email=email, password=password)
    except AuthError as exc:
        console.print(f"[bold red]✗[/] {exc}")
        raise typer.Exit(code=1)
    console.print("[bold green]✓[/] Usuario creado. Ejecuta 'auth login' para iniciar sesión.")


@app.command()
def login() -> None:
    """Login via Auth0 Device Flow y guarda tokens en almacén seguro."""

    service = _service()
    try:
        flow = service.start_device_flow()
    except AuthError as exc:
        console.print(f"[bold red]✗[/] {exc}")
        raise typer.Exit(code=1)

    console.print("[cyan]Abre en tu navegador y completa el login:[/]")
    if flow.get("verification_uri_complete"):
        console.print(f"[bold yellow]{flow['verification_uri_complete']}[/]")
    else:
        console.print(f"URL: {flow['verification_uri']}, code: [bold]{flow['user_code']}[/]")

    console.print("[cyan]Esperando autorización...[/]")
    try:
        service.poll_device_flow(flow["device_code"], flow.get("interval", 5))
    except AuthError as exc:
        console.print(f"[bold red]✗[/] {exc}")
        raise typer.Exit(code=1)
    console.print("[bold green]✓[/] Login correcto, tokens guardados.")


@app.command()
def status() -> None:
    """Muestra estado de autenticación."""

    console.print(_service().status())


@app.command()
def refresh() -> None:
    """Refresca el access token usando el refresh token."""

    try:
        _service().refresh()
    except AuthError as exc:
        console.print(f"[bold red]✗[/] {exc}")
        raise typer.Exit(code=1)
    console.print("[bold green]✓[/] Token refrescado.")


@app.command()
def logout() -> None:
    """Elimina tokens locales."""

    _service().logout()
    console.print("[bold green]✓[/] Sesión cerrada; tokens eliminados.")
