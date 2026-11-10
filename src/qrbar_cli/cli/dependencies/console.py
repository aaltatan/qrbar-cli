"""The rich console used for command output."""

from typing import Annotated

from rich.console import Console
from typer_di import Depends

ConsoleDI = Annotated[Console, Depends(lambda: Console())]  # noqa: PLW0108 - typer-di would read Console(file=...) as options
"""Injects a rich console."""
