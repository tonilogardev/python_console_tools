# python_console_tools

## Index

1. [Business Policy](#1-business-policy)
2. [Run Flow](#2-run-flow)
3. [Auth & Config](#3-auth--config)
4. [Geo Tools](#4-geo-tools)
5. [Next steps](#5-next-steps)

---

## 1 Business Policy

- ***Instruction***: Ship value fast; avoid over‑engineering. Less code, more results.
- ***Instruction***: Defaults first. Only ask user for data you cannot infer.
- ***Instruction***: Log clearly; never log secrets. Fail loud, fail early.

[←Index](#index)

## 2 Run Flow

- ***Instruction***: `python -m python_console_tools` abre login Auth0 y muestra menú (type `exit` para salir).
- ***Instruction***: Menú opciones: 1 Search north south seam; 2 Search clouds seam; 3 Create Mosaic; 9 Status; 0 Logout.
- ***File References***:
  - Menú [src/python_console_tools/cli/menu.py](./src/python_console_tools/cli/menu.py)
  - Auth login [src/python_console_tools/cli/auth.py](./src/python_console_tools/cli/auth.py)

[←Index](#index)

## 3 Auth & Config

- ***Instruction***: Completa [.env](./.env.example) con `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_AUDIENCE`.
- ***Instruction***: Callback permitido en Auth0: `http://127.0.0.1:8765/callback`.
- ***Instruction***: Logs/config en [configs/logging.dev.yaml](./configs/logging.dev.yaml).

[←Index](#index)

## 4 Geo Tools

- ***Instruction***: Instala deps geo en conda: `mamba create -n pctools-gis python=3.11 gdal proj pytorch torchvision torchgeo rasterio geopandas numba -c conda-forge -y` y luego `pip install -e .[dev,geo]`.
- ***Instruction***: Seam N-S: `python -m python_console_tools seam search-north-south --img-east <R008> --img-west <R051> --mask <mask> --out <dir>`.
- ***File References***:
  - Dijkstra pipeline [src/python_console_tools/seam/dijkstra.py](./src/python_console_tools/seam/dijkstra.py)
  - CLI comando seam [src/python_console_tools/cli/seam.py](./src/python_console_tools/cli/seam.py)
  - Handler GeoTIFF [src/python_console_tools/geo/handler.py](./src/python_console_tools/geo/handler.py)

[←Index](#index)

## 5 Next steps

- Añadir opción “Search clouds seam” y “Create Mosaic” apuntando a pipelines reales.
- Registrar ADRs en `docs/` siguiendo el skill principal-architect.

[←Index](#index)
