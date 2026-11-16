---
name: verificar-referencias
description: Verifica que cada paper citado realmente exista (URL, Crossref/PubMed) y que autores, año y título coincidan. Úsala antes de incluir cualquier referencia en un informe o PDF.
---

Objetivo: ninguna referencia entra al informe sin comprobar que existe.

## Pasos
1. Ejecuta `.venv/bin/python src/verificar_referencias.py`. Genera `bibliografia/verificacion.md` con un estado por referencia: VERIFICADA, REVISAR o NO VERIFICADA.
2. Para cada REVISAR o NO VERIFICADA:
   - Busca el título exacto con WebSearch (preferir PubMed, PMC, DOI, sitio del editor).
   - Confirma autores, año, revista y DOI contra la página de la fuente, no contra otra cita.
   - Un HTTP 403 suele ser bloqueo anti-bot, no inexistencia: confirma por búsqueda.
3. Corrige `bibliografia/referencias.md` con los datos confirmados. Si no puedes confirmar la existencia, elimina la referencia; no la completes de memoria ni la "arregles" inventando datos.
4. Comprueba también que la fuente respalde la afirmación en que se usa (abstract como mínimo). Existir no basta.
5. Registra en `verificacion.md` la fecha y qué se corrigió o eliminó.
6. Ejecuta de nuevo el script y confirma que no quedan NO VERIFICADA antes de generar el PDF (`informe-pdf-uci`).

## Reglas
- Citas secundarias deben marcarse como tales.
- Los DOI se prueban resolviendo `https://doi.org/<doi>`.
- No envíes datos personales del usuario a servicios externos al verificar.
