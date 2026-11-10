# qrbar-cli progress

Phase details: [PHASES.md](PHASES.md). Tick items as you go; record decisions below so
later phases stay consistent.

| # | Phase | Status |
|---|-------|--------|
| 0 | Project setup | done |
| 1 | App skeleton + `symbologies` | done |
| 2 | `code` command | done |
| 3 | Data and template input | done |
| 4 | `render`: paged and per_item | done |
| 5 | `render`: sheet mode | done |
| 6 | PDF output | done (real LibreOffice run not tested locally) |
| 7 | Release | in progress |

Status values: `not started` / `in progress` / `done`.

## Phase 0 - Project setup

- [x] Metadata, license (GPL-3.0-or-later), description
- [x] Dependencies (`qrbar[arabic]` from PyPI, typer stack, pyrecords, schemify-cli)
- [x] Ruff + `mypy --strict` config
- [x] Entry point `qrbar`, `__main__.py`, `py.typed`
- [x] `tests/`, `tests/fixtures/`, smoke test
- [x] pytest, ruff, mypy pass

## Phase 1 - App skeleton + `symbologies`

- [x] `TyperDI` app, `--version` / `-V` (shows the qrbar version too)
- [x] `ConsoleDI`
- [x] `errors.py`: `fail()`, `reported()` (qrbar errors -> exit 1)
- [x] `symbologies` command with payload rules
- [x] Tests

## Phase 2 - `code` command

- [x] `code <symbology> <payload>` -> `render_code`
- [x] PNG / SVG, `--scale`, `--force`
- [x] Decode round-trip tests (incl. Arabic QR), error messages

## Phase 3 - Data and template input

- [x] `TemplateDI` (bytes + kind from extension)
- [x] `DataDI` (`--data`, `--schema`, `--order`, `--filter`)
- [x] `OutputDI` + overwrite policy
- [x] Tests

## Phase 4 - `render`: paged and per_item

- [x] `render` command, `--mode paged|per_item`
- [x] `--qty-field`, `--max-copies`, `--font`
- [x] per_item naming (`--name-by`, `--numbered`), safe names, duplicates refused
- [x] End-to-end tests docx + ZPL

## Phase 5 - `render`: sheet mode

- [x] `--rows`, `--cols`, `--skip`, `--fill-last`, `--new-page-per-record`, `--collate`
- [x] Rejected combinations
- [x] Tests

## Phase 6 - PDF output

- [x] `--pdf` via `docx_to_pdf`, `--soffice`
- [x] Missing LibreOffice message (names `--soffice`)
- [x] Tests (wiring with a fake converter; real test skips without LibreOffice)

## Phase 7 - Release

- [x] README with examples for every command; `tests/test_readme.py` runs each one
- [x] `examples/` folder (templates, xlsx/json data, schema)
- [x] CI (`.github/workflows/ci.yml`, as qrbar's; not run yet: no GitHub remote)
- [x] `uv build` checked
- [ ] Publish to PyPI (needs the author: a git remote, a first commit, a PyPI token)
- [x] Demo GIFs (`docs/demo/*.tape`, recorded with vhs): zpl, code, sheet, per-item, schema

## Decisions

| Phase | Question | Decision |
|-------|----------|----------|
| 0 | Script name | `qrbar` (the library ships no script, so no clash); PyPI name stays `qrbar-cli` |
| 0 | Data input: depend or copy? | Depend on `pyrecords` (templify's readers, order, filter and rules, split out; on PyPI): `readers`, `order_by_data`, `filter_data`, `get_compiler`. Replaced the first `templify-cli` dependency. `pyspecification` declared directly because its errors are caught |
| 0 | `qrbar[arabic]` | Installed by default: Arabic labels are a headline feature and the extra is small |
| 2 | `code` default output | `<symbology>.<format>` in the current folder; no stdout output |
| 2 | Bad payload exit code | 1 (bad data); bad option combinations are 2 (usage) |
| 2 | `--scale` with SVG | Rejected (SVG ignores it) |
| 3 | Overwrite policy | Refuse existing files unless `--force`; all targets checked before the first write. The template is never overwritten, even with `--force` |
| 3 | Default output name | `<template>-labels.<ext>`: the template's own name would overwrite it when run in its folder |
| 3 | Option checks before data | `render(job, data, ...)`: typer-di resolves in signature order, so `--schema` never prompts for a doomed run |
| 4 | per_item naming source | `qrbar.records.parse_records` gives the kept record indexes (qty 0 rows give no document) |
| 4 | Row numbers | File names and `--numbered` use 1-based rows (like templify); error messages keep qrbar's 0-based `Record N` |
| 4 | Unsafe names from data | `/ \ : * ? " < > |` and control characters -> `_`, leading/trailing dots stripped |
| 4 | `--max-copies 0` | No limit (`max_copies=None`) |
| 4 | Empty data / everything filtered / all qty 0 | Exit 1 with a message, nothing written |
| 5 | Sheet checks in the CLI | `--skip` >= sheet size and `--new-page-per-record` + interleaved rejected up front (qrbar would reject them only after reading data) |
| 6 | `--pdf` output | PDF instead of docx, never both |
| 6 | LibreOffice message | qrbar's `soffice='...'` wording rewritten to `--soffice '...'` |
| 7 | README image URLs | Absolute `raw.githubusercontent.com/aaltatan/qrbar-cli/main/...` (as templify) so they render on PyPI; they show only once pushed to `main` |
| 7 | Progress display | Plain lines, no rich spinner: it crashed with `UnicodeEncodeError` on a cp1256 legacy Windows console |

## Notes

- 2026-11-09: Plan written.
- 2026-11-10: Phases 0-6 built, phase 7 up to publishing. 88 tests pass, 1 skipped
  (real PDF: LibreOffice not installed on the dev machine). Not tested: a real
  LibreOffice conversion, the interactive `--schema` prompts (tests stub `ask_list`),
  printing on a real Zebra printer.
