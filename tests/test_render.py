import io
import json
import shutil
from pathlib import Path

import pytest
import qrbar
import zxingcpp
from conftest import FIXTURES, Run, document_xml, make_xlsx, media
from PIL import Image
from qrbar.pdf import find_soffice

ITEMS = json.loads((FIXTURES / "items.json").read_text(encoding="utf-8"))

# -----------------------
# ZPL
# -----------------------


def test_zpl_paged_matches_the_library(run: Run, work: Path) -> None:
    result = run("render", "-t", "label_203dpi.zpl", "-d", "items.json")

    assert result.exit_code == 0, result.output

    written = (work / "label_203dpi-labels.zpl").read_bytes()

    assert written == qrbar.render((FIXTURES / "label_203dpi.zpl").read_bytes(), ITEMS)

    # qty 2 is one block printed twice, qty 0 is skipped
    assert written.count(b"^XA") == 2

    assert b"^PQ2" in written


def test_prn_keeps_its_extension_and_filename(run: Run, work: Path) -> None:
    shutil.copy(work / "label_203dpi.zpl", work / "label.prn")

    result = run("render", "-t", "label.prn", "-d", "items.json", "-f", "today", "-o", "out")

    assert result.exit_code == 0, result.output

    assert (work / "out" / "today.prn").is_file()


def test_zpl_per_item_named_by_column(run: Run, work: Path) -> None:
    result = run(
        "render", "-t", "label_203dpi.zpl", "-d", "items.json", "-m", "per_item", "-n", "sku"
    )

    assert result.exit_code == 0, result.output

    assert "2 files written" in result.output

    assert (work / "SKU-1.zpl").read_bytes().count(b"^XA") == 1

    assert (work / "SKU-2.zpl").is_file()

    assert not (work / "SKU-3.zpl").exists()  # qty 0


def test_per_item_default_and_numbered_names(run: Run, work: Path) -> None:
    assert (
        run("render", "-t", "label_203dpi.zpl", "-d", "items.json", "-m", "per_item").exit_code == 0
    )

    assert {path.name for path in work.glob("label_203dpi-*.zpl")} == {
        "label_203dpi-1.zpl",
        "label_203dpi-2.zpl",
    }

    result = run(
        "render", "-t", "label_203dpi.zpl", "-d", "items.json", "-m", "per_item",
        "-n", "name", "--numbered",
    )  # fmt: skip

    assert result.exit_code == 0, result.output

    assert (work / "1 - Lamp.zpl").is_file()

    assert (work / "2 - Desk lamp.zpl").is_file()


def test_per_item_names_from_data_cannot_escape_the_folder(run: Run, work: Path) -> None:
    (work / "evil.json").write_text(json.dumps([{**ITEMS[1], "sku": "../../x:y"}]))

    result = run(
        "render", "-t", "label_203dpi.zpl", "-d", "evil.json", "-m", "per_item", "-n", "sku"
    )

    assert result.exit_code == 0, result.output

    assert (work / "_.._x_y.zpl").is_file()


def test_per_item_duplicate_names_are_refused(run: Run, work: Path) -> None:
    (work / "dup.json").write_text(json.dumps([ITEMS[1], ITEMS[1]]))

    result = run(
        "render", "-t", "label_203dpi.zpl", "-d", "dup.json", "-m", "per_item", "-n", "sku"
    )

    assert result.exit_code == 1

    assert "same file name: SKU-2" in result.output

    assert not list(work.glob("SKU-2*"))


def test_per_item_missing_name_value(run: Run, work: Path) -> None:
    (work / "blank.json").write_text(json.dumps([{**ITEMS[1], "name": ""}]))

    result = run(
        "render", "-t", "label_203dpi.zpl", "-d", "blank.json", "-m", "per_item", "-n", "name"
    )

    assert result.exit_code == 1

    assert "Record 0 has no value" in result.output


