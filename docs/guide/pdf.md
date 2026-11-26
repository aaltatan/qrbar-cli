# PDF

`--pdf` converts the Word output to PDF with [LibreOffice](https://www.libreoffice.org),
so you get `.pdf` files instead of `.docx`. It works in every mode:

```text
$ qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3 --pdf
Converting to PDF with LibreOffice...
Written: .../sheet-labels.pdf

$ qrbar render -t label.docx -d items.json -m per_item -n sku --pdf
Converting to PDF with LibreOffice...
3 files written to: ...
```

PDF is the better choice when:

- the labels are printed on a machine without Word,
- they are emailed or attached to an order (one PDF per order with `-m per_item`),
- the exact layout must not change between printers.

## Finding LibreOffice

LibreOffice is found on `PATH` or in its default install folder. Otherwise point to it:

=== "Windows"

    ```text
    qrbar render -t label.docx -d items.json --pdf --soffice "D:/Apps/LibreOffice/program/soffice.exe"
    ```

=== "Linux"

    ```text
    qrbar render -t label.docx -d items.json --pdf --soffice /opt/libreoffice/program/soffice
    ```

=== "macOS"

    ```text
    qrbar render -t label.docx -d items.json --pdf --soffice /Applications/LibreOffice.app/Contents/MacOS/soffice
    ```

If it cannot be found or the conversion fails, qrbar stops with exit code 1 and writes
nothing. See [Installation](../install.md#optional-libreoffice-for-pdf).

## Things to know

- **Only Word templates.** ZPL is already the printer's language: `--pdf` with a
  `.zpl` template is refused.
- **Fonts.** LibreOffice uses the fonts installed on the machine. A font that is in
  Word but not installed is replaced, so install the template's fonts on the machine
  that converts, or use common fonts.
- **Speed.** Each document is converted by its own LibreOffice process. A `per_item`
  run of hundreds of records takes a while. One `sheet` or `paged` document is fast.
- **A stuck conversion** is stopped after 2 minutes.
- **`--soffice` needs `--pdf`.** On its own it is refused, so a typo does not go
  unnoticed.

## Print the PDF

=== "Windows"

    ```powershell
    Start-Process -FilePath sheet-labels.pdf -Verb Print
    ```

=== "Linux / macOS"

    ```text
    lp -d office-laser sheet-labels.pdf
    ```

Print sticker sheets at **100 % / actual size**, never "fit to page", or the stickers
drift off their positions.
