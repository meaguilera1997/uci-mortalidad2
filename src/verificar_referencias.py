"""Verifica que las referencias de bibliografia/referencias.md existan.

Para cada referencia (líneas que empiezan con "- "):
  1. Revisa que cada URL responda (HTTP 2xx/3xx).
  2. Busca el título en Crossref y compara similitud con la cita.
Escribe bibliografia/verificacion.md con un estado por referencia:
  VERIFICADA     = URL responde y/o Crossref encuentra un título muy similar
  REVISAR        = evidencia parcial o resultados contradictorios
  NO VERIFICADA  = sin URL válida ni coincidencia en Crossref
Uso: .venv/bin/python src/verificar_referencias.py
"""
import difflib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "bibliografia" / "referencias.md"
OUT = ROOT / "bibliografia" / "verificacion.md"
UA = {"User-Agent": "reference-checker/1.0"}  # genérico, sin datos personales


def http_status(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            return str(r.status)
    except urllib.error.HTTPError as e:
        return str(e.code)  # 403 suele ser bloqueo anti-bot, no inexistencia
    except Exception as e:
        return f"error:{type(e).__name__}"


def crossref(query: str):
    url = "https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(query)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            items = json.load(r)["message"]["items"]
    except Exception:
        return None
    best = None
    for it in items:
        title = (it.get("title") or [""])[0]
        score = difflib.SequenceMatcher(None, query.lower(), title.lower()).ratio()
        # el título completo suele estar dentro de la cita: usar contención como bonus
        if title and title.lower() in query.lower():
            score = max(score, 0.95)
        if not best or score > best[0]:
            best = (score, title, it.get("DOI"))
    return best


def main():
    refs = [l[2:].strip() for l in REF.read_text().splitlines() if l.startswith("- ")]
    rows = []
    for r in refs:
        urls = re.findall(r"https?://\S+", r)
        statuses = {u: http_status(u.rstrip(".,)")) for u in urls}
        cite = re.sub(r"https?://\S+", "", r)
        cr = crossref(cite[:250])
        url_ok = any(s.startswith(("2", "3")) for s in statuses.values())
        cr_ok = bool(cr and cr[0] >= 0.9)
        if url_ok or cr_ok:
            est = "VERIFICADA"
        elif cr and cr[0] >= 0.6 or any(s == "403" for s in statuses.values()):
            est = "REVISAR"
        else:
            est = "NO VERIFICADA"
        rows.append((est, r, statuses, cr))

    lines = ["# Verificación de referencias", "",
             "Resultado automático. 'VERIFICADA' significa que la fuente existe, no que respalde la afirmación; "
             "eso requiere lectura humana.", ""]
    for est, r, st, cr in rows:
        lines += [f"## {est}", f"- Cita: {r[:200]}"]
        lines += [f"- URL {u}: HTTP {s}" for u, s in st.items()]
        if cr:
            lines.append(f"- Crossref (similitud {cr[0]:.2f}): {cr[1]} | DOI {cr[2]}")
        lines.append("")
    OUT.write_text("\n".join(lines))
    for est, r, *_ in rows:
        print(f"[{est}] {r[:90]}")


if __name__ == "__main__":
    main()
