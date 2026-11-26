# Word (docx) templates

A Word template is a normal `.docx` that you design in Word (or LibreOffice Writer) and
fill with the same functions as ZPL: `{{ qr(...) }}`, `{{ code128(...) }}` and so on.
In Word every code becomes an **image sized in millimetres**, drawn at 600 dpi or more
so it prints sharp on any printer.

Use Word templates for:

- desktop label printers that print from Word (one label = one page),
- sticker sheets on an office laser or inkjet printer ([Label sheets](sheets.md)),
- anything that should end up as a PDF.

## One label per page

[`examples/label.docx`](https://github.com/aaltatan/qrbar-cli/blob/main/examples/label.docx)
is a page of **60 × 40 mm** with 3 mm margins. Its whole content is:

```text
{%p for item in items %}
{{ code128(item.sku, width_mm=50, height_mm=12) }}
{{ item.name }}
{%p if not loop.last %}
<page break>
{%p endif %}
{%p endfor %}
```

```bash
qrbar render -t label.docx -d items.json      # 9 pages: 3 + 1 + 5 copies, qty 0 skipped
```

What the template sees:

| Name | What it is |
|------|------------|
| `items` | Every copy, in order. A row with `qty` 3 appears 3 times. |
| `item` | Inside the loop: one copy, so its columns are `item.sku`, `item.name`, ... |

## The loop tags

Word templates use [docxtpl](https://docxtpl.readthedocs.io), which is Jinja with a few
extra tags. A normal `{% ... %}` tag leaves an empty paragraph behind in Word. These
variants remove the paragraph or row that holds them:

| Tag | Removes | Use it for |
|-----|---------|------------|
| `{%p ... %}` | The whole paragraph | Loops and conditions around paragraphs |
| `{%tr ... %}` | The whole table row | Repeating table rows (sheets) |
| `{%tc ... %}` | The whole table cell | Repeating columns |
| `{%r ... %}` | The run (formatted piece of text) | Conditions inside one line |

Write each `{%p %}` tag **alone in its own paragraph**.

## The page break

Put a real page break (++ctrl+enter++ in Word) between `{%p if not loop.last %}` and
`{%p endif %}`. That gives a page break after every label except the last one, so the
document does not end with a blank page.

## Page setup

Make the Word page **the size of one label**:

1. Layout → Size → More paper sizes: width and height of the label (60 × 40 mm).
2. Layout → Margins → Custom: small margins, for example 3 mm.
3. In the printer settings, choose the same label size.

## Sizes

A size is the code **itself**, without the white margin (quiet zone) that scanners
need around it. Leave a few millimetres of space around every code.

| Call | Size |
|------|------|
| `{{ qr(item.url) }}` | 0.25 mm per module (a 25-module QR is 6.25 mm) |
| `{{ qr(item.url, size_mm=20) }}` | 20 × 20 mm |
| `{{ code128(item.sku, width_mm=50) }}` | 50 mm wide, keeps its ratio |
| `{{ code128(item.sku, width_mm=50, height_mm=12) }}` | 50 × 12 mm |

Square codes (QR, Data Matrix, Aztec) use `size_mm`, or the width if you give
`width_mm`.

## Text and formatting

Plain values like `{{ item.name }}` take the formatting (font, size, bold, colour) of
the place where you typed them in Word. Values are escaped, so `&`, `<` and `>` in data
are safe. Arabic and other right-to-left text just works, because Word shapes it with
the document's own fonts.

## Copy order

By default the copies of a row stay together: `A A A B C C C C C`. With
`--collate interleaved` they are dealt like cards: `A B C A C A C C C`. This is handy
when you hand out one of each first:

```bash
qrbar render -t label.docx -d items.json --collate interleaved -f dealt
```

## Next

- [Label sheets](sheets.md): many labels on one A4 page.
- [PDF](pdf.md): the same output as PDF.
