---
name: python-console-guidelines
description: >
  Project-wide standards for python_console_tools. Use whenever coding,
  reviewing, or configuring CI/branches here: branching model, commit/PR rules,
  lint/format/type/test/coverage thresholds, logging/config/security practices.
---

# Guidelines

## Lema
- MENOS ES MAS: simplicidad, claridad y sólo lo necesario para aportar valor.

## Branching
- `main`: estable; merges vía PR.
- `codex/main_dev_pro`: integración continua.
- `codex/main_dev_pro_interface`: interfaz/CLI actual.
- Nuevas ramas: `codex/<area>-<breve>` (ej. `codex/feat-auth`).

## Commits y PR
- Commits estilo conventional (`feat|fix|chore|docs|refactor|test: mensaje`).
- PR: explicar qué/por qué/riesgos; checklist de checks ejecutados.
- Merge por PR; preferir squash si hay commits pequeños.

## Checks obligatorios
- `ruff format --check src tests`
- `ruff check src tests`
- `mypy src`
- `coverage run -m pytest` + `coverage report --fail-under=85`
- `bandit -r src`
- Objetivo cobertura global >=85%.

## Estilo Python
- Typing obligatorio; evita `Any`.
- Usa `pathlib`, no `os.path` plano.
- Logging en vez de `print`; config desde `configs/logging.dev.yaml`.
- Validar entradas de CLI (Typer) y exponer `--help` claro.
- No hardcodear secretos/endpoints; usar variables de entorno y `.env.example`.

## Config/Seguridad
- `.env` no se commitea; plantilla en `.env.example`.
- No loggear secretos; cuidado con trazas.
- Revisar deps nuevas; usa `pip-audit` si añades librerías sensibles.

## Tests
- Framework: `pytest`; añade tests para funciones públicas nuevas o cambiadas.
- Evita dependencias de red/tiempo real; usa fixtures.

## Definition of Done
- Lint/format/type/tests/coverage ejecutados o justificados.
- Docs actualizadas (README/CONTRIBUTING/guidelines).
- PR abierta con contexto y checklist marcada.
