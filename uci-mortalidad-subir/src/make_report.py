"""Genera reports/borrador_uci.pdf a partir de reports/metricas_por_uci.csv, resumen.json y figs/.
Uso: .venv/bin/python src/make_report.py   (ejecutar antes src/pipeline.py)
"""
import json
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "reports"
t = pd.read_csv(R / "metricas_por_uci.csv", index_col=0)
s = json.loads((R / "resumen.json").read_text())
g, m = s["global"], s["modelo"]

ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10, leading=14, alignment=4)
small = ParagraphStyle("s", parent=body, fontSize=8, leading=10, textColor=colors.grey)
H1, H2 = ss["Title"], ss["Heading2"]


def P(x, st=body):
    return Paragraph(x, st)


top = t.sort_values("pct_carga_dias", ascending=False)
mayor = top.index[0]
story = [
    P("Mortalidad y carga de días en UCI según tipo de unidad", H1),
    P("BORRADOR automático – requiere revisión humana antes de su uso docente", small),
    Spacer(1, 12),
    P("1. Resumen", H2),
    P(f"Se analizaron {g['n']:,} ingresos a UCI (PhysioNet/CinC Challenge 2012, sets A y B). "
      f"La mortalidad hospitalaria fue {g['mortalidad_pct']}%, la mediana de edad {g['edad_mediana']:.0f} años "
      f"y la mediana de estadía {g['los_mediana']:.0f} días. El Índice de Swaroop global fue {g['swaroop_global']}. "
      f"La unidad <b>{mayor}</b> concentró la mayor parte de los días-cama ({top.pct_carga_dias.iloc[0]:.1f}%), "
      f"usados aquí como proxy de costo."),
    P("2. Métodos", H2),
    P("Datos abiertos de ~8.000 adultos con estadía ≥48 h (set A y B; ver Silva et al., 2012). "
      "Como el dataset no incluye diagnósticos, la <i>patología de base</i> se aproxima con el tipo de UCI "
      "(coronaria, cirugía cardíaca, médica, quirúrgica). El costo se aproxima con días de estadía (LOS). "
      "El Índice de Swaroop se calculó como defunciones de ≥50 años por 100 defunciones. "
      "El modelo es una regresión logística (edad, sexo, SAPS-I, SOFA, tipo de UCI), con partición 70/30 estratificada."),
    P("3. Resultados por tipo de UCI", H2),
]

cols = {"n": "n", "edad_mediana": "Edad med.", "pct_mujeres": "% muj.", "los_mediana": "LOS med.",
        "mortalidad_pct": "Mort. %", "swaroop": "Swaroop", "pct_carga_dias": "% días"}
data = [["UCI"] + list(cols.values())] + [[i] + [f"{r[c]:g}" for c in cols] for i, r in t.iterrows()]
tb = Table(data, repeatRows=1)
tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b6ea5")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("ALIGN", (1, 0), (-1, -1), "CENTER")]))
story += [tb, Spacer(1, 10),
          Image(str(R / "figs/carga_mortalidad.png"), width=17 * cm, height=6.4 * cm), Spacer(1, 6),
          Image(str(R / "figs/los_boxplot.png"), width=10 * cm, height=6.3 * cm),
          Image(str(R / "figs/swaroop.png"), width=10 * cm, height=6.3 * cm),
          P("4. Modelo de mortalidad", H2),
          P(f"AUC en el conjunto de prueba = {m['auc']:.3f}; Brier = {m['brier']:.3f} "
            f"(n entrenamiento {m['n_train']}, n prueba {m['n_test']}). "
            "Odds ratios por 1 DE (o vs. UCI cirugía cardíaca, categoría de referencia): "
            + ", ".join(f"{k} {v}" for k, v in m["odds_ratios_std"].items()) + "."),
          P("5. Limitaciones (a discutir en clase)", H2),
          P("• Sin diagnósticos: el tipo de UCI es un proxy grueso de patología. "
            "• LOS no equivale a costo: ignora ventilación mecánica, diálisis y recursos (Ver bibliografía). "
            "• Estadía ≥48 h excluye muertes precoces, y los datos son de un solo centro (MIMIC-II, EE.UU.). "
            "• El Índice de Swaroop fue diseñado para poblaciones, no para cohortes de UCI adulta; con mediana de edad alta "
            "es poco discriminante entre unidades. "
            "• Análisis descriptivo y asociativo; no causal."),
          P("6. Referencias", H2)]
for line in (ROOT / "bibliografia/referencias.md").read_text().splitlines():
    if line.startswith("- "):
        story.append(P(line[2:], small))

SimpleDocTemplate(str(R / "borrador_uci.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                  topMargin=2 * cm, bottomMargin=2 * cm, title="Borrador UCI").build(story)
print("OK", R / "borrador_uci.pdf")
