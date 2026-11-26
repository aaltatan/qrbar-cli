# Commands and options

```text
qrbar [--version] [--help] <command> [options]
```

| Command | Alias | Does |
|---------|-------|------|
| [`render`](#render) | `r` | Template + data → labels (`.docx`, `.zpl`, `.prn`, `.pdf`) |
| [`code`](#code) | `c` | One barcode or QR image (`.png`, `.svg`) |
| [`symbologies`](#symbologies) | `s` | List the code types and what each one accepts |

| Global option | Meaning |
|---------------|---------|
| `-V, --version` | Print the qrbar-cli and qrbar versions |
| `--install-completion` | Install tab completion for the current shell |
| `--show-completion` | Print the completion script, to install it yourself |
| `--help` | Show help. Works after every command too: `qrbar render --help` |

## `render`

```text
qrbar render -t <template> (-d <data> | -s <schema>) [options]
```

Render a template once per copy of each record. Options are grouped as in
`qrbar render --help`.

### Template and data

| Option | Default | Meaning |
|--------|---------|---------|
| `-t, --template` | required | `.docx`, `.zpl` or `.prn`. The type comes from the extension. |
| `-d, --data` | | `.xlsx` (first row = column names) or `.json` (a list of objects) |
| `-s, --schema` | | A JSON Schema: ask for the records interactively, instead of `-d` |
| `--order` | | Column to order by, `-column` for descending. Repeatable. |
| `--filter` | | Keep matching records: a [filter](filter-rules.md) as JSON |

### Layout

| Option | Default | Meaning |
|--------|---------|---------|
| `-m, --mode` | `paged` | `paged`: one file, a label per copy. `sheet`: label sheets. `per_item`: one file per record. |
| `--collate` | `grouped` | Copy order: `grouped` (A A B B) or `interleaved` (A B A B). Not with `per_item` or ZPL. |

### Sheet (`--mode sheet`, docx only)

| Option | Default | Meaning |
|--------|---------|---------|
| `--rows` | required | Labels down a sheet |
| `--cols` | required | Labels across a sheet |
| `--skip` | `0` | Leave the first N labels empty, to reuse a partly used sheet |
| `--fill-last` | off | Pad the last sheet with empty labels |
| `--new-page-per-record` | off | Start each record's copies on a new sheet |

### Rendering

| Option | Default | Meaning |
|--------|---------|---------|
| `--qty-field` | `qty` | Column holding each record's copy count |
| `--max-copies` | `10000` | Refuse more copies than this in total. `0` = no limit. |
| `--font` | bundled IBM Plex Sans Arabic | TTF/OTF font for Arabic `text()`. ZPL only. |
| `--pdf` | off | Write PDF instead of docx. docx only, needs LibreOffice. |
| `--soffice` | found on `PATH` | LibreOffice executable for `--pdf` |

### File names

| Option | Default | Meaning |
|--------|---------|---------|
| `-f, --filename` | `<template>-labels` | Output file name without extension. `paged` and `sheet` only. |
| `-n, --name-by` | `<template>-<row>` | Column naming each file. `per_item` only. |
| `--numbered` | off | Prefix each file name with its row number: `1 - Lamp`. `per_item` only. |

### Output

| Option | Default | Meaning |
|--------|---------|---------|
| `-o, --output` | current folder | Output folder, created if missing |
| `--force` | off | Replace files that already exist (never the template) |

### Which options go together

Options that the chosen template or mode does not use are **refused**, not ignored, so
a mistake never passes silently:

| Option | Only with |
|--------|-----------|
| `--rows`, `--cols`, `--skip`, `--fill-last`, `--new-page-per-record` | `-m sheet` |
| `-m sheet` | a `.docx` template |
| `--collate interleaved` | a `.docx` template, `paged` or `sheet` |
| `--new-page-per-record` | not with `--collate interleaved` |
| `--pdf` | a `.docx` template |
| `--soffice` | `--pdf` |
| `--font` | a `.zpl` / `.prn` template |
| `-f, --filename` | `paged`, `sheet` |
| `-n, --name-by`, `--numbered` | `per_item` |
| `-d` | not with `-s` (exactly one of them) |

These checks run before the data is read, so with `--schema` they fail before the first
question.

### Examples

```bash
qrbar render -t label.zpl -d items.xlsx                 # label-labels.zpl
qrbar render -t label.docx -d items.json -f today -o out  # out/today.docx
qrbar r -t label.zpl -d items.json -m per_item -n sku -o by-sku
```

## `code`

```text
qrbar code <symbology> <payload> [options]
```

Make one barcode or QR code image.

| Argument / option | Default | Meaning |
|-------------------|---------|---------|
| `SYMBOLOGY` | required | `qr`, `code128`, `ean13`, `upca`, `datamatrix`, `pdf417`, `aztec` |
| `PAYLOAD` | required | The text to encode |
| `-o, --output` | `<symbology>.png` | Image file. `.png` or `.svg` sets the format. |
| `--format` | from `--output`, else `png` | `png` or `svg` |
| `--scale` | `4` | PNG pixels per module (one square, or the thinnest bar). PNG only. |
| `--force` | off | Replace the file if it exists |

```bash
qrbar code ean13 400638133393 -o ean13.svg
qrbar c datamatrix LMP-001 --scale 10 -o lmp-001.png
```

## `symbologies`

```text
qrbar symbologies
```

List the code types and the payload each one accepts. No options. See
[Code types](symbologies.md).
