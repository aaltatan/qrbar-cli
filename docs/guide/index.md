# User guide

This guide walks through qrbar-cli one feature at a time. Each page builds on the
previous one, but you can also jump straight to the page you need.

| Page | You will learn |
|------|----------------|
| [First labels](first-labels.md) | The three commands, and your first ZPL, Word and sheet output |
| [Zebra (ZPL) templates](zpl.md) | Write a ZPL label, sizes in mm, dpi, what qrbar adds |
| [Word (docx) templates](word.md) | One label per page in Word, loops, sizes |
| [Label sheets](sheets.md) | A4 3 × 8 sheets, `--skip`, `--fill-last`, collating |
| [Data and quantities](data.md) | Excel and JSON input, the `qty` column, typing data in |
| [Order and filter](order-filter.md) | Sort rows and print only some of them |
| [Output modes and file names](output.md) | `paged`, `sheet`, `per_item`, naming, `--force` |
| [Arabic labels](arabic.md) | Arabic text on Zebra printers, custom fonts |
| [PDF](pdf.md) | Word output as PDF through LibreOffice |
| [Single codes](codes.md) | One QR or barcode image, PNG or SVG |

## How it fits together

```text
 data (.xlsx / .json / typed in)
        │
        ▼
 --order  →  --filter                      choose and sort the rows
        │
        ▼
 template (.docx / .zpl / .prn)  +  qty    one label per copy
        │
        ▼
 --mode paged | sheet | per_item           how the labels are grouped into files
        │
        ▼
 --pdf (docx only)                         optional
        │
        ▼
 -o folder, -f / -n names, --force         where the files go
```

The template holds **everything about the look**: positions, fonts, which code type,
and its printed size. The data holds **only values**. You can reuse one data file with
many templates (a shelf label, a box label, a sticker sheet) without changing it.

## Conventions

- Commands are shown as you would type them inside the
  [`examples/`](https://github.com/aaltatan/qrbar-cli/tree/main/examples) folder.
- `$` at the start of a line marks a command when the output is shown under it.
- Paths in output are shortened to `...`.
