# Fixture — fila exprés promovida a una etapa que no existe

La fila está completa y se marcó `→ 07-etapa-inexistente`, pero el índice no
tiene esa carpeta. Promover a una etapa que no existe deja el trabajo en
ninguna parte.

Debe fallar: el destino de `→ NN-slug` tiene que estar en el índice.

| # | Fecha | Cambio | Archivos | CA | Frontera | Comando | Resultado | Confirmado por |
|---|-------|--------|----------|----|----------|---------|-----------|----------------|
| E-01 | 2026-10-19 | Corregir el mensaje de error | `src/parser.py` | — | 1 archivo, 6 líneas | `python3 -m pytest tests/test_parser.py` | exit 0 · el mensaje conserva el formato previo | Ana Ruiz · 2026-10-19 → 07-etapa-inexistente |
