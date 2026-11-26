# Output modes and file names

## Modes

`-m / --mode` decides how labels are grouped into files:

| Mode | Writes | Works with |
|------|--------|------------|
| `paged` (default) | One file: one label per copy. In ZPL, one block per record with `^PQ`. | docx, ZPL |
| `sheet` | One docx of label sheets ([Label sheets](sheets.md)) | docx |
| `per_item` | One file per record | docx, ZPL |

### One file per record

`per_item` is for when each record goes somewhere different: a file per product to
archive, a PDF per order to attach to an email, a ZPL block per printer.

```bash
# one file per product, named by SKU: LMP-001.zpl, LMP-002.zpl, BLB-010.zpl
qrbar render -t label.zpl -d items.json -m per_item -n sku -o zebra

# numbered: "1 - Desk lamp.docx", "2 - Floor lamp.docx", "3 - LED bulb.docx"
qrbar render -t label.docx -d items.xlsx -m per_item -n name --numbered -o word

# no --name-by: label-1.zpl, label-2.zpl, label-3.zpl (the row number)
qrbar render -t label.zpl -d items.json -m per_item -o rows
```

```text
3 files written to: .../examples/zebra
```

![qrbar render -m per_item: one file per row, named by a column](../demo/per-item.gif)

- A Word file in `per_item` holds every copy of its record: `LMP-001.docx` has 3 pages.
- A record with `qty 0` writes no file. The numbering keeps the row numbers, so with a
  skipped row you can get `1 - ...`, `2 - ...`, `4 - ...`.
- `--numbered` keeps files in data order in a file browser. Combine it with `--order`.

## File names

| Mode | Name | Default |
|------|------|---------|
| `paged`, `sheet` | `-f, --filename <name>` | `<template>-labels`, e.g. `label-labels.zpl` |
| `per_item` | `-n, --name-by <column>` | `<template>-<row>`, e.g. `label-1.zpl` |
| `per_item` | `--numbered` | adds `<row> - ` in front |

- Give names without the extension. The extension comes from the template (`.docx`,
  `.zpl`, `.prn`), or is `.pdf` with `--pdf`.
- Characters that are not allowed in file names (`/ \ : * ? " < > |`) become `_`.
  A SKU like `A/B` gives `A_B.zpl`, and a value like `../x` cannot write outside the
  output folder.
- Two records that give the same name are refused, so one never silently replaces
  the other:

    ```text
    Two or more records give the same file name: LMP-001
    ```

    Name by a unique column, or add `--numbered`.

- A record with an empty `--name-by` cell is an error naming the record.
- Naming options for the other mode are refused, not ignored:

    ```text
    $ qrbar render -t label.zpl -d items.json -m per_item -f x
    Invalid value: --filename does not work with --mode per_item (use --name-by)
    ```

## Output folder

`-o, --output` is the folder to write into: the current folder by default. It is
created if it does not exist, including parent folders:

```bash
qrbar render -t label.zpl -d items.json -o out/2026/november
```

## Overwriting

qrbar never overwrites a file unless you say so:

```text
$ qrbar render -t label.zpl -d items.xlsx
Error: 1 file(s) exist: label-labels.zpl. Use --force to replace.
```

- **Every** target file is checked before the first one is written. A `per_item` run
  that would replace one of 300 files writes none of them.
- `--force` replaces existing files.
- The **template itself is never replaced**, even with `--force`:

    ```text
    $ qrbar render -t label.zpl -d items.json -f label --force
    Refusing to overwrite the template label.zpl: use -f or -o.
    ```

## What a successful run prints

| Files written | Message |
|---------------|---------|
| One | `Written: <full path>` |
| Several | `<n> files written to: <folder>` |

Errors go to stderr, and the exit code tells scripts what happened
([Errors and exit codes](../reference/errors.md)).
