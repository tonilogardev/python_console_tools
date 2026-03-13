import pathlib
from typing import Optional

import rich
import typer

from python_console_tools.logging_setup import configure_logging
from python_console_tools.settings import Settings, get_settings

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


def _default_log_config() -> pathlib.Path:
    return pathlib.Path("configs") / "logging.dev.yaml"


@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[pathlib.Path] = typer.Option(
        None,
        "--config",
        "-c",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Ruta a archivo .env con configuraciones",
    ),
    log_config: pathlib.Path = typer.Option(
        _default_log_config,
        "--log-config",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Archivo YAML de logging (por defecto configs/logging.dev.yaml)",
    ),
) -> None:
    \"\"\"CLI App: punto de entrada y configuración global.\"\"\"

    configure_logging(log_config)
    settings = get_settings(env_file=config)
    ctx.obj = settings


@app.command()
def greet(name: str, excited: bool = typer.Option(False, "--excited", "-e")) -> None:
    \"\"\"Saluda con estilo.\"\"\"

    punctuation = "!" if excited else "."
    rich.print(f\"[bold green]Hola[/] {name}{punctuation}\")


@app.command()
def show_settings(ctx: typer.Context) -> None:
    \"\"\"Imprime las configuraciones cargadas.\"\"\"

    settings: Settings = ctx.obj
    rich.print_json(settings.model_dump_json())