def test_arabic_text_with_bundled_and_custom_font(run: Run, work: Path) -> None:
    (work / "ar.json").write_text(json.dumps([{"name": "مصباح"}]), encoding="utf-8")

    result = run("render", "-t", "arabic.zpl", "-d", "ar.json")

    assert result.exit_code == 0, result.output

    assert b"^GFA" in (work / "arabic-labels.zpl").read_bytes()

    font = Path(qrbar.__file__).parent / "fonts"

    ttf = next(path for path in font.iterdir() if path.suffix.lower() in {".ttf", ".otf"})

    result = run("render", "-t", "arabic.zpl", "-d", "ar.json", "--font", str(ttf), "--force")

    assert result.exit_code == 0, result.output


# -----------------------
# docx
# -----------------------


def test_docx_paged_from_excel(run: Run, work: Path) -> None:
    make_xlsx(
        work / "items.xlsx", [["sku", "name", "qty"], ["SKU-1", "Lamp", 3], ["SKU-2", "Bulb", None]]
    )

    result = run("render", "-t", "label_paged.docx", "-d", "items.xlsx")

    assert result.exit_code == 0, result.output

    docx = (work / "label_paged-labels.docx").read_bytes()

    xml = document_xml(docx)

    assert xml.count("Lamp") == 3

    assert xml.count("Bulb") == 1

    with Image.open(io.BytesIO(media(docx)[0])) as image:
        assert zxingcpp.read_barcodes(image)[0].text in {"SKU-1", "SKU-2"}


def test_docx_sheet(run: Run, work: Path) -> None:
    result = run(
        "render", "-t", "sheet_a4_3x8.docx", "-d", "items.json",
        "-m", "sheet", "--rows", "8", "--cols", "3", "--skip", "2", "--fill-last",
    )  # fmt: skip

    assert result.exit_code == 0, result.output

    xml = document_xml((work / "sheet_a4_3x8-labels.docx").read_bytes())

    assert xml.count("<w:tc>") == 24  # one full A4 3x8 sheet

    assert xml.count("Lamp") == 2  # "Desk lamp" is lowercase


def test_docx_sheet_interleaved(run: Run, work: Path) -> None:
    result = run(
        "render", "-t", "sheet_a4_3x8.docx", "-d", "items.json",
        "-m", "sheet", "--rows", "8", "--cols", "3", "--collate", "interleaved",
    )  # fmt: skip

    assert result.exit_code == 0, result.output

    xml = document_xml((work / "sheet_a4_3x8-labels.docx").read_bytes())

    assert xml.index(">Lamp<") < xml.index("Desk lamp") < xml.rindex(">Lamp<")


def test_docx_per_item(run: Run, work: Path) -> None:
    result = run(
        "render", "-t", "label_paged.docx", "-d", "items.json", "-m", "per_item", "-n", "sku"
    )

    assert result.exit_code == 0, result.output

    assert document_xml((work / "SKU-1.docx").read_bytes()).count("Lamp") == 2


# -----------------------
# data options
# -----------------------


def test_order_and_filter(run: Run, work: Path) -> None:
    result = run(
        "render", "-t", "label_203dpi.zpl", "-d", "items.json", "--order", "-sku",
        "--filter", '{"name": "string__contains", "args": ["name", "Desk"], "kwargs": {}, "inverse": false}',
    )  # fmt: skip

    assert result.exit_code == 0, result.output

    written = (work / "label_203dpi-labels.zpl").read_bytes()

    assert b"SKU-2" in written

    assert b"SKU-1" not in written


def test_filter_matching_nothing(run: Run) -> None:
    result = run(
        "render", "-t", "label_203dpi.zpl", "-d", "items.json",
        "--filter", '{"name": "string__eq", "args": ["name", "nope"], "kwargs": {}, "inverse": false}',
    )  # fmt: skip

    assert result.exit_code == 1

    assert "No records to render" in result.output


def test_bad_filter_json(run: Run) -> None:
    result = run("render", "-t", "label_203dpi.zpl", "-d", "items.json", "--filter", "{")

    assert result.exit_code == 2

    assert "not valid JSON" in result.output


