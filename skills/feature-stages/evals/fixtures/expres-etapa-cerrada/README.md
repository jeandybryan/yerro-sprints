# Fixture — dos etapas cerradas

`01-etapa` y `02-etapa` están cerradas: la auditoría coincide, el índice lo
marca y hay aprobación humana vigente.

Sirve para el caso negativo de la promoción por etapa abierta: un cambio exprés
sobre el archivo de una etapa que ya cerró no pertenece a trabajo en curso y no
promueve nada.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-etapa](01-etapa/CONCILIACION.md) | resultado | — | cerrada | cerrada | — | TAREAS.md | AUDIT.md |
| 02 | [02-etapa](02-etapa/CONCILIACION.md) | resultado | — | cerrada | cerrada | — | TAREAS.md | AUDIT.md |
