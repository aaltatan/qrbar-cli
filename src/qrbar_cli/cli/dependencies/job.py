"""Everything `render` needs besides the data, checked before the data is read.

Checking first matters with `--schema`: a bad option combination must fail before the
user types any records.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from qrbar import DEFAULT_MAX_COPIES
from typer_di import Depends

from qrbar_cli.cli.dependencies.layout import Layout, LayoutDI, Mode
from qrbar_cli.cli.dependencies.template import Template, TemplateDI

_RENDER_PANEL = "Rendering"

_NAMING_PANEL = "File names"


@dataclass(frozen=True)
class Job:
    template: Template
    layout: Layout
    qty_field: str
    max_copies: int | None
    font: bytes | None
    pdf: bool
    soffice: str | None
    filename: str | None
    name_by: str | None
    numbered: bool

    @property
    def extension(self) -> str:
        """The extension of the written files: the template's, or `pdf`."""
        return "pdf" if self.pdf else self.template.extension


def _get_job(
    template: TemplateDI,
    layout: LayoutDI,
    qty_field: Annotated[
        str,
        typer.Option(
            "--qty-field",
            help="Column holding each record's copy count",
            rich_help_panel=_RENDER_PANEL,
        ),
    ] = "qty",
    max_copies: Annotated[
        int,
        typer.Option(
            "--max-copies",
            min=0,
            help="Refuse more copies than this in total; 0 = no limit",
            rich_help_panel=_RENDER_PANEL,
        ),
    ] = DEFAULT_MAX_COPIES,
    font: Annotated[
        Path | None,
        typer.Option(
            "--font",
            exists=True,
            dir_okay=False,
            resolve_path=True,
            help=r"TTF/OTF font for Arabic text() in ZPL \[default: bundled IBM Plex Sans Arabic]",
            show_default=False,
            rich_help_panel=_RENDER_PANEL,
        ),
    ] = None,
    pdf: Annotated[
        bool,
        typer.Option(
            "--pdf",
            help="Write PDF instead of docx (needs LibreOffice)",
            rich_help_panel=_RENDER_PANEL,
        ),
    ] = False,
    soffice: Annotated[
        str | None,
        typer.Option(
            "--soffice",
            help=r"LibreOffice executable for --pdf \[default: found on PATH]",
            show_default=False,
            rich_help_panel=_RENDER_PANEL,
        ),
    ] = None,
    filename: Annotated[
        str | None,
        typer.Option(
            "-f",
            "--filename",
            help=r"Output file name without extension \[default: template name]",
            show_default=False,
            rich_help_panel=_NAMING_PANEL,
        ),
    ] = None,
    name_by: Annotated[
        str | None,
        typer.Option(
            "-n",
            "--name-by",
            help=r"per_item: column naming each file \[default: <template>-<row>]",
            show_default=False,
            rich_help_panel=_NAMING_PANEL,
        ),
    ] = None,
    numbered: Annotated[
        bool,
        typer.Option(
            "--numbered",
            help="per_item: prefix each file name with its row number: 1 - Lamp",
            rich_help_panel=_NAMING_PANEL,
        ),
    ] = False,
) -> Job:
    _check(template, layout, font=font, pdf=pdf, soffice=soffice)

    _check_naming(layout.mode, filename=filename, name_by=name_by, numbered=numbered)

    return Job(
        template=template,
        layout=layout,
        qty_field=qty_field,
        max_copies=max_copies or None,
        font=None if font is None else font.read_bytes(),
        pdf=pdf,
        soffice=soffice,
        filename=filename,
        name_by=name_by,
        numbered=numbered,
    )


def _check(
    template: Template,
    layout: Layout,
    *,
    font: Path | None,
    pdf: bool,
    soffice: str | None,
) -> None:
    zpl = template.kind == "zpl"

    problems = [
        (zpl and layout.mode == Mode.SHEET, "ZPL has no sheets: use --mode paged or per_item"),
        (
            zpl and layout.collate == "interleaved",
            "ZPL prints copies with ^PQ, so --collate interleaved does not work",
        ),
        (pdf and zpl, "--pdf only works with .docx templates"),
        (soffice is not None and not pdf, "--soffice only works with --pdf"),
        (
            font is not None and not zpl,
            "--font only works with ZPL templates; a docx uses its own fonts",
        ),
    ]

    for failed, message in problems:
        if failed:
            raise typer.BadParameter(message)


def _check_naming(mode: Mode, *, filename: str | None, name_by: str | None, numbered: bool) -> None:
    """Reject naming options the mode does not use, instead of silently ignoring them."""
    if mode == Mode.PER_ITEM:
        unused = {"--filename": filename is not None}
        reason = "does not work with --mode per_item (use --name-by)"

    else:
        unused = {"--name-by": name_by is not None, "--numbered": numbered}
        reason = "only works with --mode per_item"

    for option, given in unused.items():
        if given:
            msg = f"{option} {reason}"

            raise typer.BadParameter(msg)


JobDI = Annotated[Job, Depends(_get_job)]
"""Injects the template and every `render` option, checked against each other."""
