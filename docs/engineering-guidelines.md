# Engineering Guidelines (python_console_tools)

## Branching
- `main`: estable, sólo merges vía PR.
- `codex/main_dev_pro`: rama de integración continua (features largas).
- `codex/main_dev_pro_interface`: trabajo actual de interfaz/CLI; hacer PR hacia `codex/main_dev_pro` y luego a `main`.
- Convención para nuevas ramas: `codex/<area>-<breve>` (ej. `codex/feat-auth`, `codex/chore-ci`).

## Commits y PR
- Formato commit: `type: mensaje` (conventional commits: feat, fix, chore, docs, refactor, test).
- PR checklist:
  - `make lint format type test` pasa.
  - Sin secretos (API keys, tokens) ni `.env`.
  - Cobertura mantenida (objetivo ≥85%).
  - Descripción clara: qué cambia, por qué, riesgos.

## Estilo Python
- Typing obligatorio: funciones nuevas con anotaciones; `mypy` debe pasar.
- Lint/format: `ruff format` + `ruff check` (usa reglas en `pyproject.toml`).
- Evitar `print`; usar logging.
- Manejo de errores: `try/except` con mensajes útiles y logging, no silenciar excepciones sin razón.
- IO/paths: usar `pathlib`; parametrizar rutas.
- CLI: subcomandos con Typer; validaciones de entrada y mensajes de ayuda.

## Logging
- Config vía `configs/logging.dev.yaml`; no hardcodear niveles.
- Usa logger por módulo: `logger = logging.getLogger(__name__)`.
- Mensajes estructurados y accionables; incluye contexto (ids, recurso) pero nunca secretos.

## Configuración y secretos
- Valores en `.env` (ver `.env.example`); no commitear `.env`.
- No guardar credenciales en código ni en logs.
- Preferir variables de entorno para endpoints, tokens, rutas sensibles.

## Dependencias
- Añadir deps en `pyproject.toml`; `pip install -e .[dev]` mantiene editable.
- Para nuevas libs, justificar en PR (seguridad/superficie de ataque mínima).
- Ejecutar `pip-audit` si se añaden deps sensibles.

## Tests
- Framework: `pytest` (+ `coverage`).
- Nuevas funciones públicas: añadir tests.
- Usa fixtures en lugar de mocks ad-hoc cuando aplique.
- Objetivo: cobertura ≥85% global; evita pruebas frágiles (dependencias de tiempo/red).

## Seguridad
- Ejecutar `bandit -r src` para cambios con IO, subprocess o crypto.
- Validar entradas de usuario/CLI; no eval/exec de entrada.
- No escribir archivos fuera de rutas permitidas; crear directorios con permisos mínimos.

## Release / CI
- Workflow GH Actions: matrix 3.11/3.12; pasos `ruff format --check`, `ruff check`, `mypy`, `pytest` con coverage fail-under=85; cache de pip; `bandit`.
- Protecciones de rama recomendadas: requerir PR + checks verdes para `main` y `codex/main_dev_pro`.

## Definition of Done (por cambio)
- Código y tests actualizados.
- Lint/format/type/tests/coverage ejecutados o justificados (fail-under=85).
- Docs actualizadas (README o sección relevante).
- PR abierto con contexto y checklist marcada.
