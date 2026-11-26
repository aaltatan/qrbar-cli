# Single codes

`qrbar code` makes **one** barcode or QR image, without a template: for a web page, a
poster, a slide, an email signature, or to test a payload.

```text
qrbar code <symbology> <payload> [-o file] [--format png|svg] [--scale N] [--force]
```

```bash
qrbar code qr "https://example.com/p/1"              # qr.png
qrbar code ean13 400638133393 -o ean.svg             # SVG, from the extension
qrbar code datamatrix LMP-001 --scale 10 -o dm.png   # 10 px per module
qrbar code qr "مصباح مكتب" -o arabic-qr.png          # UTF-8, Arabic works
qrbar c pdf417 "LMP-001 Desk lamp" --format svg      # pdf417.svg
```

![qrbar code and qrbar symbologies](../demo/code.gif)

## Format and size

| Option | Default | Meaning |
|--------|---------|---------|
| `-o, --output` | `<symbology>.png` in the current folder | The image file |
| `--format` | from `-o`, else `png` | `png` or `svg` |
| `--scale` | `4` | PNG pixels per module |
| `--force` | off | Replace the file if it exists |

- **SVG** is a vector image: it scales to any size without blurring. Use it for print
  work and web pages.
- **PNG** is pixels. `--scale` sets the pixels per **module** (one QR square, or the
  thinnest bar). A 25-module QR at `--scale 4` is 100 px plus its white margin. For
  print at 300 dpi, `--scale 10` gives about 0.85 mm per module.
- The image includes the white margin (quiet zone) scanners need.
- `--scale` with SVG, or an `-o` extension that does not match `--format`, is refused:

    ```text
    Invalid value: --scale only works for PNG; an SVG scales by itself
    ```

## What to put in a QR code

A QR code holds any text. Phones act on some formats:

| Payload | Phone does |
|---------|------------|
| `https://example.com/menu` | Opens the page |
| `WIFI:T:WPA;S:Guest;P:welcome123;;` | Joins the Wi-Fi network |
| `mailto:sales@example.com` | Starts an email |
| `tel:+963110000000` | Calls the number |
| `geo:33.5138,36.2765` | Opens the map |

```bash
qrbar code qr "https://example.com/menu" -o menu.svg
qrbar code qr "WIFI:T:WPA;S:Guest;P:welcome123;;" -o wifi.png --scale 10
```

## Many codes at once

`code` makes one image per call. For a code per row of a sheet, use `render` with a
Word template, or loop in the shell:

=== "PowerShell"

    ```powershell
    1..20 | ForEach-Object { qrbar code qr "https://example.com/table/$_" -o "table-$_.svg" }
    ```

=== "bash"

    ```text
    for n in $(seq 1 20); do qrbar code qr "https://example.com/table/$n" -o "table-$n.svg"; done
    ```

## List the code types

```bash
qrbar symbologies
```

```text
 Name        Payload
 aztec       Any text, UTF-8
 code128     ASCII only
 datamatrix  Any text, UTF-8; always square
 ean13       12 digits (check digit added) or 13 (verified)
 pdf417      Any text, UTF-8
 qr          Any text, UTF-8 (Arabic works)
 upca        11 digits, or 12 with a correct check digit
```

Each type, with an example image and when to use it, is in
[Code types](../reference/symbologies.md).
