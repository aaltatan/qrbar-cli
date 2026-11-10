{% set dpi = 203 %}
^XA
^FO40,30{{ text(item.name_ar, size_mm=5) }}
^FO40,110{{ qr(item.url, size_mm=20) }}
^FO260,140^A0N,30,30^FD{{ item.sku }}^FS
^XZ
