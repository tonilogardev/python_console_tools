import sys

from python_console_tools.cli.app import app
from python_console_tools.cli.menu import run_menu
from python_console_tools.services.auth_service import AuthService
from python_console_tools.settings import get_settings


def ensure_authenticated() -> None:
    service = AuthService(get_settings())
    if service.status() == "Not logged in":
        service.start_pkce_flow()


def main() -> None:
    # Si se ejecuta sin argumentos, forzamos login y luego mostramos menú.
    if len(sys.argv) == 1:
        ensure_authenticated()
        run_menu()
    else:
        app()


if __name__ == "__main__":
    main()
