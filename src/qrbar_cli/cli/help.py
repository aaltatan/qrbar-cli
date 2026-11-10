"""Long help texts, kept out of the command code."""

RENDER_HELP = r"""Render a .docx, .zpl or .prn template with Excel or JSON data.

Each record is one label; a [bold]qty[/] column sets its copies (missing = 1, 0 = skip).

[bold]Examples[/]

  [dim]# ZPL for a Zebra printer, one block per record printed qty times[/]
  qrbar render -t label.zpl -d items.xlsx

  [dim]# A4 sheets of 3 x 8 stickers, the first 5 already used[/]
  qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3 --skip 5

  [dim]# one PDF per record, named by the sku column[/]
  qrbar render -t label.docx -d items.json -m per_item -n sku --pdf
"""

CODE_HELP = r"""Make one barcode or QR code image (PNG or SVG).

[bold]Examples[/]

  qrbar code qr "https://example.com/item/42"
  qrbar code ean13 400638133393 -o ean.svg
  qrbar code datamatrix SKU-00042 --scale 10 -o dm.png
"""
