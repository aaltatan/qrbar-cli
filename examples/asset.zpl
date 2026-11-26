{% set dpi = 203 %}
^XA
^FO20,20{{ qr("https://assets.example.com/" ~ item.tag, size_mm=18) }}
^FO190,30^A0N,34,34^FD{{ item.tag }}^FS
^FO190,80^A0N,22,22^FD{{ item.model }}^FS
^FO190,115^A0N,22,22^FDProperty of Example Co.^FS
^XZ
