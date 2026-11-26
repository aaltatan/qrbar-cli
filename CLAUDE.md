# qrbar-cli

Command line front end for the `qrbar` library
(`../../python-packages/qrbar`, `C:\Users\aaltt\dev\published\python-packages\qrbar`):
render barcode / QR sticker and label documents (`.docx`, `.zpl`, `.prn`, PDF) from
templates and Excel / JSON data, and make single code images.

Build order: [PHASES.md](PHASES.md). Status and decisions: [PROGRESS.md](PROGRESS.md).

## Principles

- **The CLI is a thin shell.** All domain logic (quantities, layout, symbologies,
  rendering, validation) lives in `qrbar`. The CLI only parses options, reads files,
  calls `qrbar.render` / `qrbar.render_code` / `qrbar.docx_to_pdf`, and writes files.
  If a feature needs new logic, add it to `qrbar` first (with its tests there).
- **Only public qrbar names.** Import from `qrbar` (`qrbar.__all__`), never from
  `qrbar.docx`, `qrbar.zpl`, ... Two exceptions: `qrbar.symbologies` (listing the code
  names) and `qrbar.records.parse_records` (`per_item` names files by the records qrbar
  kept, since qty 0 rows give no document).
- **Same stack and layout as templify** (`../templify`, the reference CLI). Read its
  `src/templify/cli/` before adding a pattern:
  - `typer` app built with `typer_di.TyperDI`, commands registered with
    `typer_swissknife.command(app, name=..., aliases=(...))`.
  - Shared options are typer-di dependencies in `cli/dependencies/<topic>.py`, exported
    as `XxxDI = Annotated[T, Depends(_get_xxx)]`.
  - `rich` console for output (`ConsoleDI`), `rich_help_panel` to group options.
  - Usage errors -> `typer.BadParameter`; runtime failures -> red message on stderr and
    `typer.Exit(1)` (templify's `_fail`).
  - Reject options the chosen mode does not use instead of ignoring them.
- **Reuse, don't copy.** Data input comes from `pyrecords` (readers for `.xlsx` /
  `.json`, `--order`, `--filter`, `--group-by` transformers and filter rules, shared with
  templify) and `schemify-cli` (`--schema`: ask for data interactively). Only write what neither has.
- **qrbar errors are user errors.** `qrbar.ValidationError` (bad data, qty, payload,
  options) -> clean message naming the record, exit 1. `qrbar.ConversionError`
  (LibreOffice missing / failing) -> clean message, exit 1. No tracebacks for either.

## Commands (target)

| Command | Alias | Does |
|---------|-------|------|
| `render` | `r` | Template + data -> one file (`paged`, `sheet`) or one file per record (`per_item`); optional `--pdf` for docx |
| `code` | `c` | One code image: `qrbar code qr "https://..." -o qr.png` (PNG / SVG) |
| `symbologies` | `s` | List the registered code names |

`render` options map 1:1 onto `qrbar.render` keywords:

| CLI | qrbar |
|-----|-------|
| `-t/--template` (`.docx`, `.zpl`, `.prn`) | `template` bytes; `kind` from the extension |
| `-d/--data` or `-s/--schema` | `data` |
| `--mode paged\|sheet\|per_item` | `mode` (default `paged`) |
| `--rows`, `--cols` | `sheet=SheetSpec(rows, cols)` |
| `--skip`, `--fill-last`, `--new-page-per-record` | `options=SheetOptions(...)` |
| `--collate grouped\|interleaved` | `collate` |
| `--qty-field` | `qty_field` (default `qty`) |
| `--max-copies` (`0` = no limit) | `max_copies` |
| `--font` (TTF/OTF path) | `font` bytes |

Output: `-o/--output` directory (default cwd), `-f/--filename` (default
`<template>-labels`); `per_item` names files by `--name-by` column or `<template>-<row>`,
`--numbered` prefix, like templify's `--each`. Existing files need `--force`, checked for
every target before the first write; the template itself is never overwritten. Names
from data go through `safe_name` (no path separators).

## Layout

```
src/qrbar_cli/
  __init__.py          # main()
  __main__.py          # python -m qrbar_cli
  cli/
    app.py             # TyperDI app + commands
    errors.py          # fail(), reported(): qrbar errors -> exit 1
    help.py            # long help texts
    dependencies/      # console, data, template, layout, job, output
examples/              # templates + data used by every README command
tests/
  fixtures/            # small templates + data (from qrbar's tests/fixtures)
  test_readme.py       # runs every `qrbar` line in README ```bash blocks
```

- `render` takes `job` before `data`: typer-di resolves in signature order, so option
  checks fail before `--schema` asks anything. Keep that order.
- No rich spinners / `console.status`: they crash legacy Windows consoles (cp1256).
- README and `docs/**/*.md` commands that need LibreOffice, a person (`--schema`) or a
  shell go in ```text blocks; everything in ```bash blocks must run against `examples/`
  (`tests/test_readme.py` runs them).
- Docs site: MkDocs Material (`mkdocs.yml`, `docs/`), deployed to GitHub Pages by
  `.github/workflows/docs.yml`. Preview: `uv run --group docs mkdocs serve`. A change to
  an option or message also updates `docs/reference/`.

## Tooling

- Python >= 3.12, `uv`, `src/` layout, entry point `qrbar = "qrbar_cli:main"`.
- `qrbar[arabic]` comes from PyPI. To try an unreleased qrbar change, temporarily add
  `[tool.uv.sources] qrbar = { path = "../../python-packages/qrbar", editable = true }`.
- `pytest` with `typer.testing.CliRunner`; tests assert on exit code, messages and the
  written files (open the docx, compare ZPL text). LibreOffice tests are skipped when
  `soffice` is missing, as in qrbar.
- `ruff` (`select = ["ALL"]`, line length 100) and `mypy --strict`, configured like
  `../syriantaxescli/pyproject.toml`.
- Code style: blank line after each statement group, before every `return`, and around
  every block (see the global CLAUDE.md).

```
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run mypy --strict src tests
```

## Out of scope (v1)

- Sending jobs to printers.
- `.lbl` / `.nlbl` templates (qrbar does not support them).
- Any rendering or validation logic not in qrbar.
