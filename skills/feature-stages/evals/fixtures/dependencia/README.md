# Fixture — dependencia abierta

Transición esperada: `necesita-decision`; la etapa dependiente no puede avanzar
mientras `01-corte` no esté cerrada o excepcionada por escrito.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-corte](01-corte/CONCILIACION.md) | corte | — | borrador-corte | borrador | — | — | — |
| 02 | [02-dependiente](02-dependiente/CONCILIACION.md) | implementar | 01-corte | cerrada | lista | — | TAREAS.md | — |
