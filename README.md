# python_console_tools

CLI modular en Python con Typer, Rich y buenas prácticas listas para usar.

## Requisitos
- Python 3.11+
- `pip` y `venv` (o `uv`/`poetry` si prefieres)

## Instalación rápida (pip + venv)
```bash
python -m venv .venv
. .venv/Scripts/activate  # PowerShell: .venv\Scripts\Activate.ps1
pip install -e .[dev]
pre-commit install
```

## Uso
```bash
python -m python_console_tools --help
python -m python_console_tools menu
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
- Auth0 (Device Flow): `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_AUDIENCE`.
- Logging configurable en `configs/logging.dev.yaml`.

## Estructura
```
.
├── pyproject.toml
├── src/python_console_tools
│   ├── __main__.py
│   ├── cli/        # comandos Typer
│   ├── services/   # lógica de negocio
│   ├── core/       # modelos/DTOs
│   ├── adapters/   # integraciones (token store, http, etc.)
│   └── settings.py
├── tests/
└── configs/logging.dev.yaml
```

## Próximos pasos
- Ajusta `project.name` y autoría en `pyproject.toml`.
- Consulta estándares en [CONTRIBUTING.md](CONTRIBUTING.md) y [docs/engineering-guidelines.md](docs/engineering-guidelines.md).
- CI: ver `.github/workflows/ci.yml` (ruff, mypy, pytest+coverage>=85, bandit).
