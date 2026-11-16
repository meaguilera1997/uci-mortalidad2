# Mortalidad y carga de días en UCI (actividad docente)

Pipeline reproducible sobre el dataset abierto PhysioNet/CinC Challenge 2012 que calcula métricas por tipo de UCI
(edad, sexo, días de estadía, mortalidad, Índice de Swaroop), ajusta un modelo de mortalidad y genera un borrador en PDF.

> Todo el material es un **borrador docente**: requiere revisión humana. Los días de estadía son un proxy de costo, no costo monetario.
> El dataset no incluye diagnósticos; el tipo de UCI se usa como proxy de patología.

## Paso a paso
1. Crear entorno e instalar dependencias (Python 3.9+):
   ```
   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```
2. Descargar los datos abiertos en `data/raw/` (`Outcomes-a.txt`, `Outcomes-b.txt`, `set-a.zip`, `set-b.zip`) desde
   https://physionet.org/content/challenge-2012/ y descomprimir los sets en `data/extracted/`.
3. Calcular métricas, modelo y figuras: `.venv/bin/python src/pipeline.py`
4. Verificar referencias: `.venv/bin/python src/verificar_referencias.py`
5. Generar el PDF: `.venv/bin/python src/make_report.py` → `reports/borrador_uci.pdf`

## Contenido
- `src/`: pipeline, generador de PDF y verificador de referencias.
- `.claude/skills/`: skills de Claude Code (`buscar-literatura-uci`, `analizar-uci`, `informe-pdf-uci`, `verificar-referencias`).
- `bibliografia/`: referencias y su verificación.
- `reports/`: resultados y PDF.

## Definiciones
- **Índice de Swaroop**: defunciones de ≥50 años por cada 100 defunciones.
- **Limitaciones**: sin diagnósticos, solo estadías ≥48 h, un solo centro, análisis no causal.
