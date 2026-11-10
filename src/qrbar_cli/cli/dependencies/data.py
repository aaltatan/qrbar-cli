"""The data options: `--data` / `--schema`, `--order` and `--filter`.

Reading and transforming come from pyrecords, asking for data from schemify.
"""

import json
from pathlib import Path
from typing import Annotated, Any
from zipfile import BadZipFile

import typer
from pyrecords import (
    ExtensionNotSupportedError,
    OrderByKey,
    filter_data,
    get_compiler,
    order_by_data,
    readers,
)
from pyspecification import (
    ArgumentError,
    ProcessArgumentError,
    RuleDoesNotExistError,
    RuleKeyDoesNotExistError,
)
from schemify import ask_list
from schemify.cli.dependencies.schema import ask_or_abort, load_schema
from typer_di import Depends

type Data = list[dict[str, Any]]

_PANEL = "Data"


def _read(
    file: Annotated[
        Path | None,
        typer.Option(
            "-d",
            "--data",
            help="Data file: .xlsx (first row = column names) or .json (a list of objects)",
            exists=True,
            dir_okay=False,
            resolve_path=True,
            rich_help_panel=_PANEL,
        ),
    ] = None,
    schema_path: Annotated[
        Path | None,
        typer.Option(
            "-s",
            "--schema",
            help="JSON Schema file: ask for the records interactively instead of --data",
            exists=True,
            dir_okay=False,
            resolve_path=True,
            rich_help_panel=_PANEL,
        ),
    ] = None,
) -> Data:
    if file is None and schema_path is not None:
        asked: Data = ask_or_abort(load_schema(schema_path), ask_list)

        return asked

    if file is None or schema_path is not None:
        msg = "Give exactly one data source: -d / --data or -s / --schema"

        raise typer.BadParameter(msg)

    try:
        data = readers[file.suffix.lstrip(".")](file)

    except ExtensionNotSupportedError as error:
        raise typer.BadParameter(str(error)) from error

    except (ValueError, BadZipFile, UnicodeDecodeError) as error:
        msg = f"Could not read data file '{file.name}': {error}"

        raise typer.BadParameter(msg) from error

    return data


def _order(
    data: Annotated[Data, Depends(_read)],
    order: Annotated[
        list[str],
        typer.Option(
            "--order",
            help="Column to order by, -column for descending (repeatable)",
            default_factory=list,
            show_default=False,
            rich_help_panel=_PANEL,
        ),
    ],
) -> Data:
    if not order:
        return data

    try:
        ordered: Data = order_by_data(data, [OrderByKey(key) for key in order])

    except KeyError as error:
        raise typer.BadParameter(str(error)) from error

    return ordered


def _filter(
    data: Annotated[Data, Depends(_order)],
    json_string: Annotated[
        str | None,
        typer.Option(
            "--filter",
            help="Keep matching records: a filter schema as JSON",
            rich_help_panel=_PANEL,
        ),
    ] = None,
) -> Data:
    if json_string is None:
        return data

    try:
        schema = json.loads(json_string)

        filtered: Data = filter_data(data, get_compiler(), schema)

    except json.JSONDecodeError as error:
        msg = f"--filter is not valid JSON: {error}"

        raise typer.BadParameter(msg) from error

    except (
        RuleKeyDoesNotExistError,
        RuleDoesNotExistError,
        ArgumentError,
        ProcessArgumentError,
    ) as error:
        raise typer.BadParameter(str(error)) from error

    except (TypeError, ValueError, AttributeError, KeyError) as error:
        msg = f"Filter failed on a data value (empty cell or wrong type?): {error}"

        raise typer.BadParameter(msg) from error

    return filtered


DataDI = Annotated[Data, Depends(_filter)]
"""Injects the records from `--data` or `--schema`, ordered and filtered."""
