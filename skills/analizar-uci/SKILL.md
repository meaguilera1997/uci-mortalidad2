---
name: analizar-uci
description: Ejecuta el pipeline de métricas UCI (edad, sexo, LOS, mortalidad, Índice de Swaroop, modelo) y revisa que los resultados sean coherentes.
---

1. Ejecuta `.venv/bin/python src/pipeline.py` desde la raíz del proyecto.
2. Verifica: n final, valores -1 tratados como faltantes, LOS > 0, mortalidad global ≈ 14%.
3. Índice de Swaroop = defunciones con edad ≥ 50 / total de defunciones × 100 (calculado solo sobre fallecidos).
4. Costo = días de estadía (proxy). Nunca lo presentes como costo monetario.
5. Para datos nuevos (MIMIC-IV/eICU con diagnósticos CIE), cambia la agrupación `UCI` por categoría diagnóstica en `load()`.
6. Informa limitaciones junto con los números.
