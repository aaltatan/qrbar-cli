"""Run every `qrbar` command in the README's bash blocks against `examples/`."""

import re
import shlex
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from qrbar_cli.cli.app import app

ROOT = Path(__file__).parent.parent

BLOCKS = re.findall(
    r"```bash\n(.*?)```", (ROOT / "README.md").read_text(encoding="utf-8"), re.DOTALL
)


def commands(block: str) -> list[list[str]]:
    """Split a bash block into commands, joining backslash continuations and open quotes."""
    found: list[list[str]] = []

    buffer = ""

    for line in block.splitlines():
        buffer += line.removesuffix("\\") + "\n"

        if line.endswith("\\"):
            continue

        try:
            words = shlex.split(buffer, comments=True)

        except ValueError:  # a quote is still open
            continue

        buffer = ""

        if words:
            found.append(words)

    assert not buffer.strip(), f"unfinished command: {buffer}"

    return found


COMMANDS = [words for block in BLOCKS for words in commands(block) if words[0] == "qrbar"]


def test_the_readme_has_commands() -> None:
    assert len(COMMANDS) > 25


@pytest.mark.parametrize("words", COMMANDS, ids=[" ".join(words)[:80] for words in COMMANDS])
def test_readme_command(words: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    shutil.copytree(ROOT / "examples", tmp_path, dirs_exist_ok=True)

    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, words[1:])

    assert result.exit_code == 0, result.output
