"""Report runtime failures as a red message and exit code 1, never as a traceback."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import NoReturn

import typer
from qrbar import QrbarError


def fail(message: str) -> NoReturn:
    """Print `message` in red on stderr and exit with code 1."""
    typer.secho(message, fg="red", err=True)

    raise typer.Exit(1)


@contextmanager
def reported() -> Iterator[None]:
    """Turn qrbar errors (bad data, payload, LibreOffice missing) into `fail`."""
    try:
        yield

    except QrbarError as error:
        fail(f"Error: {error}")
