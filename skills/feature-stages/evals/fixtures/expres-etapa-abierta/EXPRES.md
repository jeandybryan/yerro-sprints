# Fixture — un cambio exprés sobre el archivo de una etapa abierta

El cambio es pequeño y su fila está completa. Lo que lo hace grande es el
contexto: `src/parser.py` es el archivo de `T1` de `01-etapa`, que está
implementando. Un cambio exprés dentro de una etapa abierta sobre el mismo
archivo es trabajo de esa etapa, no de la vía exprés.

Debe fallar: la promoción por etapa abierta no depende del número de cambios.

| # | Fecha | Cambio | Archivos | CA | Frontera | Comando | Resultado | Confirmado por |
|---|-------|--------|----------|----|----------|---------|-----------|----------------|
| E-01 | 2026-10-19 | Corregir el mensaje de error | `src/parser.py` | — | 1 archivo, 6 líneas | `python3 -m pytest tests/test_parser.py` | exit 0 · el mensaje conserva el formato previo | Ana Ruiz · 2026-10-19 |
