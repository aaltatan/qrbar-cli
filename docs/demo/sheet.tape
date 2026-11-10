Output docs/demo/sheet.gif
Set Height 560
Source docs/demo/common.tape

Type "qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3 --skip 4" Sleep 300ms Enter Sleep 4s
Type "qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3" Sleep 300ms Enter Sleep 4s
Type "qrbar render -t sheet.docx -d items.xlsx -m sheet --rows 8 --cols 3 --force -f sheet-labels" Sleep 300ms Enter Sleep 4s
Type "qrbar render -t label.zpl -d items.xlsx -m sheet --rows 8 --cols 3" Sleep 300ms Enter Sleep 5s
