from pathlib import Path

import pytest
import zxingcpp
from conftest import Run
from PIL import Image


def decode(path: Path) -> str:
    with Image.open(path) as image:
        results = zxingcpp.read_barcodes(image)

    assert len(results) == 1

    return results[0].text


def test_png_named_after_the_symbology(run: Run, work: Path) -> None:
    result = run("code", "qr", "https://example.com/item/42")

    assert result.exit_code == 0, result.output

    assert decode(work / "qr.png") == "https://example.com/item/42"


@pytest.mark.parametrize(
    ("symbology", "payload", "expected"),
    [
        ("ean13", "400638133393", "4006381333931"),
        ("code128", "SKU-00042", "SKU-00042"),
        ("datamatrix", "SKU-00042", "SKU-00042"),
        ("qr", "مصباح مكتب", "مصباح مكتب"),
    ],
)
def test_png_round_trip(run: Run, work: Path, symbology: str, payload: str, expected: str) -> None:
    result = run("code", symbology, payload, "-o", "out/code.png", "--scale", "6")

    assert result.exit_code == 0, result.output

    assert decode(work / "out" / "code.png") == expected


def test_svg_from_the_output_extension(run: Run, work: Path) -> None:
    result = run("code", "aztec", "hello", "-o", "a.svg")

    assert result.exit_code == 0, result.output

    assert (work / "a.svg").read_bytes().lstrip().startswith(b"<")


def test_format_and_extension_must_agree(run: Run) -> None:
    result = run("code", "qr", "x", "-o", "a.png", "--format", "svg")

    assert result.exit_code == 2

    assert "does not end in .svg" in result.output


def test_scale_with_svg_is_rejected(run: Run) -> None:
    result = run("code", "qr", "x", "--format", "svg", "--scale", "9")

    assert result.exit_code == 2

    assert "--scale only works for PNG" in result.output


def test_bad_payload_names_the_problem(run: Run, work: Path) -> None:
    result = run("code", "ean13", "4006381333932")

    assert result.exit_code == 1

    assert "wrong check digit" in result.output

    assert not (work / "ean13.png").exists()


def test_unknown_symbology_lists_the_names(run: Run) -> None:
    result = run("code", "qrr", "x")

    assert result.exit_code == 1

    assert "Available: aztec" in result.output


def test_existing_file_needs_force(run: Run, work: Path) -> None:
    (work / "qr.png").write_bytes(b"keep me")

    result = run("code", "qr", "x")

    assert result.exit_code == 1

    assert "--force" in result.output

    assert (work / "qr.png").read_bytes() == b"keep me"

    assert run("code", "qr", "x", "--force").exit_code == 0

    assert decode(work / "qr.png") == "x"
