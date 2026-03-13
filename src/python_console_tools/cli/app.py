import typer

from python_console_tools.cli import auth, data, geoservice, mosaic, seam
from python_console_tools.cli.menu import menu  # registers menu command

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

app.add_typer(auth.app, name="auth", help="Autenticación: login, signup")
app.add_typer(seam.app, name="seam", help="Operaciones de seam")
app.add_typer(data.app, name="data", help="Descarga de datos Copernicus")
app.add_typer(mosaic.app, name="mosaic", help="Generar mosaicos (ej. Cataluña)")
app.add_typer(geoservice.app, name="geoservice", help="Operaciones sobre geoservicio")


@app.callback()
def main() -> None:
    """python_console_tools CLI."""
