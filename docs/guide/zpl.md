# Zebra (ZPL) templates

ZPL is the language Zebra and most other thermal label printers speak. A qrbar ZPL
template is **one label**, `^XA ... ^XZ`, with [Jinja](https://jinja.palletsprojects.com)
tags in it. It is rendered once per row of your data, and the row is available as
`item`.

Templates can be `.zpl` or `.prn`. Both are read as ZPL, and the output keeps the
template's extension.

## A first template

This is
[`examples/label.zpl`](https://github.com/aaltatan/qrbar-cli/blob/main/examples/label.zpl):

```text
{% set dpi = 203 %}
^XA
^FO50,50{{ qr(item.url, size_mm=25) }}
^FO50,300{{ code128(item.sku, width_mm=40, height_mm=10) }}
^FO50,450{{ ean13(item.ean) }}
^FO50,600^A0N,30,30^FD{{ item.name }}^FS
^XZ
```

Line by line:

1. The printer resolution, used to turn millimetres into printer dots.
2. A QR code of the `url` column, 25 × 25 mm, its top-left corner at dot (50, 50).
3. A Code 128 of the `sku` column, 40 mm wide and 10 mm tall.
4. An EAN-13 of the `ean` column, at its default size.
5. Plain text from the `name` column, in the printer's own font `0`, 30 dots tall.

Positions (`^FO x,y`) and fonts (`^A0N,h,w`) are plain ZPL and stay yours. qrbar only
fills in the codes.

```bash
qrbar render -t label.zpl -d items.xlsx
```

```text
^XA^CI28
^FO50,50^BQN,2,8^FH_^FDMA,https://example.com/p/1^FS
^FO50,300^BY2^BCN,80,N,N,N,A^FH_^FDLMP-001^FS
^FO50,450^BY2^BEN,100,N,N^FH_^FD400638133393^FS
^FO50,600^A0N,30,30^FDDesk lamp^FS
^PQ3^XZ
^XA^CI28
...
```

## What qrbar adds and checks

- **`^CI28` after `^XA`**, so the printer reads the data as UTF-8.
- **`^PQ<qty>` before `^XZ`.** A row with `qty` 3 becomes **one block printed 3 times**,
  not three blocks. Do not put your own `^PQ` in the template.
- **Code payloads are hex-escaped** (`^FH`), so `^`, `~` and `_` inside a code are safe.
- **Printer commands in data are refused.** A plain `{{ item.name }}` containing `^` or
  `~` stops the run, so a value cannot inject commands into your label:

    ```text
    Error: Record 0: Value 'x^FDy' contains '^', which ZPL reads as a command.
    ```

    Use `{{ text(item.name) }}` for free text that may contain them.

- **Typos are errors, not empty fields.** `{{ item.nmae }}` stops the run and names the
  row, instead of printing a label with a blank where the name should be:

    ```text
    Error: Record 0: 'dict object' has no attribute 'nmae'
    ```

## Sizes and dpi

Sizes in templates are in **millimetres**. qrbar converts them to printer dots using
`dpi`, which is **203** unless you set it. Set it before the first code:

| Printer | Line |
|---------|------|
| 203 dpi (8 dots/mm), most desktop Zebras | `{% set dpi = 203 %}` (default) |
| 300 dpi (12 dots/mm) | `{% set dpi = 300 %}` |
| 600 dpi (24 dots/mm) | `{% set dpi = 600 %}` |

`^FO` positions and `^A0` font sizes are not converted: they are always dots. To
convert in your head: at 203 dpi, 1 mm ≈ 8 dots; at 300 dpi, 1 mm ≈ 12 dots.

| Call | Size |
|------|------|
| `qr(x)` | about 0.25 mm per module (one QR square) |
| `qr(x, size_mm=25)` | 25 × 25 mm, or the largest whole-dot size under it |
| `code128(x, width_mm=40)` | 40 mm wide, default height |
| `code128(x, width_mm=40, height_mm=10)` | 40 × 10 mm |
| `ean13(x)` | default module, 50 modules tall |

A printer can only draw whole dots, so a module is 1 to 10 dots wide. qrbar picks the
largest module that fits, so a code can come out a little smaller than asked, never
bigger.

## Every code type

The functions are the same in ZPL and Word. In ZPL each one becomes the printer's own
barcode command:

| Function | ZPL |
|----------|-----|
| `qr(data, ...)` | `^BQ` |
| `code128(data, ...)` | `^BC` |
| `ean13(data, ...)` | `^BE` |
| `upca(data, ...)` | `^BU` |
| `datamatrix(data, ...)` | `^BX` |
| `pdf417(data, ...)` | `^B7` |
| `aztec(data, ...)` | `^BO` |
| `barcode(name, data, ...)` | any of the above, chosen by `name` |
| `text(value, size_mm=3)` | `^A0`, or a `^GF` graphic for Arabic |

See [Template functions](../reference/template-functions.md) for every argument, and
[Code types](../reference/symbologies.md) for what each code accepts.

## Using Jinja

Everything Jinja offers works in the template. Some patterns that come up on real
labels:

```text
{# build the QR payload from a column #}
^FO20,20{{ qr("https://assets.example.com/" ~ item.tag, size_mm=18) }}

{# a column name with spaces #}
^FO30,30{{ code128(item["Item Code"], width_mm=45, height_mm=10) }}

{# format a number #}
^FO30,170^A0N,36,36^FD{{ "%.2f"|format(item["Unit Price"]) }} USD^FS

{# upper case, and a default for an empty cell #}
^FO30,120^A0N,28,28^FD{{ item.name|upper }}^FS
^FO30,160^A0N,22,22^FD{{ item.note or "-" }}^FS

{# only some labels get a line #}
{% if item.fragile %}^FO30,200^A0N,40,40^FDFRAGILE^FS{% endif %}

{# choose the code type from the data #}
^FO20,20{{ barcode(item.kind, item.code, size_mm=12) }}
```

!!! note "`{% if %}` needs the column"
    `item.fragile` must exist in every row (it can be empty). A column missing from the
    data is an error, by design. For a column that only some rows have, write
    `item.get("fragile")`.

## Designing the label

Write the fixed parts of the label in any ZPL designer (ZebraDesigner, Labelary, or by
hand), then replace the variable fields with `{{ ... }}`:

1. Design the label with sample values and export or copy the ZPL.
2. Remove any `^PQ` line. qrbar adds it from `qty`.
3. Replace each barcode command (for example `^BCN,80,Y,N,N^FDSAMPLE^FS`) with the
   matching function, keeping the `^FO` in front of it:
   `^FO50,300{{ code128(item.sku, height_mm=10) }}`.
4. Replace sample text inside `^FD...^FS` with `{{ item.<column> }}`.
5. Add `{% set dpi = ... %}` on the first line if the printer is not 203 dpi.

!!! warning "Human-readable lines"
    qrbar draws codes **without** the printed text under them. If you want the digits
    under an EAN-13 or the SKU under a Code 128, add an `^A0` text field yourself. This
    keeps the text position and font under your control.

## Next

- [Data and quantities](data.md): where `item` comes from, and how `qty` works.
- [Arabic labels](arabic.md): `text()` for Arabic and other text the printer cannot draw.
- [Output modes](output.md): one ZPL file per product with `-m per_item`.
