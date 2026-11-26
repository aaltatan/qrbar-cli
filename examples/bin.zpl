{% set dpi = 300 %}
^XA
^FO40,40{{ datamatrix(item.location, size_mm=20) }}
^FO330,50^A0N,120,120^FD{{ item.location }}^FS
^FO330,200^A0N,45,45^FDZone {{ item.zone }}, aisle {{ item.aisle }}^FS
^FO40,330{{ code128(item.location, width_mm=80, height_mm=12) }}
^XZ
