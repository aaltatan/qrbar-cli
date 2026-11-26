# Template functions

These functions are available in every template, Word and ZPL alike.

| Function | Word (docx) | ZPL |
|----------|-------------|-----|
| `qr(data, ...)` | Image | `^BQ` |
| `code128(data, ...)` | Image | `^BC` |
| `ean13(data, ...)` | Image | `^BE` |
| `upca(data, ...)` | Image | `^BU` |
| `datamatrix(data, ...)` | Image | `^BX` |
| `pdf417(data, ...)` | Image | `^B7` |
| `aztec(data, ...)` | Image | `^BO` |
| `barcode(name, data, ...)` | Any of the above, by name | Any of the above, by name |
| `text(value, size_mm=3)` | | `^A0` for Latin, `^GF` graphic for Arabic |

## Code functions

```text
qr(data, *, size_mm=None, width_mm=None, height_mm=None)
```

The same arguments for every code function. Sizes are keyword arguments: write `size_mm=20`, not `20`.

| Argument | Meaning |
|----------|---------|
| `data` | The value to encode: a string, or an integer (`{{ ean13(item.ean) }}` with `"ean": 400638133393` works) |
| `size_mm` | Width **and** height in mm. For square codes (QR, Data Matrix, Aztec). |
| `width_mm` | Width in mm. A square code uses it for both sides. |
| `height_mm` | Height in mm. For linear codes (Code 128, EAN-13, UPC-A) and PDF417. |

| Given | Result |
|-------|--------|
| nothing | about 0.25 mm per module; linear codes 50 modules tall |
| `size_mm=20` | 20 × 20 mm |
| `width_mm=50` | 50 mm wide; Word keeps the ratio, ZPL uses the default height |
| `width_mm=50, height_mm=12` | 50 × 12 mm |

- Sizes are the code **without** its white margin. Leave a few mm free around it.
- In ZPL a module is a whole number of dots (1 to 10), so the code is the largest size
  that fits in what you asked for. Set `{% set dpi = 300 %}` (or your printer's dpi)
  before the first code; the default is 203.
- Codes print **no human-readable text**. Add a text field under the code yourself.
- A payload a code cannot encode stops the run with an error naming the record. See
  [Code types](symbologies.md) for what each code accepts.

## `barcode`

```text
barcode(name, data, *, size_mm=None, width_mm=None, height_mm=None)
```

Pick the code type at render time, from the data or a variable:

```text
^XA^FO20,20{{ barcode(item.kind, item.code, size_mm=12) }}^XZ
```

With `{"kind": "datamatrix", "code": "SKU-7"}` this prints a Data Matrix. An unknown
name is an error.

## `text` (ZPL)

```text
text(value, *, size_mm=3)
```

A text field that is safe for any value:

- **Arabic** (and other text that needs shaping) is drawn as a right-to-left graphic
  (`^GF`), with the bundled font or `--font`.
- **Latin** text becomes a normal `^A0` field, escaped so `^` and `~` print as
  characters instead of being read as commands.
- `size_mm` is the font height in mm.

Use `text()` for every field that comes from people (names, notes, addresses). A plain
`{{ item.name }}` is refused if the value contains `^` or `~`.

## Variables

| Template | Variable | Value |
|----------|----------|-------|
| ZPL | `item` | The current record |
| ZPL | `dpi` | Set it yourself: `{% set dpi = 300 %}` (default 203) |
| docx, `paged` / `per_item` | `items` | Every copy to print, in order |
| docx, `sheet` | `pages` | Sheets → rows → cells; a cell is a record or `None` |

## Jinja

Templates are [Jinja](https://jinja.palletsprojects.com/en/stable/templates/), so
filters, conditions, loops and expressions all work:

| Want | Write |
|------|-------|
| Join text | `"https://example.com/" ~ item.sku` |
| Column with a space | `item["Unit Price"]` |
| Optional column | `item.get("note", "")` |
| Two decimals | `"%.2f"\|format(item.price)` |
| Upper case | `item.name\|upper` |
| Fallback for empty | `item.note or "-"` |
| Condition | `{% if item.fragile %}...{% endif %}` |
| Comment | `{# not printed #}` |

Word templates add the [docxtpl](https://docxtpl.readthedocs.io) tags `{%p %}`,
`{%tr %}`, `{%tc %}` and `{%r %}`; see [Word templates](../guide/word.md#the-loop-tags).
