# Label sheets

Sticker sheets (A4 3 × 8, Letter 3 × 10, and so on) hold many labels on one page. Word
has no "repeat this cell" feature, so qrbar does the layout: it splits the copies into
**pages → rows → cells**, and the template loops over them.

Sheets work with **Word templates only** (`-m sheet`). ZPL printers feed one label at a
time, so there is nothing to lay out.

## The template

[`examples/sheet.docx`](https://github.com/aaltatan/qrbar-cli/blob/main/examples/sheet.docx)
is an A4 page with **zero margins** and a table with **one row of three 70 × 37 mm
cells**:

```text
{%p for page in pages %}
┌─────────────────────────┬─────────────────────┬─────────────────────┐
│ {%tr for row in page %}                                             │
├─────────────────────────┼─────────────────────┼─────────────────────┤
│ {% if row[0] %}         │ {% if row[1] %} ... │ {% if row[2] %} ... │
│ {{ qr(row[0].url,       │                     │                     │
│       size_mm=20) }}    │                     │                     │
│ {% endif %}             │                     │                     │
│ {% if row[0] %}         │                     │                     │
│ {{ row[0].name }}       │                     │                     │
│ {% endif %}             │                     │                     │
├─────────────────────────┼─────────────────────┼─────────────────────┤
│ {%tr endfor %}                                                      │
└─────────────────────────┴─────────────────────┴─────────────────────┘
{%p if not loop.last %} <page break> {%p endif %}
{%p endfor %}
```

What the template sees:

| Name | What it is |
|------|------------|
| `pages` | A list of sheets |
| `page` | One sheet: a list of rows |
| `row` | One row: a list of exactly `--cols` cells |
| `row[0]`, `row[1]`, ... | A cell: the copy's columns, or `None` for an empty position |

The `{% if row[0] %}` around each cell leaves empty positions blank. Rows are always
padded to the full width, so the Word table stays even.

!!! tip "Building the table in Word"
    - Set every row height to **exactly** the sticker height (Table properties → Row →
      Specify height → Exactly).
    - Set the column widths to the sticker width, and the page margins to match the
      sheet's top and left margins.
    - Keep the paragraphs between the `{%p %}` tags at 1 pt font size, so a full sheet
      does not spill a blank page.

## Render a sheet

```bash
# 9 stickers on one A4 sheet
qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3
```

`--rows` and `--cols` are the stickers **down** and **across** a sheet. Both are
required with `-m sheet`.

## Reuse a partly used sheet

You printed 13 stickers yesterday, and the sheet has 11 left. Skip the used positions:

```bash
qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3 --skip 13 -f continue
```

Positions count left to right, top to bottom, starting at 1. `--skip 13` leaves
positions 1 to 13 empty on the **first** sheet only. Later sheets start at position 1.

![qrbar render -m sheet, with --skip, --force and a rejected option](../demo/sheet.gif)

## Every product on its own sheet

```bash
qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3 --new-page-per-record --fill-last
```

- `--new-page-per-record` starts each row's copies on a new sheet: handy when each
  product goes into a different box.
- `--fill-last` pads the last sheet with empty positions, so every page has the full
  grid. Use it when the template draws borders or cut lines on empty cells too.

## Copy order on the sheet

```bash
# A, B, C, A, B, C ... instead of A, A, A, B, C ...
qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3 --collate interleaved
```

## How the options combine

For 2 copies of A and 1 of B on a 2 × 2 sheet:

| Options | Sheet 1 | Sheet 2 |
|---------|---------|---------|
| none | `A A` / `B ·` | |
| `--skip 1` | `· A` / `A B` | |
| `--collate interleaved` | `A B` / `A ·` | |
| `--new-page-per-record` | `A A` | `B ·` |

`·` is an empty position (`None` in the template).

| Option | Effect |
|--------|--------|
| `--rows`, `--cols` | The sheet grid (required with `-m sheet`) |
| `--skip N` | Leave the first N positions empty |
| `--fill-last` | Pad the last sheet with empty positions |
| `--new-page-per-record` | Each row's copies start on a new sheet |
| `--collate grouped\|interleaved` | Copy order: `A A B B` (default) or `A B A B` |

Options that do not fit together are refused before anything is read:

```text
$ qrbar render -t sheet.docx -d items.json -m sheet --rows 2 --cols 2 --skip 4
Invalid value: --skip 4 leaves no label free on a 2x2 sheet

$ qrbar render -t sheet.docx -d items.json -m sheet --rows 8 --cols 3 --new-page-per-record --collate interleaved
Invalid value: --new-page-per-record keeps a record's copies together, it cannot be interleaved

$ qrbar render -t label.zpl -d items.json -m sheet --rows 8 --cols 3
Invalid value: ZPL has no sheets: use --mode paged or per_item
```

## Common sheet sizes

| Sheet | `--rows` | `--cols` | Sticker |
|-------|----------|----------|---------|
| A4, 24 per sheet | 8 | 3 | 70 × 37 mm |
| A4, 21 per sheet | 7 | 3 | 70 × 42.4 mm |
| A4, 65 per sheet | 13 | 5 | 38.1 × 21.2 mm |
| US Letter, 30 per sheet | 10 | 3 | 2.625 × 1 in |

Check the exact sizes and margins on your sheet's packaging: brands differ by a
millimetre or two, and that matters on the last row.
