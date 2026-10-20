# Fixture — handoffs inválidos

Cada etapa viola una regla observable de handoff. `doctor.py` debe nombrarla.

- `01-prematuro`: `TAREAS.md` con etapa `borrador`.
- `02-sin-test`: lista principal sin `Test-first` ni `Test`.
- `03-audit-incompleta`: auditoría sin snapshot, trazabilidad, evidencia ni veredicto.
- `04-cierre-sin-coincide`: etapa `cerrada` con veredicto distinto de `coincide`.
- `05-estado-incompatible`: etapa `lista` con conciliación `abierta`.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-prematuro](01-prematuro/CONCILIACION.md) | corte | — | borrador-corte | borrador | — | TAREAS.md | — |
| 02 | [02-sin-test](02-sin-test/CONCILIACION.md) | implementar | — | cerrada | lista | — | TAREAS.md | — |
| 03 | [03-audit-incompleta](03-audit-incompleta/CONCILIACION.md) | auditar | — | cerrada | auditando | — | TAREAS.md | AUDIT.md |
| 04 | [04-cierre-sin-coincide](04-cierre-sin-coincide/CONCILIACION.md) | cerrar | — | cerrada | cerrada | — | TAREAS.md | AUDIT.md |
| 05 | [05-estado-incompatible](05-estado-incompatible/CONCILIACION.md) | implementar | — | abierta | lista | — | TAREAS.md | — |
