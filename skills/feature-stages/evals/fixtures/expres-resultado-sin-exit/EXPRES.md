# Fixture — fila exprés con un resultado que no es un resultado

El árbol es coherente y la fila declara comando y persona. El resultado es
«ok»: un resultado sin código de salida ni propósito no distingue «pasó» de
«no se ejecutó».

Debe fallar: `Resultado` exige el exit y qué prueba.

| # | Fecha | Cambio | Archivos | CA | Frontera | Comando | Resultado | Confirmado por |
|---|-------|--------|----------|----|----------|---------|-----------|----------------|
| E-01 | 2026-10-19 | Corregir el mensaje de error | `src/parser.py` | — | 1 archivo, 6 líneas | `python3 -m pytest tests/test_parser.py` | ok | Ana Ruiz · 2026-10-19 |
