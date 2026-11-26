# Filter rules

`--filter` takes one rule, or a group of rules, as JSON. See
[Order and filter](../guide/order-filter.md) for how to write and combine them.

```json
{"name": "<rule>", "args": ["<column>", <value>], "kwargs": {}, "inverse": false}
```

- The first item of `args` is always the **column**. The second, if the rule has one,
  is the value to compare with.
- Values are converted to the rule's type: `"3"` works for `int__gt`, and
  `"2026-01-01"` for `date__ge`.
- `"inverse": true` keeps the records that do **not** match.
- Groups: `{"operator": "all" | "any", "expressions": [ ... ]}`, nestable.
- A value that cannot be compared (an empty cell in a number rule, for example) stops
  the run with `Filter failed on a data value (empty cell or wrong type?)`. Filter the
  empty cells out first with `is_null` and `"inverse": true`.

## Any type

| Rule | Keeps records where | Example `args` |
|------|---------------------|----------------|
| `is_true` | the column is `true` | `["fragile"]` |
| `is_null` | the column is empty (`null`) | `["note"]` |

## Text

| Rule | Keeps records where | Example `args` |
|------|---------------------|----------------|
| `string__eq` | the column equals the value | `["category", "lighting"]` |
| `string__regex` | the column matches the regular expression | `["sku", "^LMP-[0-9]{3}$"]` |
| `string__contains` | the column contains the value | `["name", "lamp"]` |
| `string__icontains` | the column contains the value, ignoring case | `["name", "LAMP"]` |
| `string__is_in` | the column is one of the values in the list | `["category", ["bulbs", "cables"]]` |
| `string__iis_in` | the column is one of the values in the list, ignoring case | `["category", ["Bulbs", "CABLES"]]` |
| `string__startswith` | the column starts with the value | `["sku", "LMP"]` |
| `string__istartswith` | the column starts with the value, ignoring case | `["sku", "lmp"]` |
| `string__endswith` | the column ends with the value | `["sku", "-001"]` |
| `string__iendswith` | the column ends with the value, ignoring case | `["name", "LAMP"]` |
| `string__length_eq` | the length of the column equals the value | `["ean", 12]` |
| `string__length_gt` | the length of the column is greater than the value |  |
| `string__length_ge` | the length of the column is greater than or equal to the value |  |
| `string__length_lt` | the length of the column is less than the value |  |
| `string__length_le` | the length of the column is less than or equal to the value |  |

## Whole numbers

| Rule | Keeps records where | Example `args` |
|------|---------------------|----------------|
| `int__eq` | the column equals the value |  |
| `int__gt` | the column is greater than the value | `["qty", 1]` |
| `int__ge` | the column is greater than or equal to the value |  |
| `int__lt` | the column is less than the value |  |
| `int__le` | the column is less than or equal to the value |  |

## Decimal numbers

| Rule | Keeps records where | Example `args` |
|------|---------------------|----------------|
| `float__eq` | the column equals the value |  |
| `float__gt` | the column is greater than the value |  |
| `float__ge` | the column is greater than or equal to the value | `["weight", 2.5]` |
| `float__lt` | the column is less than the value |  |
| `float__le` | the column is less than or equal to the value |  |

## Exact decimals (money)

| Rule | Keeps records where | Example `args` |
|------|---------------------|----------------|
| `decimal__eq` | the column equals the value |  |
| `decimal__gt` | the column is greater than the value |  |
| `decimal__ge` | the column is greater than or equal to the value |  |
| `decimal__lt` | the column is less than the value | `["price", "19.99"]` |
| `decimal__le` | the column is less than or equal to the value |  |

## Dates

| Rule | Keeps records where | Example `args` |
|------|---------------------|----------------|
| `date__eq` | the column equals the value, comparing the day only |  |
| `date__gt` | the column is greater than the value, comparing the day only |  |
| `date__ge` | the column is greater than or equal to the value, comparing the day only | `["purchased", "2026-01-01"]` |
| `date__lt` | the column is less than the value, comparing the day only |  |
| `date__le` | the column is less than or equal to the value, comparing the day only |  |

## Date and time

| Rule | Keeps records where | Example `args` |
|------|---------------------|----------------|
| `datetime__eq` | the column equals the value |  |
| `datetime__gt` | the column is greater than the value |  |
| `datetime__ge` | the column is greater than or equal to the value |  |
| `datetime__lt` | the column is less than the value | `["printed_at", "2026-11-26T08:00:00"]` |
| `datetime__le` | the column is less than or equal to the value |  |

## UUIDs

| Rule | Keeps records where | Example `args` |
|------|---------------------|----------------|
| `uuid__eq` | the column equals the value | `["id", "0b7e2c1a-4b7e-4d2f-9a0e-2f4c9d1e8b11"]` |
| `uuid__gt` | the column is greater than the value |  |
| `uuid__ge` | the column is greater than or equal to the value |  |
| `uuid__lt` | the column is less than the value |  |
| `uuid__le` | the column is less than or equal to the value |  |

