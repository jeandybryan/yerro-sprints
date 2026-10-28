# Fixture — cambio exprés sobre el archivo de una etapa ya cerrada

`01-etapa` y `02-etapa` están cerradas; sus tareas tocaron `src/parser.py` y
`src/otro.py`. El registro exprés de abajo toca el archivo de la etapa que
cerró.

Debe pasar sin errores: la promoción por etapa abierta solo mira el trabajo
activo, no el histórico.

| # | Fecha | Cambio | Archivos | CA | Frontera | Comando | Resultado | Confirmado por |
|---|-------|--------|----------|----|----------|---------|-----------|----------------|
| E-01 | 2026-10-19 | Corregir el mensaje de error | `src/otro.py` | — | 1 archivo, 6 líneas | `python3 -m pytest tests/test_otro.py` | exit 0 · el mensaje conserva el formato previo | Ana Ruiz · 2026-10-19 |
