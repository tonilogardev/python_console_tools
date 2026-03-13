---
name: console-ux-style
description: >
  Consistent, legible terminal UX for python_console_tools: Rich/typer styling,
  colors/icons, messages, spinners, tables, error/success patterns, and logging
  vs stdout guidance. Use whenever adding or editing CLI output.
---

# Console UX Style

## Principles
- Prioriza legibilidad y brevedad; no inundar con texto.
- Usa `rich` para color/format; no ANSI manual.
- Separa stdout (mensajes al usuario) de logging (diagnóstico).
- Salidas deterministas: mismo formato para éxito/errores.

## Pattern de salida
- Success: `console.print("[bold green]✓[/] Mensaje")`
- Info: `console.print("[cyan]-[/] Mensaje")`
- Warning: `console.print("[yellow]![/] Mensaje")`
- Error (human): `console.print("[bold red]✗[/] Mensaje")`
- Error (detalle técnico) al logger, no al usuario; si procede, ofrecer `--verbose` para stack.

## Componentes Rich
- `Console` único por módulo: `console = Console()` (pasar a funciones para test).
- Tablas: `Table(show_header=True, header_style="bold magenta")`; columnas con `style`.
- Progreso/spinners: `with console.status("Descargando..."):`; mensajes breves.
- Paneles para resúmenes: `Panel.fit(texto, title="...", border_style="blue")`.

## Typer
- Usa opciones con `--help` claro; valida argumentos.
- Evita `print`; siempre `console.print`.
- Para prompts, `typer.prompt` con `hide_input` solo en credenciales; confirmar acciones destructivas con `typer.confirm`.
- Propaga un `--verbose / -v` global si se necesita detalle: aumenta nivel de logging y muestra trazas opcionales.

## Colores/Estilos
- Verde = éxito, Cian = info, Amarillo = warning, Rojo = error.
- No abusar de fondos; preferir estilo minimal.
- Emojis/símbolos: ✓ ✗ ! - (consistentes con patrón arriba).

## Errores
- Captura excepciones en CLI, muestra mensaje corto al usuario y registra detalle en logger.
- Devuelve códigos de salida adecuados (`typer.Exit(code=1)` en errores).

## Ejemplos breves
- Lista de items:
  ```python
  table = Table(show_header=True, header_style="bold magenta")
  table.add_column("ID", style="white")
  table.add_column("Estado", style="green")
  for item in items:
      table.add_row(item.id, item.state)
  console.print(table)
  ```
- Spinner:
  ```python
  with console.status("Procesando..."):
      do_work()
  console.print("[bold green]✓[/] Listo")
  ```

## Logging vs consola
- Logging estructurado ya configurado; usa `logger = logging.getLogger(__name__)`.
- No mezclar logs con UX Rich; logs van a handlers, mensajes de usuario al `Console`.

## Tests
- Inyecta `Console(record=True)` en tests para aserciones de salida.
