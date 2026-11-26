{% set dpi = 203 %}
^XA
^FO30,30{{ code128(item["Item Code"], width_mm=45, height_mm=10) }}
^FO30,130^A0N,28,28^FD{{ item["Description"] }}^FS
^FO30,170^A0N,36,36^FD{{ "%.2f"|format(item["Unit Price"]) }} USD^FS
^XZ
