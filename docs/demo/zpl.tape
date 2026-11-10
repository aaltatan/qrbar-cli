Output docs/demo/zpl.gif
Set Height 760
Source docs/demo/common.tape

Type "Get-Content label.zpl" Enter Sleep 2s
Type "qrbar render -t label.zpl -d items.xlsx" Sleep 300ms Enter Sleep 4s
Type "Get-Content label-labels.zpl -TotalCount 14" Enter Sleep 5s
