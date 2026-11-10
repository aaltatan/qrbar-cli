"""The layout options: `--mode` and the sheet options, mapped onto `qrbar.render`."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated

import typer
from qrbar import Collate, SheetOptions, SheetSpec
from typer_di import Depends

_PANEL = "Layout"

_SHEET_PANEL = "Sheet (--mode sheet, docx only)"


class Mode(StrEnum):
    PAGED = "paged"
    SHEET = "sheet"
    PER_ITEM = "per_item"


class CollateChoice(StrEnum):
    GROUPED = "grouped"
    INTERLEAVED = "interleaved"


@dataclass(frozen=True)
class Layout:
    """The `mode`, `sheet`, `options` and `collate` arguments of `qrbar.render`."""

    mode: Mode
    sheet: SheetSpec | None = None
    options: SheetOptions | None = None
    collate: Collate | None = None


def _get_layout(
    mode: Annotated[
        Mode,
        typer.Option(
            "-m",
            "--mode",
            help="paged: one file, a label per copy. sheet: label sheets. "
            "per_item: one file per record",
            rich_help_panel=_PANEL,
        ),
    ] = Mode.PAGED,
    collate: Annotated[
        CollateChoice | None,
        typer.Option(
            "--collate",
            help=r"Copy order: grouped (A,A,B,B) or interleaved (A,B,A,B) \[default: grouped]",
            show_default=False,
            rich_help_panel=_PANEL,
        ),
    ] = None,
    rows: Annotated[
        int | None,
        typer.Option("--rows", min=1, help="Labels down a sheet", rich_help_panel=_SHEET_PANEL),
    ] = None,
    cols: Annotated[
        int | None,
        typer.Option("--cols", min=1, help="Labels across a sheet", rich_help_panel=_SHEET_PANEL),
    ] = None,
    skip: Annotated[
        int,
        typer.Option(
            "--skip",
            min=0,
            help="Leave the first N labels empty, to reuse a partly used sheet",
            rich_help_panel=_SHEET_PANEL,
        ),
    ] = 0,
    fill_last: Annotated[
        bool,
        typer.Option(
            "--fill-last",
            help="Pad the last sheet with empty labels",
            rich_help_panel=_SHEET_PANEL,
        ),
    ] = False,
    new_page_per_record: Annotated[
        bool,
        typer.Option(
            "--new-page-per-record",
            help="Start each record's copies on a new sheet",
            rich_help_panel=_SHEET_PANEL,
        ),
    ] = False,
) -> Layout:
    chosen: Collate | None = None if collate is None else collate.value

    if mode != Mode.SHEET:
        given = {
            "--rows": rows is not None,
            "--cols": cols is not None,
            "--skip": skip != 0,
            "--fill-last": fill_last,
            "--new-page-per-record": new_page_per_record,
        }

        for option, used in given.items():
            if used:
                msg = f"{option} only works with --mode sheet"

                raise typer.BadParameter(msg)

        if mode == Mode.PER_ITEM and collate is not None:
            msg = "--collate does not work with --mode per_item (one file per record)"

            raise typer.BadParameter(msg)

        return Layout(mode=mode, collate=chosen)

    if rows is None or cols is None:
        msg = "--mode sheet needs --rows and --cols"

        raise typer.BadParameter(msg)

    if skip >= rows * cols:
        msg = f"--skip {skip} leaves no label free on a {rows}x{cols} sheet"

        raise typer.BadParameter(msg)

    if new_page_per_record and chosen == "interleaved":
        msg = "--new-page-per-record keeps a record's copies together, it cannot be interleaved"

        raise typer.BadParameter(msg)

    options = SheetOptions(
        skip=skip,
        fill_last=fill_last,
        new_page_per_record=new_page_per_record,
    )

    return Layout(mode=mode, sheet=SheetSpec(rows=rows, cols=cols), options=options, collate=chosen)


LayoutDI = Annotated[Layout, Depends(_get_layout)]
"""Injects the `--mode` and sheet options, checked against each other."""
