# Fixture — contexto compactado

Un agente perdió el contexto a mitad de la etapa: `T1`–`T3` están hechas y `T4`
sigue pendiente. `next_step.py --reconcile` debe devolver `T4` y **no** reabrir
lo hecho.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-etapa](01-etapa/CONCILIACION.md) | implementar | — | cerrada | implementando | — | TAREAS.md | — |
