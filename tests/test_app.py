from conftest import Run


def test_help_lists_the_commands(run: Run) -> None:
    result = run("--help")

    assert result.exit_code == 0

    for name in ("symbologies", "code", "render"):
        assert name in result.output


def test_version(run: Run) -> None:
    result = run("--version")

    assert result.exit_code == 0

    assert result.output.startswith("qrbar-cli ")

    assert "(qrbar " in result.output


def test_symbologies_lists_every_code_with_its_payload(run: Run) -> None:
    result = run("symbologies")

    assert result.exit_code == 0

    for name in ("qr", "code128", "ean13", "upca", "datamatrix", "pdf417", "aztec"):
        assert name in result.output

    assert "12 digits" in result.output


def test_alias(run: Run) -> None:
    assert run("s").output == run("symbologies").output
