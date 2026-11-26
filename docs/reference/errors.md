# Errors and exit codes

| Exit | Meaning | Written |
|------|---------|---------|
| `0` | Success | The files |
| `1` | Bad data, bad payload, a file already exists, LibreOffice missing or failed | Nothing |
| `2` | Bad command line: unknown or missing option, options that do not go together | Nothing |

Errors are one clear message on stderr, never a Python traceback. When a run fails,
**nothing is written**. Scripts can rely on the exit code (see
[A daily job](../recipes.md#a-daily-job)).

`Record 0` in a message is the **first data record**: the first object in a JSON file,
or the second row of an Excel sheet (the first row holds the column names). So
`Record 4` is Excel row 6.

## Exit code 1: data and files

| Message | Cause | Fix |
|---------|-------|-----|
| `Record 0: 'dict object' has no attribute 'nmae'` | The template uses a column the record does not have | Fix the spelling in the template, or add the column. Use `item.get("col")` for an optional column. |
| `Record 0: Value 'x^FDy' contains '^', which ZPL reads as a command.` | A plain `{{ ... }}` in ZPL got a value with `^` or `~` | Use `{{ text(item.name) }}` for that field |
| `Record 0: invalid quantity 'three', must be a whole number.` | `qty` is not a whole number ≥ 0 | Fix the cell; empty means 1, `0` skips |
| `9 copies requested, more than max_copies=5.` | The copies add up to more than `--max-copies` (default 10 000) | Check the quantities, or raise `--max-copies` (`0` = no limit) |
| `Record 1: code128: invalid payload '', must not be empty.` | A code got an empty cell | Fill the cell, or filter the row out |
| `ean13: invalid payload '4006381333932', wrong check digit, expected 1.` | The last digit of an EAN/UPC is wrong | Use the digit shown, or give 12 digits and let qrbar add it |
| `upca: invalid payload '12345', must be 11 or 12 digits.` | Wrong length for EAN-13 / UPC-A | Check the number; in Excel format the column as Text to keep leading zeros |
| `code128: invalid payload '...', only ASCII characters are allowed.` | Arabic or other non-ASCII text in a Code 128 | Use `qr` or `datamatrix` for that value |
| `No records to render (the data is empty, or --filter matched nothing).` | Nothing left after reading and filtering | Check the filter values and the sheet |
| `Nothing rendered: every record has qty 0.` | Every record was skipped | Check the `qty` column, or `--qty-field` |
| `1 file(s) exist: label-labels.zpl. Use --force to replace.` | An output file is already there | `--force`, or another `-f` / `-o` |
| `Refusing to overwrite the template label.zpl: use -f or -o.` | The output would replace the template | Pick another name or folder |
| `Two or more records give the same file name: LMP-001` | `per_item` names clash | Name by a unique column, or add `--numbered` |
| `Record 1 has no value in --name-by column 'sku'.` | An empty cell in the naming column | Fill it, or name by another column |
| `Error: ... LibreOffice ...` | `--pdf` could not find or run LibreOffice | [Install it](../install.md#optional-libreoffice-for-pdf), or give `--soffice` |

## Exit code 2: command line

These are checked **before** any data is read or asked for.

| Message | Fix |
|---------|-----|
| `Template 'items.json' must be .docx, .zpl or .prn` | `-t` is the template, `-d` the data |
| `Give exactly one data source: -d / --data or -s / --schema` | Use one of them |
| `Could not read data file 'items.xlsx': ...` | The file is damaged, or not really `.xlsx` / UTF-8 JSON |
| `"Key 'price' not found in data, Available keys: ..."` | `--order` names a column that does not exist |
| `--filter is not valid JSON: ...` | Check the quotes; see [PowerShell and quotes](../guide/order-filter.md#keep-filters-in-files) |
| `Filter failed on a data value (empty cell or wrong type?): ...` | The filter is missing `kwargs` / `inverse`, names an unknown rule, or meets a value it cannot compare |
| `--mode sheet needs --rows and --cols` | Add both |
| `--rows only works with --mode sheet` (and `--cols`, `--skip`, ...) | Add `-m sheet`, or drop the option |
| `--skip 4 leaves no label free on a 2x2 sheet` | `--skip` must be smaller than `rows × cols` |
| `ZPL has no sheets: use --mode paged or per_item` | Sheets are for Word templates |
| `ZPL prints copies with ^PQ, so --collate interleaved does not work` | Drop `--collate` for ZPL |
| `--collate does not work with --mode per_item (one file per record)` | Drop `--collate` |
| `--new-page-per-record keeps a record's copies together, it cannot be interleaved` | Use one or the other |
| `--pdf only works with .docx templates` | ZPL goes straight to the printer |
| `--soffice only works with --pdf` | Add `--pdf` |
| `--font only works with ZPL templates; a docx uses its own fonts` | Set the font in Word |
| `--filename does not work with --mode per_item (use --name-by)` | Use `-n` |
| `--name-by only works with --mode per_item` (and `--numbered`) | Add `-m per_item`, or use `-f` |
| `--output '...x.jpg' does not end in .png` | `code` writes `.png` or `.svg` |
| `--scale only works for PNG; an SVG scales by itself` | Drop `--scale` for SVG |

## Word errors

In Word `paged` and `sheet` modes all records are rendered as one document, so a data
error there may not name the record. Run the same data with `-m per_item -o check` to
find the record, then delete the `check` folder.

## Still stuck

Open an [issue](https://github.com/aaltatan/qrbar-cli/issues) with the command, the
message, and a small template and data file that show the problem.
