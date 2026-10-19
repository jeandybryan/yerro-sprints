# Fixture — delta sin auditoría que lo origine

Transición esperada: `necesita-decision`; un delta solo existe para cerrar una
brecha auditada contra el baseline.

- `01-sin-audit`: hay un delta y no hay `AUDIT.md` que lo origine.
- `02-con-coincide`: hay un delta pero la última pasada dice `coincide`.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-sin-audit](01-sin-audit/CONCILIACION.md) | cerrar delta | — | cerrada | lista | TAREAS-delta-01.md | TAREAS.md | — |
| 02 | [02-con-coincide](02-con-coincide/CONCILIACION.md) | cerrar delta | — | cerrada | lista | TAREAS-delta-01.md | TAREAS.md | AUDIT.md |
