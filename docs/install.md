# Installation

qrbar-cli needs **Python 3.12 or newer**. Install it as a tool, so the `qrbar` command
is available everywhere without touching your other Python projects:

=== "uv"

    ```text
    uv tool install qrbar-cli
    ```

=== "pipx"

    ```text
    pipx install qrbar-cli
    ```

=== "pip"

    ```text
    pip install qrbar-cli
    ```

Everything it needs, including Arabic text shaping, installs as prebuilt wheels. No
compiler and no system libraries.

Check that it works:

```text
$ qrbar --version
qrbar-cli 0.1.0 (qrbar 0.1.2)
```

## Optional: LibreOffice for PDF

`--pdf` converts Word output to PDF with [LibreOffice](https://www.libreoffice.org). You
only need it for that one option. qrbar finds LibreOffice on `PATH` or in its default
install folder. Otherwise, point to it with `--soffice` (see [PDF](guide/pdf.md)).

=== "Windows"

    Install from [libreoffice.org](https://www.libreoffice.org/download/), or:

    ```powershell
    winget install TheDocumentFoundation.LibreOffice
    ```

=== "Ubuntu / Debian"

    ```text
    sudo apt-get install --no-install-recommends libreoffice-writer-nogui
    ```

=== "macOS"

    ```text
    brew install --cask libreoffice
    ```

## Shell completion

Tab completion for commands and options:

```text
qrbar --install-completion
```

Restart the shell after installing it.

## Upgrade and uninstall

=== "uv"

    ```text
    uv tool upgrade qrbar-cli
    uv tool uninstall qrbar-cli
    ```

=== "pipx"

    ```text
    pipx upgrade qrbar-cli
    pipx uninstall qrbar-cli
    ```

## The example files

Every `qrbar` command in this documentation runs against the files in the
[`examples/`](https://github.com/aaltatan/qrbar-cli/tree/main/examples) folder of the
repository. Download it (or clone the repository) and run the commands from inside it:

```text
git clone https://github.com/aaltatan/qrbar-cli
cd qrbar-cli/examples
```
