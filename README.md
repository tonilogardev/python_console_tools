# python_console_tools

Proyecto base para herramientas de consola en Python con tipado, logging estructurado y buenas prácticas listas para usar.

## Requisitos
- Python 3.11+
- `pip` y `venv` (o `uv`/`poetry` si prefieres)

## Instalación rápida (pip + venv)
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e .[dev]
pre-commit install
```

## Uso
```bash
python -m python_console_tools --help
```

## Tareas comunes
- Lint: `ruff check src tests`
- Formato: `ruff format src tests`
- Tipos: `mypy src`
- Tests: `pytest`
- Cobertura: `coverage run -m pytest` seguido de `coverage report`
- Seguridad: `bandit -r src` y `pip-audit`

## Configuración
- Variables de entorno en `.env` (ver `.env.example`).
- Logging configurable en `configs/logging.dev.yaml`.

## Estructura
```
.
├── pyproject.toml
├── src/python_console_tools
│   ├── __main__.py
│   ├── cli.py
│   ├── logging_setup.py
│   └── settings.py
├── tests/
└── configs/logging.dev.yaml
```

## Próximos pasos
- Ajusta `project.name` y autoría en `pyproject.toml`.
- Para publicar, ejecuta `git add . && git commit -m "chore: bootstrap" && git push -u origin main`.
