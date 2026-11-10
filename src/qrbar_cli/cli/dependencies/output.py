"""Where results are written: `--output`, and `--force` to replace existing files."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from typer_di import Depends

from qrbar_cli.cli.errors import fail

# characters Windows forbids in file names, plus control characters
_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_name(name: str) -> str:
    """Make `name` (often a data value) a single, valid file name without a path."""
    cleaned = _UNSAFE.sub("_", name).strip().strip(".")

    return cleaned or "_"


@dataclass(frozen=True)
class Output:
    """The output directory, and whether existing files may be replaced."""

    directory: Path
    force: bool

    def write(self, files: dict[str, bytes]) -> list[Path]:
        """Write `files` (name -> content) into the directory, all or nothing.

        Every target is checked before the first write, so a refused overwrite
        leaves no half-written batch behind.
        """
        paths = {self.directory / name: content for name, content in files.items()}

        if not self.force:
            existing = [path.name for path in paths if path.exists()]

            if existing:
                shown = ", ".join(existing[:5]) + (", ..." if len(existing) > 5 else "")  # noqa: PLR2004

                fail(f"Error: {len(existing)} file(s) exist: {shown}. Use --force to replace.")

        self.directory.mkdir(parents=True, exist_ok=True)

        for path, content in paths.items():
            path.write_bytes(content)

        return list(paths)


def _get_output(
    directory: Annotated[
        Path,
        typer.Option(
            "-o",
            "--output",
            help=r"Output directory, created if missing \[default: current directory]",
            show_default=False,
            file_okay=False,
            resolve_path=True,
            rich_help_panel="Output",
        ),
    ] = Path(),
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Replace files that already exist",
            rich_help_panel="Output",
        ),
    ] = False,
) -> Output:
    return Output(directory=directory, force=force)


OutputDI = Annotated[Output, Depends(_get_output)]
"""Injects the `--output` directory and `--force`."""
