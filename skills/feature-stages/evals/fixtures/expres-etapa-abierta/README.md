# Fixture — dos etapas, una implementando y otra cerrada

`02-etapa` está cerrada: la auditoría coincide, el índice lo marca y hay
aprobación humana vigente. `01-etapa` está implementando.

Sirve para dos casos de la vía exprés: un cambio sobre `src/parser.py` mientras
`01-etapa` está abierta promueve a esa etapa; un cambio sobre `src/otro.py`,
cuya etapa ya cerró, no promueve nada.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-etapa](01-etapa/CONCILIACION.md) | resultado | — | cerrada | implementando | — | TAREAS.md | — |
| 02 | [02-etapa](02-etapa/CONCILIACION.md) | resultado | — | cerrada | cerrada | — | TAREAS.md | AUDIT.md |
