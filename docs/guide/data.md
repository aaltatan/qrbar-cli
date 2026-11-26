# Data and quantities

Every label comes from one **record**: a row of an Excel sheet, an object in a JSON
file, or a record you type in. Its columns are available in the template as
`item.<column>`, or `row[i].<column>` in [sheets](sheets.md).

## Sources

| Option | Source | Format |
|--------|--------|--------|
| `-d items.xlsx` | Excel | The **active sheet**. The first row holds the column names, and each following row is one record. |
| `-d items.json` | JSON | A list of objects: `[{"sku": "LMP-001", ...}, ...]` |
| `-s item.schema.json` | Typed in | A JSON Schema. qrbar asks for each record ([below](#typing-the-data-in)). |

Give exactly one of `-d` and `-s`.

### Excel

- The sheet that was open when the file was last saved is read. Move the sheet you
  want to the front, or save with it selected.
- **Blank rows are skipped**, so a gap in the middle of the sheet is fine.
- **Formulas give their last saved value.** Save the file in Excel after changing it;
  a file written by another program may have no saved values.
- Cells keep their type: numbers stay numbers, dates stay dates. A barcode number like
  `400638133393` works as a number, but a leading zero is lost in a number cell. Format
  EAN and UPC columns as **Text** in Excel (`012345678905`).

### JSON

```json
[
  {"url": "https://example.com/p/1", "sku": "LMP-001", "ean": "400638133393", "name": "Desk lamp", "qty": 3},
  {"url": "https://example.com/p/2", "sku": "LMP-002", "ean": "590123412345", "name": "Floor lamp", "qty": 1}
]
```

JSON files must be UTF-8. Keys can have any name, including spaces.

### Other formats

CSV and other formats are not read directly. Convert them to JSON or open and save them
in Excel. For a CSV, a one-liner works:

```text
python -c "import csv,json,sys; json.dump(list(csv.DictReader(open(sys.argv[1], encoding='utf-8'))), open(sys.argv[2], 'w', encoding='utf-8'))" items.csv items.json
```

## Column names

| Column | In the template |
|--------|-----------------|
| `sku` | `item.sku` |
| `unit price` | `item["unit price"]` |
| `Item Code` | `item["Item Code"]` |
| `2nd line` | `item["2nd line"]` |

Use the bracket form for names with spaces, dashes, or a leading digit.

A column the template uses must exist in every record. `{{ item.nmae }}` (a typo) is
an error naming the record, not an empty field. See
[Errors](../reference/errors.md).

## Quantities

The `qty` column sets how many copies of a record to print:

| `qty` | Copies |
|-------|--------|
| missing, empty | 1 |
| `3`, `"3"`, `3.0`, `" 3 "` | 3 |
| `0` | none, the record is skipped |
| `-1`, `2.5`, `"three"`, `true` | error naming the record |

In Word the copies are repeated labels. In ZPL a record is one block with `^PQ<qty>`,
and the printer makes the copies.

### Another quantity column

Your data calls it `Quantity`, `copies`, or `Labels`? Point to it:

```bash
qrbar render -t erp.zpl -d erp-export.json --qty-field Quantity
```

### The copy limit

A run is limited to **10 000 copies in total**. This stops a typo like
`qty = 100000` from sending a job that empties the label roll. A run over the limit
writes nothing:

```text
$ qrbar render -t label.zpl -d items.json --max-copies 5
Error: 9 copies requested, more than max_copies=5.
```

Raise or lift the limit for big jobs you trust:

```bash
qrbar render -t label.zpl -d items.json --max-copies 50000 -f big-run
qrbar render -t label.zpl -d items.json --max-copies 0 -f no-limit    # 0 = no limit
```

Use a lower limit as a safety net on shared machines:

```bash
qrbar render -t label.zpl -d items.json --max-copies 100 -f capped
```

## Typing the data in

No data file for a one-off label? Give a [JSON Schema](https://json-schema.org), and
qrbar asks for each record, using [schemify](https://github.com/aaltatan/schemify).
[`examples/item.schema.json`](https://github.com/aaltatan/qrbar-cli/blob/main/examples/item.schema.json):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Label",
  "type": "object",
  "properties": {
    "sku": { "title": "SKU", "type": "string" },
    "name": { "title": "Name", "type": "string" },
    "qty": { "title": "Copies", "type": "integer", "minimum": 0 }
  },
  "required": ["sku", "name", "qty"],
  "additionalProperties": false
}
```

```text
$ qrbar render -t small.zpl -s item.schema.json
Item 1
? SKU: LMP-009
? Name: Wall lamp
? Copies: 2

? Add another item? (1 so far) No
Written: .../small-labels.zpl
```

![qrbar render -s: typing two labels in, then the ZPL they make](../demo/schema.gif)

- The questions follow the schema: `title` is the question, `type` picks the input,
  and `minimum`, `enum`, `pattern` and the other rules check each answer.
- Option mistakes are reported **before** the first question, so you never type
  records for a command that then fails.
- ++ctrl+c++ cancels without writing anything.

Keep a schema next to each template that people fill in by hand: the template and its
questions then travel together.