def test_schema_asks_for_records(run: Run, work: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from qrbar_cli.cli.dependencies import data  # noqa: PLC0415

    monkeypatch.setattr(data, "ask_list", lambda _schema: [{"sku": "S-9", "name": "Typed"}])

    result = run("render", "-t", "label_paged.docx", "-s", "items.schema.json")

    assert result.exit_code == 0, result.output

    assert "Typed" in document_xml((work / "label_paged-labels.docx").read_bytes())


def test_bad_options_fail_before_asking(run: Run, monkeypatch: pytest.MonkeyPatch) -> None:
    from qrbar_cli.cli.dependencies import data  # noqa: PLC0415

    def never(_schema: object) -> object:
        raise AssertionError

    monkeypatch.setattr(data, "ask_list", never)

    result = run(
        "render",
        "-t",
        "label_203dpi.zpl",
        "-s",
        "items.schema.json",
        "-m",
        "sheet",
        "--rows",
        "1",
        "--cols",
        "1",
    )

    assert result.exit_code == 2

    assert "ZPL has no sheets" in result.output


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ([], "exactly one data source"),
        (["-d", "items.json", "-s", "items.schema.json"], "exactly one data source"),
        (["-d", "label_203dpi.zpl"], "not supported"),
    ],
)
def test_data_source_errors(run: Run, args: list[str], message: str) -> None:
    result = run("render", "-t", "label_203dpi.zpl", *args)

    assert result.exit_code == 2

    assert message in result.output


def test_bad_json_data(run: Run, work: Path) -> None:
    (work / "bad.json").write_text('{"not": "a list"}')

    result = run("render", "-t", "label_203dpi.zpl", "-d", "bad.json")

    assert result.exit_code == 2

    assert "list of objects" in result.output


# -----------------------
# qrbar errors and option checks
# -----------------------


def test_bad_qty_names_the_record(run: Run, work: Path) -> None:
    (work / "qty.json").write_text(json.dumps([ITEMS[1], {**ITEMS[1], "qty": -1}]))

    result = run("render", "-t", "label_203dpi.zpl", "-d", "qty.json")

    assert result.exit_code == 1

    assert "Error:" in result.output

    assert "-1" in result.output

    assert "Traceback" not in result.output


def test_custom_qty_field_and_max_copies(run: Run, work: Path) -> None:
    (work / "n.json").write_text(json.dumps([{**ITEMS[1], "n": 50}]))

    result = run(
        "render", "-t", "label_203dpi.zpl", "-d", "n.json", "--qty-field", "n", "--max-copies", "10"
    )

    assert result.exit_code == 1

    assert "max_copies=10" in result.output

    result = run(
        "render", "-t", "label_203dpi.zpl", "-d", "n.json", "--qty-field", "n", "--max-copies", "0"
    )

    assert result.exit_code == 0, result.output

    assert b"^PQ50" in (work / "label_203dpi-labels.zpl").read_bytes()


def test_existing_output_needs_force(run: Run, work: Path) -> None:
    assert run("render", "-t", "label_203dpi.zpl", "-d", "items.json").exit_code == 0

    result = run("render", "-t", "label_203dpi.zpl", "-d", "items.json")

    assert result.exit_code == 1

    assert "--force" in result.output

    assert run("render", "-t", "label_203dpi.zpl", "-d", "items.json", "--force").exit_code == 0


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["-t", "items.json"], "must be .docx, .zpl or .prn"),
        (["-t", "label_paged.docx", "--rows", "2"], "--rows only works with --mode sheet"),
        (["-t", "label_paged.docx", "--fill-last"], "--fill-last only works with --mode sheet"),
        (["-t", "label_paged.docx", "-m", "sheet", "--rows", "2"], "needs --rows and --cols"),
        (
            ["-t", "label_paged.docx", "-m", "sheet", "--rows", "2", "--cols", "2", "--skip", "4"],
            "leaves no label free",
        ),
        (
            ["-t", "label_paged.docx", "-m", "sheet", "--rows", "2", "--cols", "2",
             "--new-page-per-record", "--collate", "interleaved"],
            "cannot be interleaved",
        ),
        (["-t", "label_paged.docx", "-m", "per_item", "--collate", "grouped"], "--collate does not work"),
        (["-t", "label_203dpi.zpl", "--collate", "interleaved"], "^PQ"),
        (["-t", "label_203dpi.zpl", "--pdf"], "--pdf only works with .docx"),
        (["-t", "label_paged.docx", "--soffice", "x"], "--soffice only works with --pdf"),
        (["-t", "label_paged.docx", "--font", "items.json"], "--font only works with ZPL"),
        (["-t", "label_paged.docx", "-m", "per_item", "-f", "x"], "--filename does not work"),
        (["-t", "label_paged.docx", "-n", "sku"], "--name-by only works with --mode per_item"),
        (["-t", "label_paged.docx", "--numbered"], "--numbered only works with --mode per_item"),
    ],
)  # fmt: skip
def test_option_errors(run: Run, args: list[str], message: str) -> None:
    result = run("render", "-d", "items.json", *args)

    assert result.exit_code == 2

    assert message in " ".join(result.output.split()).replace("| ", "")


