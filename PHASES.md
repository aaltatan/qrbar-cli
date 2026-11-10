# qrbar-cli build phases

Each phase ends in a working, tested, type-checked state. Do them in order; a phase only
depends on the ones before it. Track status in [PROGRESS.md](PROGRESS.md). Design rules
live in [CLAUDE.md](CLAUDE.md).

Every phase is done only when:

```
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run mypy --strict src tests
```

all pass.

---

## Phase 0 - Project setup

**Goal:** a CLI skeleton with the stack and tooling wired up.

- Real `description`, license (GPL-3.0-or-later), metadata in `pyproject.toml`.
- Dependencies: `qrbar[arabic]` (PyPI), `typer`, `typer-di`, `typer-swissknife`,
  `rich`, `templify-cli`, `schemify-cli`.
- Dev deps: `pytest`, `ruff`, `mypy`. Ruff and `mypy --strict` config like syriantaxescli.
- Entry point `qrbar = "qrbar_cli:main"`, `__main__.py`, `py.typed`.
- `tests/`, `tests/fixtures/`, a smoke test (`qrbar --help` exits 0).

**Decide:** script name (`qrbar` vs `qrbar-cli`); depend on `templify-cli` for data input
or copy the few functions (it pulls docxtpl/openpyxl/pyspecification, mostly already
needed).

**Done when:** the three commands above pass and `uv run qrbar --help` shows the app.

---

## Phase 1 - App skeleton + `symbologies`

**Goal:** the app structure every later command plugs into.

- `cli/app.py`: `TyperDI` app, `no_args_is_help`, `--version`.
- `cli/dependencies/console.py`: `ConsoleDI` (as in templify).
- Error helper: `qrbar.ValidationError` / `ConversionError` -> red stderr message, exit 1.
- `symbologies` (`s`): table of registered code names from `qrbar.symbologies`.

**Done when:** CliRunner tests cover `--help`, `--version`, `symbologies` output.

---

## Phase 2 - `code` command

**Goal:** one code image from the command line.

- `qrbar code <symbology> <payload> [-o file] [--format png|svg] [--scale N]`
  -> `qrbar.render_code`.
- Format from `--format` or the `-o` extension; unknown symbology lists valid names.
- No `-o`: write to `<symbology>.<format>` in cwd (or stdout for SVG? decide).

**Decide:** default output target; whether bad payloads exit 1 or 2.

**Done when:** tests decode the written PNG (zxing-cpp, already a qrbar dep), check SVG,
and cover bad symbology / payload messages.

---

## Phase 3 - Data and template input

**Goal:** the shared `render` inputs as typer-di dependencies.

- `TemplateDI`: `-t/--template`, read as bytes; kind from extension
  (`.docx` -> docx, `.zpl` / `.prn` -> zpl), other extensions rejected.
- `DataDI`: `-d/--data` (`.xlsx`, `.json` via templify readers) or `-s/--schema`
  (schemify `ask_list`); `--order`, `--filter` (reuse templify's pipeline functions).
- `OutputDI`: `-o/--output` dir, `-f/--filename`, overwrite policy.

**Decide:** reuse templify's `DataDI` directly (it brings `--each` / `--object` /
`--group-by`, which qrbar does not need) or compose from its readers + transformers;
overwrite policy (refuse, `--force`, or overwrite).

**Done when:** dependency tests cover each source, bad extensions, unreadable files.

---

## Phase 4 - `render`: paged and per_item

**Goal:** the main command for docx and ZPL in the two modes every template supports.

- `render` (`r`) with `--mode paged|per_item`, `--qty-field`, `--max-copies`, `--font`.
- `paged`: one file `<filename>.<docx|zpl|prn>` (keep the template's extension).
- `per_item`: one file per record, named by `--name-by` column or index, `--numbered`.
- Progress / summary line with rich, as templify.

**Done when:** end-to-end tests with fixture templates: docx paged / per_item, ZPL paged
(exact text) / per_item, qty error message names the record, `--max-copies` limit,
Arabic `text()` with and without `--font`.

---

## Phase 5 - `render`: sheet mode

**Goal:** label sheets (docx only).

- `--mode sheet` with `--rows`, `--cols`, `--skip`, `--fill-last`,
  `--new-page-per-record`, `--collate`.
- Reject sheet options outside `sheet`, `sheet` with ZPL, missing `--rows/--cols`
  (as `BadParameter`, before reading data).

**Done when:** tests cover an A4 3x8 sheet (cell count in `document.xml`), each option,
and each rejected combination.

---

## Phase 6 - PDF output

**Goal:** `render --pdf` converts docx output with `qrbar.docx_to_pdf`.

- `--pdf` writes `.pdf` instead of (or beside? decide) the `.docx`; works for all modes.
- `--pdf` with ZPL rejected. Missing LibreOffice -> clean message, exit 1.

**Done when:** tests (skipped without LibreOffice) check the PDF page count; the missing
LibreOffice path is tested with a fake `soffice`.

---

## Phase 7 - Release

- README: install, every command with examples, sample templates; demo GIFs like
  templify (`docs/demo/`).
- CI (GitHub Actions): ruff, mypy, tests on 3.12+ (Ubuntu + Windows).
- `uv build`, publish.
