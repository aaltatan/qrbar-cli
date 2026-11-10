Output docs/demo/per-item.gif
Set Height 520
Source docs/demo/common.tape

Type "qrbar render -t label.docx -d items.xlsx -m per_item -n name --numbered -o word" Sleep 300ms Enter Sleep 5s
Type "Get-ChildItem word -Name" Enter Sleep 2s
Type "qrbar render -t arabic.zpl -d items.json -m per_item -n sku -o zebra" Sleep 300ms Enter Sleep 4s
Type "Get-ChildItem zebra -Name" Enter Sleep 4s
