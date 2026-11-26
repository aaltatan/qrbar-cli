# Development

```text
git clone https://github.com/aaltatan/qrbar-cli
cd qrbar-cli
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run mypy --strict src tests
```

qrbar-cli is a thin shell around the [qrbar](https://github.com/aaltatan/qrbar)
library: rendering, layout, code types and validation live there. A feature that needs
new logic goes into qrbar first.

## Documentation

This site is built with [MkDocs](https://www.mkdocs.org) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). The pages are in
`docs/`, and the navigation in `mkdocs.yml`.

```text
uv run --group docs mkdocs serve          # live preview on http://127.0.0.1:8000
uv run --group docs mkdocs build --strict # what CI runs: broken links fail the build
```

Every push to `main` builds the site and publishes it to GitHub Pages
(`.github/workflows/docs.yml`).

### Commands in the docs are tested

The test suite runs every `qrbar` command in the ` ```bash ` blocks of `README.md` and
`docs/**/*.md` against a copy of `examples/`. So:

- commands in ` ```bash ` blocks must work from inside `examples/`;
- commands that need LibreOffice, a person (`--schema`), a printer, or another shell
  go in ` ```text ` or ` ```powershell ` blocks, which are not run.

### Demo GIFs

The GIFs in `docs/demo/` are recorded with [vhs](https://github.com/charmbracelet/vhs)
from the repository root (PowerShell 7). Each tape runs this checkout in a scratch copy
of `examples/`:

```text
vhs docs/demo/zpl.tape
```

## Releasing

Push a `v*` tag. The release workflow builds the package, publishes it to PyPI with
trusted publishing, and creates a GitHub release.

## License

GPL-3.0-or-later, like [qrbar](https://github.com/aaltatan/qrbar). The bundled IBM Plex
Sans Arabic font is under the SIL Open Font License 1.1.
