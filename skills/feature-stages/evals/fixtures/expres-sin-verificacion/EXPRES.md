# Fixture — fila exprés sin la prueba ni la confirmación

El árbol es coherente: la etapa `01-etapa` está `lista` y el registro
existe. Lo que falta es lo único que convierte el registro en prueba de que
se probó: la fila no declara el comando, ni el resultado, ni quién confirmó
que no hay CA nuevo ni cambio de interfaz pública.

Debe fallar: una fila sin `Comando`, `Resultado` y `Confirmado por` escritos
no es un registro, es una intención.

| # | Fecha | Cambio | Archivos | CA | Frontera | Comando | Resultado | Confirmado por |
|---|-------|--------|----------|----|----------|---------|-----------|----------------|
| E-01 | 2026-10-19 | Corregir el mensaje de error | `src/parser.py` | — | 1 archivo, 6 líneas | — | — | — |
