# Recipes

Complete, real-world jobs. Every template and data file used here is in
[`examples/`](https://github.com/aaltatan/qrbar-cli/tree/main/examples).

## Warehouse bin labels

**Job:** a label for every bin location, read by handheld scanners from a distance,
on a 300 dpi Zebra with 100 × 50 mm labels. Each bin gets two labels: one for the
front, one for the back.

[`bin.zpl`](https://github.com/aaltatan/qrbar-cli/blob/main/examples/bin.zpl):

```text
{% set dpi = 300 %}
^XA
^FO40,40{{ datamatrix(item.location, size_mm=20) }}
^FO330,50^A0N,120,120^FD{{ item.location }}^FS
^FO330,200^A0N,45,45^FDZone {{ item.zone }}, aisle {{ item.aisle }}^FS
^FO40,330{{ code128(item.location, width_mm=80, height_mm=12) }}
^XZ
```

[`bins.json`](https://github.com/aaltatan/qrbar-cli/blob/main/examples/bins.json):

```json
[
  {"location": "A-01-01", "zone": "A", "aisle": 1, "qty": 2},
  {"location": "A-01-02", "zone": "A", "aisle": 1, "qty": 2},
  {"location": "B-04-03", "zone": "B", "aisle": 4, "qty": 2}
]
```

```bash
qrbar render -t bin.zpl -d bins.json --order location
```

```text
^XA^CI28
^FO40,40^BXN,10,200^FH_^FDA-01-01^FS
^FO330,50^A0N,120,120^FDA-01-01^FS
^FO330,200^A0N,45,45^FDZone A, aisle 1^FS
^FO40,330^BY8^BCN,142,N,N,N,A^FH_^FDA-01-01^FS
^PQ2^XZ
...
```

Why it looks like this:

- **Two codes for one value.** Older laser scanners read the Code 128, and camera
  scanners read the small Data Matrix from further away.
- **`{% set dpi = 300 %}`** makes `size_mm` and `width_mm` correct on a 300 dpi
  printer. Without it, every code would come out at 203/300 of its size.
- **`qty` 2 per bin** prints front and back labels as one block with `^PQ2`.
- **`--order location`** prints the labels in the order you walk the aisles.

Only zone B was re-racked? Print just those:

```bash
qrbar render -t bin.zpl -d bins.json -f zone-b \
  --filter '{"name": "string__startswith", "args": ["location", "B-"], "kwargs": {}, "inverse": false}'
```

## IT asset tags

**Job:** a small 50 × 25 mm tag on every laptop and monitor. Scanning the QR code opens
the asset's page in the inventory system. The data is an export of the asset register.

[`asset.zpl`](https://github.com/aaltatan/qrbar-cli/blob/main/examples/asset.zpl):

```text
{% set dpi = 203 %}
^XA
^FO20,20{{ qr("https://assets.example.com/" ~ item.tag, size_mm=18) }}
^FO190,30^A0N,34,34^FD{{ item.tag }}^FS
^FO190,80^A0N,22,22^FD{{ item.model }}^FS
^FO190,115^A0N,22,22^FDProperty of Example Co.^FS
^XZ
```

[`assets.json`](https://github.com/aaltatan/qrbar-cli/blob/main/examples/assets.json)
has `tag`, `model`, `department` and `purchased`, and no `qty` column, so every asset
gets one tag.

```bash
qrbar render -t asset.zpl -d assets.json
```

- **The URL is built in the template** with Jinja's `~`: the data keeps only the tag,
  and if the inventory system moves, you change one line.
- **The tag number is printed too**, so a person can type it when the QR code is
  scratched.

New equipment arrived this year, for the Finance department only:

```bash
qrbar render -t asset.zpl -d assets.json -f finance-new --filter '{
  "operator": "all",
  "expressions": [
    {"name": "date__ge", "args": ["purchased", "2026-01-01"], "kwargs": {}, "inverse": false},
    {"name": "string__eq", "args": ["department", "Finance"], "kwargs": {}, "inverse": false}
  ]
}'
```

One ZPL file per department, to send to the printer in each office:

```bash
qrbar render -t asset.zpl -d assets.json -f it -o by-department \
  --filter '{"name": "string__eq", "args": ["department", "IT"], "kwargs": {}, "inverse": false}'
```

## Labels from an ERP export

**Job:** the ERP exports the items to label with its own column names: `Item Code`,
`Description`, `Unit Price`, `Quantity`. Print price labels without renaming anything.

[`erp.zpl`](https://github.com/aaltatan/qrbar-cli/blob/main/examples/erp.zpl):

```text
{% set dpi = 203 %}
^XA
^FO30,30{{ code128(item["Item Code"], width_mm=45, height_mm=10) }}
^FO30,130^A0N,28,28^FD{{ item["Description"] }}^FS
^FO30,170^A0N,36,36^FD{{ "%.2f"|format(item["Unit Price"]) }} USD^FS
^XZ
```

```bash
qrbar render -t erp.zpl -d erp-export.json --qty-field Quantity
```

```text
^XA^CI28
^FO30,30^BY3^BCN,80,N,N,N,A^FH_^FDLMP-001^FS
^FO30,130^A0N,28,28^FDDesk lamp^FS
^FO30,170^A0N,36,36^FD24.50 USD^FS
^PQ2^XZ
...
```

- **`item["Item Code"]`** reads a column with a space in its name.
- **`"%.2f"|format(...)`** prints `89` as `89.00` and `3.75` as `3.75`.
- **`--qty-field Quantity`** reads the copies from the ERP's own column.

The same works with the `.xlsx` the ERP saves: `-d erp-export.xlsx`.

## Price stickers on A4 sheets

**Job:** the shop has an office laser printer and A4 sheets of 24 stickers, and half a
sheet left from yesterday.

```bash
# the first 13 stickers are gone
qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3 --skip 13 -f today
```

Tomorrow, the remaining 2 stickers of that sheet first:

```bash
qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3 --skip 22 -f tomorrow
```

Print the docx at **100 %** (never "fit to page"), or add `--pdf` and print the PDF.

## One PDF per order

**Job:** attach the labels for each order to its email.

```text
qrbar render -t label.docx -d orders.xlsx -m per_item -n order_no --pdf -o outbox
```

Each order becomes `outbox/<order_no>.pdf`, with as many pages as its `qty`.

## Reprint one product

A label was damaged. Reprint only that SKU:

```bash
qrbar render -t label.zpl -d items.json -f reprint \
  --filter '{"name": "string__eq", "args": ["sku", "BLB-010"], "kwargs": {}, "inverse": false}'
```

The file still prints `^PQ5` from the data. To print one copy, use a one-record JSON
file with `"qty": 1`, or type it in with [`--schema`](guide/data.md#typing-the-data-in).

## Send ZPL straight to a Zebra printer

qrbar writes files. It does not talk to printers, so any way of sending a raw file
works:

=== "Windows (shared printer)"

    Share the printer (Printer properties → Sharing), for example as `zebra`, then:

    ```text
    qrbar render -t label.zpl -d items.xlsx -f job --force
    copy /b job.zpl \\localhost\zebra
    ```

    In PowerShell, run the `copy` through `cmd /c "copy /b job.zpl \\localhost\zebra"`.

=== "Linux / macOS (CUPS)"

    Create a raw queue once, then send the file:

    ```text
    lpadmin -p zebra -E -v usb://Zebra/ZD421 -m raw
    qrbar render -t label.zpl -d items.xlsx -f job --force
    lp -d zebra -o raw job.zpl
    ```

=== "Network printer (port 9100)"

    ```text
    qrbar render -t label.zpl -d items.xlsx -f job --force
    nc printer.local 9100 < job.zpl
    ```

    In PowerShell:

    ```powershell
    $client = [Net.Sockets.TcpClient]::new("printer.local", 9100)
    $stream = $client.GetStream()
    $bytes = [IO.File]::ReadAllBytes("job.zpl")
    $stream.Write($bytes, 0, $bytes.Length)
    $client.Close()
    ```

!!! tip "Test before a big run"
    Print with `--max-copies 1` first, or filter down to one record, and check the
    position and size on a real label. Then print the rest.

## A daily job

**Job:** every morning, print the labels the ERP exported overnight into a dated
folder, and stop the script if anything is wrong.

=== "PowerShell"

    ```powershell
    $day = Get-Date -Format yyyy-MM-dd
    qrbar render -t sheet.docx -d \\server\exports\labels.xlsx -m sheet --rows 8 --cols 3 -o "labels\$day"
    if ($LASTEXITCODE -ne 0) { throw "qrbar failed with exit code $LASTEXITCODE" }
    ```

=== "bash"

    ```text
    set -e
    qrbar render -t sheet.docx -d /mnt/exports/labels.xlsx -m sheet --rows 8 --cols 3 -o "labels/$(date +%F)"
    ```

Exit code `0` means written, `1` means bad data, and `2` means a bad command line
([Errors and exit codes](reference/errors.md)). When a run fails, nothing is written,
so a half-finished batch never reaches the printer.

## QR codes for tables, rooms or posters

```bash
qrbar code qr "https://example.com/menu" -o menu.svg
```

One per table, as SVG for the print shop:

```powershell
1..20 | ForEach-Object { qrbar code qr "https://example.com/menu?table=$_" -o "table-$_.svg" }
```

## A label typed in at the counter

No spreadsheet, just one or two labels now. Keep a schema next to the template, and
let the person at the counter answer the questions:

```text
$ qrbar render -t small.zpl -s item.schema.json -f counter --force
Item 1
? SKU: LMP-009
? Name: Wall lamp
? Copies: 2

? Add another item? (1 so far) No
Written: .../counter.zpl
```

See [Typing the data in](guide/data.md#typing-the-data-in).
