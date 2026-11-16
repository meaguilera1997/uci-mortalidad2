---
name: informe-pdf-uci
description: Genera el borrador en PDF (resumen, métodos, tabla, figuras, modelo, limitaciones, referencias) a partir de los resultados del pipeline.
---

1. Corre primero la skill `analizar-uci`.
2. Ejecuta `.venv/bin/python src/make_report.py`; produce `reports/borrador_uci.pdf`.
3. Revisa el PDF: que cada cifra coincida con `reports/metricas_por_uci.csv` y que la sección de limitaciones esté presente.
4. El documento es un BORRADOR: el docente o estudiante debe validar interpretación y referencias.
