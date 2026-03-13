import typer
from rich.console import Console

geo_app = typer.Typer(help="Geospatial ML utilities")
console = Console()


@geo_app.command("validate-pipeline")
def validate_pipeline() -> None:
    """E2E smoke test: rasterio + torch + handler windowed IO."""

    try:
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
        import torch
        from python_console_tools.geo.handler import SatelliteImageHandler
    except ImportError as exc:  # pragma: no cover - optional deps
        console.print(f"[bold red]Necesitas instalar las deps geo[/] ({exc}). Usa conda y `pip install -e .[geo]`.")
        raise typer.Exit(code=1)

    input_path = "data/dummy_input.tif"
    output_path = "data/dummy_output.tif"

    console.print("[cyan]1. Generando GeoTIFF sintético (EPSG:4326)...[/]")
    transform = from_origin(-10, 40, 0.1, 0.1)
    synthetic_data = np.random.rand(1, 256, 256).astype(np.float32)

    with rasterio.open(
        input_path,
        "w",
        driver="GTiff",
        height=256,
        width=256,
        count=1,
        dtype=str(synthetic_data.dtype),
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(synthetic_data)

    console.print("[cyan]2. Leyendo ventana 128x128...[/]")
    handler = SatelliteImageHandler(input_path)
    tensor, profile, window, window_transform = handler.get_patch(row_off=64, col_off=64, width=128, height=128)

    console.print(f"[cyan]3. Inference dummy con torch (shape {tensor.shape})...[/]")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    console.print(f"[yellow]Usando dispositivo: {device}[/]")
    tensor = tensor.to(device)
    inferred = torch.nn.functional.relu(tensor)  # placeholder

    console.print("[cyan]4. Escribiendo resultado...[/]")
    handler.write_patch(output_path, inferred.cpu(), profile, window=window, window_transform=window_transform)

    console.print(f"[bold green]✓[/] Pipeline OK. Salida: {output_path}")
