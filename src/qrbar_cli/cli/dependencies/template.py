"""The `--template` option: its bytes and kind (docx or ZPL), picked by extension."""

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from qrbar import TemplateKind
from typer_di import Depends

KINDS: dict[str, TemplateKind] = {"docx": "docx", "zpl": "zpl", "prn": "zpl"}
"""Template extensions and the qrbar kind each one renders as."""


@dataclass(frozen=True)
class Template:
    """A template file read into memory."""

    path: Path
    content: bytes
    kind: TemplateKind

    @property
    def extension(self) -> str:
        """The extension, lowercase and without the dot: `docx`, `zpl` or `prn`."""
        return self.path.suffix.lstrip(".").lower()


def _get_template(
    path: Annotated[
        Path,
        typer.Option(
            "-t",
            "--template",
            help="Template file: .docx, .zpl or .prn",
            exists=True,
            dir_okay=False,
            resolve_path=True,
            show_default=False,
        ),
    ],
) -> Template:
    kind = KINDS.get(path.suffix.lstrip(".").lower())

    if kind is None:
        msg = f"Template '{path.name}' must be .docx, .zpl or .prn"

        raise typer.BadParameter(msg)

    return Template(path=path, content=path.read_bytes(), kind=kind)


TemplateDI = Annotated[Template, Depends(_get_template)]
"""Injects the `--template` file."""
