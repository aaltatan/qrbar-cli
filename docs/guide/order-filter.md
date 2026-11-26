# Order and filter

You rarely want to print the whole sheet. `--order` sorts the records and `--filter`
keeps only some of them. They run before rendering, in this order:

**order → filter → render**

## Order

`--order <column>` sorts ascending. Put `-` in front for descending. Repeat the option
to sort by more than one column:

```bash
# by category, then by name descending
qrbar render -t label.docx -d items.xlsx --order category --order -name
```

The order decides the order of labels on the roll or sheet, and the numbering of
`per_item` files. Printing in shelf order, for example, saves a walk around the
warehouse:

```bash
qrbar render -t bin.zpl -d bins.json --order zone --order aisle --order location -f walk-order
```

An unknown column is reported with the columns that exist:

```text
$ qrbar render -t label.zpl -d items.json --order price
Invalid value: "Key 'price' not found in data, Available keys: url, sku, ean, name, name_ar, category, qty"
```

## Filter

`--filter` takes a small JSON document. One rule looks like this:

```json
{"name": "string__eq", "args": ["category", "lighting"], "kwargs": {}, "inverse": false}
```

| Key | Meaning |
|-----|---------|
| `name` | The rule: `<type>__<test>`, see [Filter rules](../reference/filter-rules.md) |
| `args` | The column first, then the value to compare with |
| `kwargs` | Extra named arguments; `{}` for every built-in rule |
| `inverse` | `true` keeps the records that do **not** match |

All four keys are required.

```bash
# only lighting products, into lighting.docx
qrbar render -t label.docx -d items.json -f lighting \
  --filter '{"name": "string__eq", "args": ["category", "lighting"], "kwargs": {}, "inverse": false}'

# everything except cables, SKUs A to Z
qrbar render -t label.zpl -d items.json --order sku -f no-cables \
  --filter '{"name": "string__eq", "args": ["category", "cables"], "kwargs": {}, "inverse": true}'
```

### More rules

```bash
# SKUs that start with LMP
qrbar render -t label.zpl -d items.json -f lamps \
  --filter '{"name": "string__startswith", "args": ["sku", "LMP"], "kwargs": {}, "inverse": false}'

# one of several departments
qrbar render -t asset.zpl -d assets.json -f it-and-sales \
  --filter '{"name": "string__is_in", "args": ["department", ["IT", "Sales"]], "kwargs": {}, "inverse": false}'

# bought this year
qrbar render -t asset.zpl -d assets.json -f new-assets \
  --filter '{"name": "date__ge", "args": ["purchased", "2026-01-01"], "kwargs": {}, "inverse": false}'

# rows that need 3 or more labels
qrbar render -t label.zpl -d items.json -f bulk \
  --filter '{"name": "int__ge", "args": ["qty", 3], "kwargs": {}, "inverse": false}'
```

Values in `args` are converted to the rule's type, so `"3"` and `3` both work for
`int__ge`, and `"2026-01-01"` works for `date__ge`.

### Combining rules

Wrap rules in `all` (every rule must match) or `any` (one is enough). Groups can be
nested:

```bash
qrbar render -t label.zpl -d items.json -f bulbs-or-floor --filter '{
  "operator": "any",
  "expressions": [
    {"name": "string__eq", "args": ["category", "bulbs"], "kwargs": {}, "inverse": false},
    {"name": "string__icontains", "args": ["name", "floor"], "kwargs": {}, "inverse": false}
  ]
}'
```

```bash
# lighting products that need more than one label
qrbar render -t label.zpl -d items.json -f lighting-bulk --filter '{
  "operator": "all",
  "expressions": [
    {"name": "string__eq", "args": ["category", "lighting"], "kwargs": {}, "inverse": false},
    {"name": "int__gt", "args": ["qty", 1], "kwargs": {}, "inverse": false}
  ]
}'
```

### Keep filters in files

Long filters are easier to keep in a file and reuse.

=== "bash"

    ```text
    qrbar render -t label.zpl -d items.json --filter "$(cat lighting.filter.json)"
    ```

=== "PowerShell"

    ```powershell
    qrbar render -t label.zpl -d items.json --filter (Get-Content lighting.filter.json -Raw)
    ```

!!! warning "PowerShell and quotes"
    Windows PowerShell 5 removes the inner `"` from an argument written inline. Read the
    filter from a file as shown above, or put it in a variable first. PowerShell 7.3
    and newer pass inline JSON correctly.

### When nothing matches

```text
$ qrbar render -t label.zpl -d items.json --filter '{"name": "string__eq", "args": ["sku", "NOPE"], "kwargs": {}, "inverse": false}'
No records to render (the data is empty, or --filter matched nothing).
```

The run exits with code 1 and writes nothing.

## Next

[Filter rules](../reference/filter-rules.md) lists all 47 rules.
