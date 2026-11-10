"""The qrbar command line application."""

from importlib.metadata import version
from pathlib import Path
from typing import Annotated, Any

import qrbar
import typer
from qrbar import ImageFormat, symbologies
from qrbar.records import parse_records
from rich.table import Table
from typer_di import TyperDI
from typer_swissknife import command

from qrbar_cli.cli.dependencies.console import ConsoleDI
from qrbar_cli.cli.dependencies.data import Data, DataDI
from qrbar_cli.cli.dependencies.job import Job, JobDI
from qrbar_cli.cli.dependencies.layout import Mode
from qrbar_cli.cli.dependencies.output import Output, OutputDI, safe_name
from qrbar_cli.cli.errors import fail, reported
from qrbar_cli.cli.help import CODE_HELP, RENDER_HELP

app = TyperDI(
    name="qrbar",
    help="Barcode and QR code labels from templates and data: docx, ZPL and PDF.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

PAYLOADS = {
    "qr": "Any text, UTF-8 (Arabic works)",
    "datamatrix": "Any text, UTF-8; always square",
    "aztec": "Any text, UTF-8",
    "pdf417": "Any text, UTF-8",
    "code128": "ASCII only",
    "ean13": "12 digits (check digit added) or 13 (verified)",
    "upca": "11 digits, or 12 with a correct check digit",
}
"""Payload rules of the built-in codes, shown by `symbologies`."""


def _version(value: bool) -> None:
    if value:
        typer.echo(f"qrbar-cli {version('qrbar-cli')} (qrbar {version('qrbar')})")

        raise typer.Exit


@app.callback()
def _main(
    _: Annotated[
        bool,
        typer.Option("--version", "-V", callback=_version, is_eager=True, help="Show the version"),
    ] = False,
) -> None:
    """Barcode and QR code labels from templates and data: docx, ZPL and PDF."""


# -----------------------
# symbologies
# -----------------------


@command(app, name="symbologies", aliases=("s",), help="List the code types and their payloads")
def list_symbologies(console: ConsoleDI) -> None:
    table = Table("Name", "Payload", box=None, header_style="bold")

    for name in symbologies.names():
        table.add_row(f"[cyan]{name}[/]", PAYLOADS.get(name, ""))

    console.print(table)


# -----------------------
# code
# -----------------------


@command(app, name="code", aliases=("c",), no_args_is_help=True, help=CODE_HELP)
def code(
    console: ConsoleDI,
    symbology: Annotated[str, typer.Argument(help="Code type, see: qrbar symbologies")],
    payload: Annotated[str, typer.Argument(help="Text to encode")],
    output_file: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output",
            help=r"Image file; .png or .svg sets the format \[default: <symbology>.png]",
            show_default=False,
            dir_okay=False,
            resolve_path=True,
        ),
    ] = None,
    fmt: Annotated[
        ImageFormat | None,
        typer.Option(
            "--format",
            help=r"png or svg \[default: from --output, else png]",
            show_default=False,
        ),
    ] = None,
    scale: Annotated[
        int,
        typer.Option("--scale", min=1, help="PNG pixels per module (one square or thin bar)"),
    ] = qrbar.symbologies.DEFAULT_SCALE,
    force: Annotated[bool, typer.Option("--force", help="Replace the file if it exists")] = False,
) -> None:
    suffix = None if output_file is None else output_file.suffix.lstrip(".").lower()

    if fmt is None:
        fmt = "svg" if suffix == "svg" else "png"

    if suffix is not None and suffix != fmt:
        msg = f"--output '{output_file}' does not end in .{fmt}"

        raise typer.BadParameter(msg)

    if fmt == "svg" and scale != qrbar.symbologies.DEFAULT_SCALE:
        msg = "--scale only works for PNG; an SVG scales by itself"

        raise typer.BadParameter(msg)

    with reported():
        image = qrbar.render_code(symbology, payload, fmt, scale=scale)

    target = output_file or Path(f"{safe_name(symbology)}.{fmt}").resolve()

    Output(directory=target.parent, force=force).write({target.name: image})

    console.print(f"[green]Written:[/] {target}", soft_wrap=True)


# -----------------------
# render
# -----------------------


@command(app, name="render", aliases=("r",), no_args_is_help=True, help=RENDER_HELP)
def render(console: ConsoleDI, job: JobDI, data: DataDI, output: OutputDI) -> None:
    # `job` comes before `data`: bad option combinations fail before --schema asks anything
    if not data:
        fail("No records to render (the data is empty, or --filter matched nothing).")

    # no rich spinner: its characters crash legacy Windows consoles (e.g. cp1256)
    with reported():
        files = _render(job, data)

        if job.pdf:
            console.print("Converting to PDF with LibreOffice...")

            try:
                files = {
                    name: qrbar.docx_to_pdf(content, soffice=job.soffice)
                    for name, content in files.items()
                }

            except qrbar.ConversionError as error:
                # qrbar's message names its soffice= argument; here it is an option
                fail(f"Error: {str(error).replace("soffice='", "--soffice '")}")

    if not files:
        fail("Nothing rendered: every record has qty 0.")

    if job.template.path.name in files and output.directory == job.template.path.parent:
        fail(f"Refusing to overwrite the template {job.template.path.name}: use -f or -o.")

    paths = output.write(files)

    if len(paths) == 1:
        console.print(f"[green]Written:[/] {paths[0]}", soft_wrap=True)

        return

    console.print(f"[green]{len(paths)} files written to:[/] {output.directory}", soft_wrap=True)


def _render(job: Job, data: Data) -> dict[str, bytes]:
    """Render the data, returning file names (with extension) and contents."""
    template = job.template

    layout = job.layout

    if layout.mode != Mode.PER_ITEM:
        document = qrbar.render(
            template.content,
            data,
            mode="sheet" if layout.mode == Mode.SHEET else "paged",
            kind=template.kind,
            qty_field=job.qty_field,
            sheet=layout.sheet,
            options=layout.options,
            collate=layout.collate,
            max_copies=job.max_copies,
            font=job.font,
        )

        name = safe_name(job.filename or f"{template.path.stem}-labels")

        return {f"{name}.{job.extension}": document}

    documents = qrbar.render(
        template.content,
        data,
        mode="per_item",
        kind=template.kind,
        qty_field=job.qty_field,
        max_copies=job.max_copies,
        font=job.font,
    )

    # qty 0 records give no document, so name the documents by the records kept
    kept = [record.index for record in parse_records(data, job.qty_field)]

    names = [_item_name(job, data[index], index) for index in kept]

    duplicates = sorted({name for name in names if names.count(name) > 1})

    if duplicates:
        fail(f"Two or more records give the same file name: {', '.join(duplicates[:5])}")

    return {
        f"{name}.{job.extension}": document for name, document in zip(names, documents, strict=True)
    }


def _item_name(job: Job, item: dict[str, Any], index: int) -> str:
    row = index + 1

    if job.name_by is None:
        name = f"{job.template.path.stem}-{row}"

    elif item.get(job.name_by) in {None, ""}:
        fail(f"Record {index} has no value in --name-by column '{job.name_by}'.")

    else:
        name = str(item[job.name_by])

    return safe_name(f"{row} - {name}" if job.numbered else name)


def main() -> None:
    """Run the qrbar application."""
    app()
