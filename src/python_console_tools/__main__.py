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
    args = sys.argv[1:]

    def is_auth_passthrough() -> bool:
        return len(args) >= 2 and args[0] == "auth" and args[1] in {"login", "logout", "signup"}

    if not args:
        ensure_authenticated()
        run_menu()
        return

    if not is_auth_passthrough():
        ensure_authenticated()
    app()


if __name__ == "__main__":
    main()
