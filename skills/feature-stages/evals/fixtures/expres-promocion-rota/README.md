# Fixture — fila exprés promovida a una etapa que no existe

La fila está completa y se marcó `→ 07-etapa-inexistente`, pero el índice no
tiene esa carpeta. Promover a una etapa que no existe deja el trabajo en
ninguna parte.

Debe fallar: el destino de `→ NN-slug` tiene que estar en el índice.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-etapa](01-etapa/CONCILIACION.md) | resultado | — | cerrada | lista | — | TAREAS.md | — |
