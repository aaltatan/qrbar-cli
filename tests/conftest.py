import io
import shutil
import zipfile
from collections.abc import Callable
from pathlib import Path

import openpyxl
import pytest
from typer.testing import CliRunner, Result

from qrbar_cli.cli.app import app

FIXTURES = Path(__file__).parent / "fixtures"

type Run = Callable[..., Result]


@pytest.fixture
def work(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Return a working directory holding copies of the fixtures."""
    for path in FIXTURES.iterdir():
        if path.is_file():
            shutil.copy(path, tmp_path)

    monkeypatch.chdir(tmp_path)

    return tmp_path


@pytest.fixture
def run(work: Path) -> Run:
    """Invoke the app in `work`; stdout and stderr are both in `result.output`."""
    runner = CliRunner()

    def invoke(*args: str, input: str | None = None) -> Result:  # noqa: A002
        return runner.invoke(app, list(args), input=input)

    return invoke


def make_xlsx(path: Path, rows: list[list[object]]) -> Path:
    workbook = openpyxl.Workbook()

    sheet = workbook.active

    assert sheet is not None

    for row in rows:
        sheet.append(row)

    workbook.save(path)

    return path


def document_xml(docx: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(docx)) as archive:
        return archive.read("word/document.xml").decode()


def media(docx: bytes) -> list[bytes]:
    with zipfile.ZipFile(io.BytesIO(docx)) as archive:
        return [archive.read(name) for name in archive.namelist() if name.startswith("word/media/")]
