# Fixture — transiciones

Árbol de feature usado por `scripts/test_next_step.py` para comprobar que cada
estado de los artefactos devuelve una única transición válida.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-corte](01-corte/CONCILIACION.md) | corte | — | borrador-corte | borrador | — | — | — |
| 04 | [04-lista](04-lista/CONCILIACION.md) | implementar | — | cerrada | lista | — | TAREAS.md | — |
| 05 | [05-auditando](05-auditando/CONCILIACION.md) | auditar | — | cerrada | auditando | — | TAREAS.md | AUDIT.md |
| 06 | [06-cerrada](06-cerrada/CONCILIACION.md) | cerrada | — | cerrada | cerrada | — | TAREAS.md | AUDIT.md |
| 07 | [07-delta](07-delta/CONCILIACION.md) | cerrar delta | — | cerrada | lista | TAREAS-delta-01.md | TAREAS.md | AUDIT.md |