# -----------------------
# PDF
# -----------------------


def test_pdf_converts_every_document(run: Run, work: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str | None] = []

    def fake(docx: bytes, *, soffice: str | None = None) -> bytes:
        assert docx.startswith(b"PK")

        calls.append(soffice)

        return b"%PDF-fake"

    monkeypatch.setattr(qrbar, "docx_to_pdf", fake)

    result = run(
        "render", "-t", "label_paged.docx", "-d", "items.json",
        "-m", "per_item", "-n", "sku", "--pdf", "--soffice", "my-soffice",
    )  # fmt: skip

    assert result.exit_code == 0, result.output

    assert calls == ["my-soffice", "my-soffice"]

    assert (work / "SKU-1.pdf").read_bytes() == b"%PDF-fake"

    assert not list(work.glob("SKU-*.docx"))


def test_pdf_without_libreoffice(run: Run, work: Path) -> None:
    result = run(
        "render",
        "-t",
        "label_paged.docx",
        "-d",
        "items.json",
        "--pdf",
        "--soffice",
        str(work / "nope.exe"),
    )

    assert result.exit_code == 1

    assert "LibreOffice was not found" in result.output

    assert not (work / "label_paged-labels.pdf").exists()


def test_missing_libreoffice_hint_names_the_option(
    run: Run, monkeypatch: pytest.MonkeyPatch
) -> None:
    def missing(docx: bytes, *, soffice: str | None = None) -> bytes:
        msg = "LibreOffice ... was not found: install it or pass soffice='/path/to/soffice'."

        raise qrbar.ConversionError(msg)

    monkeypatch.setattr(qrbar, "docx_to_pdf", missing)

    result = run("render", "-t", "label_paged.docx", "-d", "items.json", "--pdf")

    assert result.exit_code == 1

    assert "pass --soffice '/path/to/soffice'" in result.output


def _has_libreoffice() -> bool:
    try:
        find_soffice()  # PATH and the default install folders, as --pdf does

    except qrbar.ConversionError:
        return False

    return True


@pytest.mark.skipif(not _has_libreoffice(), reason="LibreOffice is not installed")
def test_pdf_with_libreoffice(run: Run, work: Path) -> None:
    from pypdf import PdfReader  # noqa: PLC0415

    result = run("render", "-t", "label_paged.docx", "-d", "items.json", "--pdf")

    assert result.exit_code == 0, result.output

    assert len(PdfReader(work / "label_paged-labels.pdf").pages) == 3


def test_never_overwrites_the_template(run: Run, work: Path) -> None:
    before = (work / "label_203dpi.zpl").read_bytes()

    result = run(
        "render", "-t", "label_203dpi.zpl", "-d", "items.json", "-f", "label_203dpi", "--force"
    )

    assert result.exit_code == 1

    assert "Refusing to overwrite the template" in result.output

    assert (work / "label_203dpi.zpl").read_bytes() == before
